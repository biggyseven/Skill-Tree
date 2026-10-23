<style>
.aci-diagram{width:100%;max-width:100%;overflow-x:auto;margin:1.25rem 0;padding:.75rem;border:1px solid #1b3854;border-radius:14px;background:#07111e;color:#e5edf8;box-sizing:border-box}
.aci-diagram svg{display:block;width:100%;height:auto;min-width:720px}
.aci-diagram path.flow{animation:aciFlowDash 1.6s linear infinite}
@keyframes aciFlowDash{to{stroke-dashoffset:-26}}
@media(max-width:720px){.aci-diagram svg{min-width:720px}}
@media(prefers-reduced-motion:reduce){.aci-diagram *{animation:none!important}}
</style>

# Cisco ACI : Fabric et Politiques — Niveau Débutant

**Niveau :** Débutant  
**Domaine :** Réseaux de data center — Cisco Application Centric Infrastructure (ACI)  
**Objectif :** comprendre l’architecture physique d’une fabric ACI, le rôle de l’APIC, le modèle de politiques applicatives, les groupes d’endpoints et les contrats qui contrôlent les communications.

Cisco ACI est une solution de réseau de data center définie par logiciel. Elle combine une fabric physique construite autour de commutateurs leaf et spine avec un modèle de politiques configurées et distribuées par des contrôleurs APIC. Au lieu de configurer chaque commutateur indépendamment pour chaque besoin applicatif, l’administrateur décrit des objets et des relations : réseaux, groupes d’endpoints, contrats, domaines, chemins et services externes. La fabric applique ensuite la politique sur les équipements concernés.

ACI ne fait pas disparaître les principes réseau classiques. Les adresses IP, VLAN, passerelles, routes, ports, protocoles, DNS, les règles de filtrage et le dépannage restent importants. Ce qui change, c’est la manière dont ils sont modélisés, distribués et observés.

> **Analogie :** imagine un campus avec des routes rapides entre les bâtiments. Les commutateurs leaf sont les points d’accès où arrivent les serveurs ; les spine sont les axes rapides qui relient les leaf entre eux. L’APIC est le centre de gestion qui distribue les plans et les règles. Les contrats indiquent quels groupes d’applications peuvent communiquer, sur quels services.

---

## 1. Pourquoi Cisco ACI ?

### 1.1 Les limites d’une gestion traditionnelle

Dans un data center traditionnel, un administrateur peut avoir à configurer des VLAN, des interfaces, des trunks, des passerelles, des routes et des règles de filtrage sur de nombreux équipements. À mesure que les applications et les serveurs se multiplient, garder une configuration cohérente devient difficile.

Les problèmes fréquents sont :
- des configurations différentes d’un commutateur à l’autre ;
- des changements manuels difficiles à auditer ;
- une dépendance excessive aux adresses IP ou aux VLAN pour représenter une application ;
- des règles de sécurité répétées sur plusieurs équipements ;
- un dépannage long parce qu’il faut reconstituer le chemin et les politiques ;
- une extension du data center qui demande de nombreuses modifications.

ACI vise à fournir une fabric réseau pilotée par politiques. L’administrateur décrit l’intention, par exemple « le groupe Web peut communiquer avec le groupe Applicatif en HTTPS », au lieu de devoir traduire ce besoin en une longue séquence de commandes sur chaque équipement.

### 1.2 Que signifie ACI ?

ACI signifie **Application Centric Infrastructure**. Le modèle part des besoins des applications et décrit leurs relations réseau. La fabric est à la fois :
- une topologie physique de commutateurs ;
- un réseau overlay qui transporte le trafic ;
- un modèle d’objets et de politiques ;
- un système de gestion et de supervision.

« Centré sur l’application » ne signifie pas que le réseau devine automatiquement la sécurité métier. Les administrateurs doivent encore définir les groupes, les flux attendus, les contrats et les chemins de connexion.

### 1.3 Où ACI est-il utilisé ?

ACI est principalement utilisé dans les infrastructures de data center, par exemple :
- applications d’entreprise à plusieurs couches ;
- serveurs physiques et machines virtuelles ;
- fermes de serveurs web et d’applications ;
- bases de données ;
- environnements privés ou hybrides ;
- interconnexion avec des réseaux d’entreprise ou des réseaux externes ;
- environnements qui nécessitent une segmentation cohérente et une gestion centralisée.

Les fonctions disponibles dépendent des versions logicielles, des familles de commutateurs et de la conception déployée. Le cours explique les principes fondamentaux plutôt que de supposer un modèle matériel unique.

## 2. L’architecture physique : leaf et spine

### 2.1 Les commutateurs leaf

Les commutateurs **leaf** sont les points de connexion des endpoints à la fabric. Un endpoint peut être un serveur physique, un hyperviseur, un équipement de stockage, une appliance réseau ou une connexion vers un réseau externe. Les ports des leaf relient les équipements à la fabric et peuvent être configurés selon le domaine, le VLAN et le mode de connexion appropriés.

Dans un modèle courant :
- les serveurs se connectent aux leaf ;
- les interfaces vers les hôtes sont configurées selon les politiques d’accès ;
- les leaf hébergent des fonctions d’accès au réseau fabric et appliquent les politiques pour les endpoints ;
- certains leaf jouent le rôle de **border leaf** pour relier la fabric à des réseaux externes.

### 2.2 Les commutateurs spine

Les commutateurs **spine** forment le cœur de transport de la fabric. Ils assurent une connectivité à haut débit entre les leaf. Dans la topologie leaf-spine ACI habituelle, les leaf se connectent aux spine et les spine ne se relient pas directement entre eux au sein de la fabric standard. De même, on ne câble pas directement les leaf les uns aux autres comme chemin normal de la fabric.

Le spine n’est pas l’endroit où l’on branche normalement les serveurs. Les endpoints se raccordent aux leaf. Lorsqu’une source connectée à un leaf doit atteindre une destination connectée à un autre leaf, le trafic traverse le réseau spine-leaf.

### 2.3 Pourquoi leaf-spine ?

Avec une topologie hiérarchique traditionnelle, un chemin peut traverser plusieurs niveaux de commutation. La topologie leaf-spine permet de créer des chemins prévisibles entre les leaf et d’étendre la capacité en ajoutant des équipements compatibles et correctement dimensionnés.

Les avantages attendus :
- chemins relativement réguliers entre les racks ;
- évolutivité horizontale ;
- possibilité de répartir la capacité entre plusieurs spine ;
- redondance des chemins ;
- séparation claire entre ports d’accès et transport fabric.

L’architecture doit néanmoins être dimensionnée : nombre de ports, débit des uplinks, surabonnement, capacité des spine, diversité des liens et contraintes matérielles. Ajouter des commutateurs ne corrige pas automatiquement un plan d’adressage ou une politique mal conçus.

### 2.4 La redondance physique

Dans un design de production, on vise généralement plusieurs spine, plusieurs leaf selon les besoins, des chemins redondants et un cluster APIC résilient. La topologie exacte dépend des exigences de disponibilité, des matériels et de la version ACI. La documentation de conception Cisco doit être vérifiée avant de définir une taille minimale ou une limite supportée.

Un serveur critique peut être raccordé à deux leaf pour limiter l’impact de la perte d’un switch ou d’un lien, à condition que le serveur, le bonding, les interfaces et la politique de raccordement soient configurés correctement. La double connexion n’est pas une garantie automatique de bascule : la façon dont les ports sont présentés à l’hôte et les fonctions de redondance utilisées doivent correspondre au design.

### Schéma 1 — Fabric ACI leaf-spine avec équipements et sens du trafic

<div class="aci-diagram">
<svg viewBox="0 0 1000 530" width="100%" role="img" aria-label="Fabric Cisco ACI leaf-spine avec serveurs et flux de données directionnels" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="aci1blue" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#38bdf8"/></marker><marker id="aci1green" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#34d399"/></marker><marker id="aci1amber" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#fbbf24"/></marker></defs>
<rect x="55" y="20" width="890" height="315" rx="18" fill="#0a1727" stroke="#60a5fa" stroke-width="2" stroke-dasharray="8 5"/><text x="500" y="48" fill="#e5edf8" font-size="17" font-weight="bold" text-anchor="middle">Fabric Cisco ACI</text>
<rect x="310" y="70" width="140" height="78" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.6"/><text x="380" y="101" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Spine 1</text><text x="380" y="123" fill="#c4b5fd" font-size="12" text-anchor="middle">Transport</text>
<rect x="550" y="70" width="140" height="78" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.6"/><text x="620" y="101" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Spine 2</text><text x="620" y="123" fill="#c4b5fd" font-size="12" text-anchor="middle">Transport</text>
<rect x="115" y="210" width="150" height="82" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="190" y="241" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Leaf 101</text><text x="190" y="264" fill="#a9bdd5" font-size="12" text-anchor="middle">Accès serveur</text>
<rect x="425" y="210" width="150" height="82" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="500" y="241" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Leaf 102</text><text x="500" y="264" fill="#a9bdd5" font-size="12" text-anchor="middle">Accès serveur</text>
<rect x="735" y="210" width="150" height="82" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="810" y="241" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Leaf 103</text><text x="810" y="264" fill="#a9bdd5" font-size="12" text-anchor="middle">Border leaf</text>
<!-- Liaisons physiques leaf-spine, bidirectionnelles : traits neutres -->
<path d="M380 148 L190 210 M380 148 L500 210 M380 148 L810 210 M620 148 L190 210 M620 148 L500 210 M620 148 L810 210" fill="none" stroke="#64748b" stroke-width="2.2"/>
<rect x="105" y="385" width="190" height="75" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><rect x="125" y="402" width="27" height="29" rx="3" fill="none" stroke="#34d399" stroke-width="2"/><path d="M125 410 H152 M131 419 H146" stroke="#34d399" stroke-width="1.5"/><text x="220" y="413" fill="#e5edf8" font-size="14" font-weight="bold" text-anchor="middle">Serveur A</text><text x="220" y="435" fill="#a9bdd5" font-size="12" text-anchor="middle">Endpoint source</text>
<rect x="405" y="385" width="190" height="75" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><rect x="425" y="402" width="27" height="29" rx="3" fill="none" stroke="#34d399" stroke-width="2"/><path d="M425 410 H452 M431 419 H446" stroke="#34d399" stroke-width="1.5"/><text x="520" y="413" fill="#e5edf8" font-size="14" font-weight="bold" text-anchor="middle">Serveur B</text><text x="520" y="435" fill="#a9bdd5" font-size="12" text-anchor="middle">Endpoint destination</text>
<rect x="735" y="385" width="220" height="75" rx="10" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><text x="845" y="413" fill="#e5edf8" font-size="14" font-weight="bold" text-anchor="middle">Réseau externe</text><text x="845" y="435" fill="#fcd34d" font-size="12" text-anchor="middle">Routeur / pare-feu</text>
<!-- Flux de données illustratif : chaque segment se termine par une flèche -->
<path class="flow" d="M200 385 L190 294" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci1green)"/>
<path class="flow" d="M190 208 L380 150" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci1green)"/>
<path class="flow" d="M380 150 L500 208" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci1green)"/>
<path class="flow" d="M500 294 L510 385" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci1green)"/>
<path class="flow" d="M845 385 L810 294" fill="none" stroke="#fbbf24" stroke-width="2.8" stroke-dasharray="7 5" marker-end="url(#aci1amber)"/>
<text x="65" y="490" fill="#a9bdd5" font-size="12">Traits bleus/gris : liaisons physiques leaf-spine (bidirectionnelles).</text><text x="65" y="510" fill="#a9bdd5" font-size="12">Flèches pointillées vertes : exemple de flux Serveur A vers Serveur B à travers la fabric. Ambre : exemple de flux du réseau externe vers la fabric.</text>
</svg>
</div>

Les lignes entre leaf et spine représentent la connectivité physique de la fabric ; les flèches sont indicatives pour matérialiser les chemins. En fonctionnement réel, le trafic est acheminé selon les informations de forwarding et les politiques de la fabric, pas selon l’animation du schéma.

## 3. Le rôle de l’APIC

### 3.1 Qu’est-ce que l’APIC ?

L’**Application Policy Infrastructure Controller (APIC)** est le système central de gestion et de contrôle d’ACI. Les administrateurs l’utilisent pour définir les objets de la fabric et des tenants, configurer les politiques, surveiller l’état des équipements et consulter les événements.

L’APIC permet notamment :
- de découvrir et gérer les nœuds de la fabric ;
- de définir les tenants, VRF, bridge domains et EPG ;
- de définir les contrats et filtres ;
- de créer les politiques de ports et de raccordement ;
- d’intégrer des réseaux externes ;
- de suivre les événements, défauts et statistiques ;
- d’automatiser les modifications via les interfaces d’API prises en charge.

### 3.2 L’APIC n’est pas un routeur en série

Il faut distinguer le **plan de gestion/politique** du **plan de données**. L’APIC orchestre les configurations et les politiques de la fabric. Les commutateurs leaf et spine acheminent les paquets. En fonctionnement normal, chaque paquet ne doit pas remonter à l’APIC pour décider où aller.

Cette distinction aide à diagnostiquer les incidents. Si l’interface de gestion APIC est indisponible, les flux déjà programmés dans la fabric peuvent continuer à être transférés, tandis que les opérations de gestion, les changements de configuration et certaines fonctions de supervision peuvent être affectés. Le comportement exact lors d’une panne dépend de l’état du cluster et de la nature de l’opération. Ne considère donc pas une perte de l’APIC comme sans impact, mais ne suppose pas non plus que toute panne APIC interrompt immédiatement tout trafic.

### 3.3 Cluster APIC

Dans une conception de production, les APIC sont généralement déployés en cluster afin de fournir la résilience des fonctions de gestion et de politique. Le nombre de contrôleurs, leur placement, les exigences de quorum et les versions prises en charge doivent suivre le guide d’installation et de conception de la release ACI utilisée.

Le cluster doit être traité comme un composant essentiel :
- protéger ses accès d’administration ;
- surveiller son état et ses événements ;
- sauvegarder la configuration selon la procédure approuvée ;
- contrôler la compatibilité des mises à jour ;
- limiter les changements pendant une maintenance ;
- documenter la récupération en cas de panne.

### 3.4 Interface graphique, API et automatisation

Une interface graphique facilite l’apprentissage et la consultation des objets. Les API permettent de générer ou mettre à jour les objets de façon automatisée. Pour un débutant, l’interface APIC est un bon moyen de comprendre le modèle de données ; pour une exploitation mature, des pratiques d’automatisation, de revue et de contrôle de dérive deviennent importantes.

Ne copie pas simplement une configuration dans plusieurs environnements. Paramètre les objets, documente les dépendances et valide le résultat avec des tests réseau réels.

### Schéma 2 — Plan de gestion et plan de données

<div class="aci-diagram">
<svg viewBox="0 0 1000 455" width="100%" role="img" aria-label="APIC gérant les politiques tandis que les paquets circulent entre endpoints à travers leaf et spine" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="aci2violet" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#a78bfa"/></marker><marker id="aci2green" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#34d399"/></marker></defs>
<rect x="330" y="20" width="340" height="72" rx="13" fill="#211d3a" stroke="#a78bfa" stroke-width="1.7"/><text x="500" y="50" fill="#e5edf8" font-size="17" text-anchor="middle" font-weight="bold">Cluster APIC</text><text x="500" y="73" fill="#c4b5fd" font-size="13" text-anchor="middle">Gestion, politiques, supervision</text>
<rect x="60" y="160" width="250" height="92" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="185" y="190" fill="#e5edf8" font-size="16" font-weight="bold" text-anchor="middle">Leaf / Spine A</text><text x="185" y="214" fill="#a9bdd5" font-size="13" text-anchor="middle">Applique le forwarding</text><text x="185" y="234" fill="#a9bdd5" font-size="13" text-anchor="middle">Transporte les paquets</text>
<rect x="690" y="160" width="250" height="92" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="815" y="190" fill="#e5edf8" font-size="16" font-weight="bold" text-anchor="middle">Leaf / Spine B</text><text x="815" y="214" fill="#a9bdd5" font-size="13" text-anchor="middle">Applique le forwarding</text><text x="815" y="234" fill="#a9bdd5" font-size="13" text-anchor="middle">Transporte les paquets</text>
<path d="M390 92 L255 155" fill="none" stroke="#a78bfa" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#aci2violet)"/><path d="M610 92 L745 155" fill="none" stroke="#a78bfa" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#aci2violet)"/>
<rect x="60" y="330" width="250" height="65" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="185" y="356" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Serveur source</text><text x="185" y="378" fill="#a9bdd5" font-size="12" text-anchor="middle">Endpoint A</text>
<rect x="690" y="330" width="250" height="65" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="815" y="356" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Serveur destination</text><text x="815" y="378" fill="#a9bdd5" font-size="12" text-anchor="middle">Endpoint B</text>
<path class="flow" d="M185 330 V256" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci2green)"/><path class="flow" d="M310 205 H685" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci2green)"/><path class="flow" d="M815 256 V325" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci2green)"/>
<rect x="300" y="112" width="400" height="28" rx="7" fill="#07111e" stroke="#334155" stroke-width="1"/><text x="500" y="131" fill="#c4b5fd" font-size="12" text-anchor="middle">Plan de gestion : APIC vers les nœuds</text>
<text x="60" y="425" fill="#a9bdd5" font-size="12">Plan de données : les paquets circulent entre les endpoints via les leaf et spine.</text><text x="60" y="443" fill="#a9bdd5" font-size="12">L’APIC programme et supervise la fabric ; il n’est pas un routeur en série pour chaque paquet.</text>
</svg>
</div>

Les flèches violettes représentent la configuration et la gestion ; les flèches vertes représentent un exemple de paquet de données. Cette séparation entre plans est une idée fondamentale pour comprendre ACI.

## 4. Découverte et initialisation de la fabric

### 4.1 Préparation physique

Avant de configurer les politiques applicatives, il faut une topologie physique correcte. Cela comprend :
- choix et vérification des modèles de commutateurs compatibles avec le mode ACI ;
- câblage leaf-spine selon le design ;
- raccordement des APIC aux leaf prévus ;
- alimentation, redondance et câblage de management ;
- vérification des transceivers, débits et compatibilités ;
- inventaire des ports et documentation de la topologie.

Un mauvais câblage peut faire échouer la découverte ou créer une topologie qui ne correspond pas au diagramme. Étiquette les liens et compare la configuration physique au plan d’installation.

### 4.2 Découverte des nœuds

Le processus de mise en service comprend le bootstrap de l’APIC et la découverte/identification des switches. Les mécanismes précis dépendent de la procédure de déploiement, mais LLDP est couramment impliqué dans la détection des voisins et de la topologie. L’administrateur affecte les rôles/nœuds comme requis et vérifie la connectivité des liens.

Pendant la découverte :
1. vérifier les connexions physiques ;
2. démarrer et préparer les composants selon le guide de la version ;
3. identifier les nœuds détectés ;
4. attribuer les identifiants et noms attendus ;
5. confirmer que les leaf voient les spine prévus ;
6. corriger les défauts avant d’ajouter les politiques d’accès.

Ne saute pas directement à la configuration de contrat si l’état de la fabric n’est pas sain.

### 4.3 Contrôles après initialisation

Vérifie dans l’APIC :
- les nœuds attendus sont présents et opérationnels ;
- les liens fabric sont actifs ;
- les défauts critiques ont été compris ;
- le cluster APIC est sain ;
- les versions et compatibilités sont celles du plan ;
- l’heure, le DNS, la gestion et les comptes d’administration sont correctement établis ;
- la sauvegarde et le processus de restauration sont documentés.

Une icône verte ne remplace pas un test de trafic. L’état d’un nœud et le résultat d’une application sont deux signaux différents.

## 5. Le modèle logique : les objets ACI

Le modèle ACI emploie une hiérarchie d’objets. Il faut connaître les relations entre ces objets avant de construire la première application.

### 5.1 Tenant

Un **tenant** est un conteneur logique de politiques et de ressources. Il peut représenter une application d’entreprise, une équipe, un client ou une unité d’administration. Il aide à organiser et isoler les objets, mais **un tenant n’est pas à lui seul un réseau privé** et ne garantit pas que tous les flux sont isolés sans autres politiques.

ACI possède des tenants intégrés et permet de créer des tenants définis par l’administrateur. Le tenant `common` peut servir à partager certains objets selon le design ; il ne faut pas y mettre des objets au hasard sous prétexte qu’ils sont communs.

### 5.2 VRF (context)

Un **VRF**, également appelé contexte dans ACI, fournit un contexte de routage de couche 3. Il contient l’espace de routage dans lequel des bridge domains et leurs sous-réseaux peuvent être associés. La séparation par VRF peut permettre des espaces d’adresses qui se recouvrent, si la conception et les connexions externes le permettent ; l’accès entre VRF exige des mécanismes et politiques spécifiques.

Une VRF ne correspond pas forcément à une seule application. Plusieurs bridge domains peuvent partager le même contexte de routage. La décision dépend de l’isolation nécessaire et des besoins de connectivité.

### 5.3 Bridge Domain (BD)

Un **bridge domain** définit un domaine de couche 2 dans le modèle ACI, avec des paramètres de forwarding et, selon le type de BD, des sous-réseaux associés qui peuvent fournir le rôle de passerelle par défaut. Le BD est associé à une VRF. Il participe à la définition de la segmentation de couche 2 et des comportements de forwarding.

Ne confonds pas :
- **BD** : domaine de couche 2 et paramètres associés ;
- **VRF** : contexte de routage de couche 3 ;
- **VLAN** : identifiant de couche 2 utilisé sur certains liens et dans le raccordement des endpoints ;
- **EPG** : regroupement logique des endpoints pour appliquer la politique.

Ils sont liés mais ne représentent pas le même objet.

### 5.4 Application Profile

Un **Application Profile** est un conteneur logique qui regroupe des EPG liés à une application. Il organise la représentation de l’application — par exemple les couches Web, App et DB — mais n’est pas à lui seul un pare-feu ou un réseau.

### 5.5 Endpoint Group (EPG)

Un **EPG** regroupe les endpoints qui partagent une même politique. Les endpoints sont généralement des serveurs, VMs ou autres workloads raccordés à la fabric et classés selon des critères configurés. Un EPG peut être associé à un bridge domain. Les façons de placer les endpoints dans un EPG dépendent de leur type et des politiques d’accès : bindings statiques, domaines physiques, intégration de virtualisation ou mécanismes supportés.

Exemple de modèle à trois groupes :
- `EPG-Web` : serveurs frontaux ;
- `EPG-App` : serveurs applicatifs ;
- `EPG-DB` : bases de données.

Cette séparation rend la politique plus proche des relations applicatives. Elle ne signifie pas que chaque EPG possède obligatoirement un sous-réseau distinct ; les relations BD/EPG et les choix d’architecture déterminent la conception.

### 5.6 Contrat, sujet et filtre

Un **contrat** définit une relation de communication entre groupes : un EPG qui fournit un service expose un contrat, et un EPG qui en a besoin le consomme. Le contrat contient un ou plusieurs sujets ; les sujets référencent des filtres qui précisent des protocoles et ports, par exemple TCP/443.

Un **filtre** décrit les critères de trafic correspondant à une règle. Un **sujet** organise un ensemble de filtres et de comportements liés au contrat. La façon dont le contrat est consommé/fourni et sa portée doivent être comprises avant de l’associer aux EPG.

En règle générale, ACI utilise le contrat pour définir les communications autorisées entre EPG distincts ; le comportement par défaut entre EPG est généralement restrictif. Le comportement intra-EPG peut être différent et dépend aussi des options de politique comme l’isolation. Ne suppose pas qu’un contrat existe simplement parce que deux endpoints appartiennent au même tenant.

### Schéma 3 — Hiérarchie logique des objets ACI

<div class="aci-diagram">
<svg viewBox="0 0 1000 555" width="100%" role="img" aria-label="Objets ACI avec Tenant contenant VRF, bridge domain, application profile, EPG et relations de contrat" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="aci3blue" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#38bdf8"/></marker><marker id="aci3green" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#34d399"/></marker><marker id="aci3amber" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#fbbf24"/></marker></defs>
<rect x="20" y="18" width="960" height="515" rx="18" fill="#0a1727" stroke="#a78bfa" stroke-width="1.8"/><text x="50" y="50" fill="#e5edf8" font-size="18" font-weight="bold">Tenant</text><text x="145" y="50" fill="#c4b5fd" font-size="12">Conteneur logique des objets et politiques</text>
<rect x="65" y="90" width="310" height="70" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="220" y="119" fill="#e5edf8" font-size="16" font-weight="bold" text-anchor="middle">VRF / Context</text><text x="220" y="141" fill="#a9bdd5" font-size="12" text-anchor="middle">Contexte de routage L3</text>
<path d="M220 160 V197" fill="none" stroke="#38bdf8" stroke-width="2.7" marker-end="url(#aci3blue)"/><text x="238" y="184" fill="#a9bdd5" font-size="11">BD associé</text>
<rect x="65" y="202" width="310" height="100" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="220" y="232" fill="#e5edf8" font-size="16" font-weight="bold" text-anchor="middle">Bridge Domain (BD)</text><text x="220" y="255" fill="#a9bdd5" font-size="12" text-anchor="middle">Domaine de couche 2</text><text x="220" y="276" fill="#a9bdd5" font-size="12" text-anchor="middle">Subnet / passerelle si configuré</text>
<rect x="475" y="90" width="455" height="65" rx="11" fill="#0d2a27" stroke="#34d399" stroke-width="1.6"/><text x="702" y="118" fill="#e5edf8" font-size="16" font-weight="bold" text-anchor="middle">Application Profile</text><text x="702" y="139" fill="#a9bdd5" font-size="12" text-anchor="middle">Organise les groupes liés à l’application</text>
<path d="M702 155 V190" fill="none" stroke="#34d399" stroke-width="2.7" marker-end="url(#aci3green)"/>
<rect x="450" y="195" width="500" height="120" rx="12" fill="#071f1d" stroke="#34d399" stroke-width="1.4"/><text x="700" y="218" fill="#6ee7b7" font-size="13" font-weight="bold" text-anchor="middle">EPG : groupes d’endpoints</text>
<rect x="470" y="235" width="140" height="58" rx="8" fill="#10243a" stroke="#38bdf8" stroke-width="1.3"/><text x="540" y="260" fill="#e5edf8" font-size="14" font-weight="bold" text-anchor="middle">EPG-Web</text><text x="540" y="279" fill="#a9bdd5" font-size="11" text-anchor="middle">Frontaux</text>
<rect x="630" y="235" width="140" height="58" rx="8" fill="#10243a" stroke="#38bdf8" stroke-width="1.3"/><text x="700" y="260" fill="#e5edf8" font-size="14" font-weight="bold" text-anchor="middle">EPG-App</text><text x="700" y="279" fill="#a9bdd5" font-size="11" text-anchor="middle">Logique métier</text>
<rect x="790" y="235" width="140" height="58" rx="8" fill="#10243a" stroke="#38bdf8" stroke-width="1.3"/><text x="860" y="260" fill="#e5edf8" font-size="14" font-weight="bold" text-anchor="middle">EPG-DB</text><text x="860" y="279" fill="#a9bdd5" font-size="11" text-anchor="middle">Données</text>
<path d="M700 315 V350" fill="none" stroke="#fbbf24" stroke-width="2.7" stroke-dasharray="7 5" marker-end="url(#aci3amber)"/>
<rect x="475" y="356" width="455" height="78" rx="11" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.6"/><text x="702" y="384" fill="#e5edf8" font-size="16" font-weight="bold" text-anchor="middle">Contrat / Sujet / Filtre</text><text x="702" y="407" fill="#fcd34d" font-size="12" text-anchor="middle">Relation de politique entre EPG et ports autorisés</text>
<text x="65" y="350" fill="#a9bdd5" font-size="13" font-weight="bold">À distinguer</text><text x="65" y="375" fill="#a9bdd5" font-size="12">VRF = routage L3</text><text x="65" y="396" fill="#a9bdd5" font-size="12">BD = domaine L2</text><text x="65" y="417" fill="#a9bdd5" font-size="12">EPG = groupe de politique</text><text x="65" y="438" fill="#a9bdd5" font-size="12">Contrat = relation d’accès</text>
<path class="flow" d="M540 293 V328 H650 V350" fill="none" stroke="#fbbf24" stroke-width="2.4" stroke-dasharray="7 5" marker-end="url(#aci3amber)"/><path class="flow" d="M860 293 V328 H755 V350" fill="none" stroke="#fbbf24" stroke-width="2.4" stroke-dasharray="7 5" marker-end="url(#aci3amber)"/>
<text x="475" y="468" fill="#a9bdd5" font-size="12">EPG : associés à un BD et regroupés dans un Application Profile.</text><text x="475" y="488" fill="#a9bdd5" font-size="12">Les contrats relient les EPG ; ils ne remplacent pas les routes.</text>
</svg>
</div>

Le dessin résume des relations courantes, mais ne représente pas tous les objets et toutes les associations possibles. Un contrat est une relation de politique entre EPG, pas simplement un enfant qui transformerait un EPG en sous-réseau.

## 6. Comment ACI transporte les paquets

### 6.1 Underlay et overlay

Une fabric ACI utilise une infrastructure physique de transport appelée **underlay** et un réseau logique d’encapsulation appelé **overlay**. VXLAN est au cœur du modèle overlay ACI : le trafic est encapsulé pour traverser la fabric, permettant de transporter les réseaux/logiques des tenants sur le réseau physique leaf-spine.

Pour comprendre le principe :
- l’underlay fournit une connectivité IP entre les nœuds de la fabric ;
- l’overlay représente des segments et politiques logiques ;
- les leaf raccordent les endpoints et réalisent les fonctions de forwarding nécessaires ;
- l’encapsulation permet de transporter le trafic d’un leaf source vers un leaf destination ;
- les politiques ACI déterminent si les endpoints sont autorisés à communiquer.

L’overlay ne remplace pas le routage IP de base : l’infrastructure doit être saine pour que les paquets encapsulés puissent traverser la fabric.

### 6.2 Endpoint et informations de forwarding

ACI apprend et maintient des informations sur les endpoints, notamment où se trouvent des adresses MAC/IP dans la fabric, selon le type d’endpoint et les mécanismes de découverte. Les leaf utilisent ces informations pour transmettre le trafic vers le bon port ou le bon leaf distant. Les détails internes de distribution et d’identification varient avec la version et la configuration ; le point essentiel pour un débutant est que le fabric sait associer un endpoint à son point de raccordement.

Lorsqu’un serveur migre ou change de port, ces informations doivent rester cohérentes. Les symptômes d’une information endpoint incorrecte peuvent ressembler à un problème de VLAN, de câblage ou de routage.

### 6.3 Flux entre deux serveurs sur le même leaf ou différents leaf

Si deux endpoints sont sur le même leaf et dans des conditions de politique compatibles, le trafic peut être traité localement sur ce leaf. Si la destination se trouve derrière un autre leaf, la fabric transfère le trafic à travers un ou plusieurs liens leaf-spine. Le chemin physique dépend de la topologie et des mécanismes de forwarding.

Il n’est pas nécessaire de connaître tous les détails de VXLAN pour commencer à travailler avec les politiques, mais il faut savoir où s’effectuent les raccordements et quels éléments peuvent affecter le chemin.

### 6.4 L2 et L3 dans ACI

Le bridge domain porte la dimension de couche 2 et des paramètres associés ; la VRF fournit le contexte de couche 3. Une passerelle de sous-réseau peut être configurée dans le BD. Le trafic vers des destinations d’un autre sous-réseau peut nécessiter une décision de routage dans la VRF, tout en restant soumis aux politiques applicables.

Ne confonds pas la présence d’une route et l’autorisation d’une communication. Dans ACI, le modèle de politique et le forwarding sont étroitement liés, mais restent deux dimensions distinctes de l’analyse.

### Schéma 4 — Flux entre deux endpoints sur des leaf différents

<div class="aci-diagram">
<svg viewBox="0 0 1000 410" width="100%" role="img" aria-label="Flux VXLAN d’un serveur à l’autre à travers leaf source, spine et leaf destination" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="aci4green" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#34d399"/></marker></defs>
<rect x="20" y="75" width="960" height="220" rx="16" fill="#0a1727" stroke="#60a5fa" stroke-width="1.8" stroke-dasharray="8 5"/><text x="500" y="101" fill="#e5edf8" font-size="16" font-weight="bold" text-anchor="middle">Fabric Cisco ACI</text>
<rect x="30" y="140" width="155" height="95" rx="11" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><rect x="48" y="158" width="25" height="30" rx="3" fill="none" stroke="#34d399" stroke-width="1.8"/><path d="M48 167 H73 M54 177 H67" stroke="#34d399" stroke-width="1.4"/><text x="125" y="174" fill="#e5edf8" font-size="14" font-weight="bold" text-anchor="middle">Serveur A</text><text x="108" y="211" fill="#a9bdd5" font-size="12" text-anchor="middle">Endpoint source</text>
<rect x="225" y="140" width="145" height="95" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="297" y="174" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Leaf 101</text><text x="297" y="197" fill="#a9bdd5" font-size="12" text-anchor="middle">Encapsule</text><text x="297" y="216" fill="#a9bdd5" font-size="12" text-anchor="middle">VXLAN</text>
<rect x="420" y="140" width="145" height="95" rx="11" fill="#211d3a" stroke="#a78bfa" stroke-width="1.5"/><text x="492" y="174" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Spine</text><text x="492" y="197" fill="#c4b5fd" font-size="12" text-anchor="middle">Transport</text><text x="492" y="216" fill="#c4b5fd" font-size="12" text-anchor="middle">underlay IP</text>
<rect x="615" y="140" width="145" height="95" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="687" y="174" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Leaf 102</text><text x="687" y="197" fill="#a9bdd5" font-size="12" text-anchor="middle">Décapsule</text><text x="687" y="216" fill="#a9bdd5" font-size="12" text-anchor="middle">VXLAN</text>
<rect x="805" y="140" width="165" height="95" rx="11" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><rect x="824" y="158" width="25" height="30" rx="3" fill="none" stroke="#34d399" stroke-width="1.8"/><path d="M824 167 H849 M830 177 H843" stroke="#34d399" stroke-width="1.4"/><text x="905" y="174" fill="#e5edf8" font-size="14" font-weight="bold" text-anchor="middle">Serveur B</text><text x="888" y="211" fill="#a9bdd5" font-size="12" text-anchor="middle">Endpoint destination</text>
<path class="flow" d="M185 188 H220" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci4green)"/><path class="flow" d="M370 188 H415" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci4green)"/><path class="flow" d="M565 188 H610" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci4green)"/><path class="flow" d="M760 188 H800" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci4green)"/>
<rect x="120" y="320" width="760" height="55" rx="10" fill="#111d30" stroke="#334155" stroke-width="1.2"/><text x="500" y="343" fill="#e5edf8" font-size="14" font-weight="bold" text-anchor="middle">VXLAN : overlay logique transporté sur l’underlay IP</text><text x="500" y="362" fill="#a9bdd5" font-size="12" text-anchor="middle">La politique ACI s’applique aux endpoints ; la fabric transporte les paquets selon les informations de forwarding.</text>
<text x="30" y="398" fill="#a9bdd5" font-size="12">Flux illustré : source vers destination ; les réponses suivent le chemin retour approprié.</text>
</svg>
</div>

## 7. Les politiques d’accès aux ports et aux endpoints

### 7.1 Domaines et raccordement

Un endpoint physique ou virtuel doit être associé à la fabric via des politiques d’accès. Selon le cas, la configuration peut inclure :
- un **physical domain** pour des équipements connectés physiquement ;
- un domaine de virtualisation (VMM) pour des environnements intégrés ;
- un VLAN pool et l’encapsulation correspondante ;
- une interface ou un bundle de ports ;
- un policy group, un profil de ports et un profil de leaf ;
- une association statique de chemin vers l’EPG.

La terminologie exacte dépend de la version et du type de raccordement. Le principe : ACI doit savoir quels ports existent, quelles fonctions leur sont associées, comment ils transportent le trafic et à quel EPG l’endpoint appartient.

### 7.2 VLAN et EPG

Le VLAN peut être utilisé sur le port d’accès comme identifiant d’encapsulation pour un endpoint ou un ensemble d’endpoints. Dans ACI, il ne faut pas considérer le VLAN comme l’unique définition de la politique : l’EPG, le BD, la VRF et les contrats forment le modèle logique de communication.

Le même numéro de VLAN peut être réutilisé dans des contextes où l’architecture le permet, mais toute réutilisation doit être comprise dans le modèle d’accès et de domaine. Évite de copier le même VLAN ID partout sans inventaire de l’encapsulation et des trunks.

### 7.3 Raccordement statique et domaines VMM

Dans certains environnements, on associe manuellement un chemin physique et une encapsulation à un EPG. Dans un environnement virtualisé intégré, les mécanismes VMM peuvent aider à classifier les workloads et à associer leurs réseaux logiques. Les deux chemins ne sont pas identiques ; il faut suivre le guide correspondant au type de serveur/hyperviseur.

### 7.4 Port access, trunk et LACP

Les modes de port, les profils de ports, les port-channels et les mécanismes d’agrégation doivent correspondre au câblage et au comportement de l’hôte. Si un serveur utilise un bond/LACP, le côté ACI doit être configuré avec les objets attendus pour le mode choisi. Un mauvais mélange de modes peut produire des symptômes intermittents : une interface fonctionne, l’autre non, les MAC se déplacent ou la redondance n’agit pas comme prévu.

Avant la mise en production, teste :
- perte d’un lien ;
- perte d’un leaf si le serveur est dual-homed ;
- apprentissage MAC/IP ;
- VLAN/encapsulation attendus ;
- débit et erreurs d’interface ;
- appartenance de l’endpoint au bon EPG.

## 8. Créer une première politique d’application

Nous allons prendre un exemple pédagogique en trois couches :

- **EPG-Web** : serveurs Web recevant des clients ;
- **EPG-App** : serveurs applicatifs ;
- **EPG-DB** : base de données.

Le but est d’autoriser Web → App sur le port applicatif défini et App → DB sur le port DB prévu, tout en évitant un accès direct non prévu de Web vers DB. Les numéros de ports ci-dessous sont illustratifs ; ils doivent correspondre à l’application réellement installée.

### 8.1 Étape 1 : créer le tenant

Choisis ou crée un tenant qui correspond au domaine de gestion souhaité. Donne un nom clair et identifie les propriétaires qui seront responsables de ses politiques. Ne confonds pas le nom d’un tenant avec une frontière complète de routage.

### 8.2 Étape 2 : créer une VRF

Dans le tenant, crée un contexte de routage si le design en a besoin. Détermine quelles applications et quels bridge domains doivent partager ce contexte. Vérifie l’isolation attendue et les chemins vers les réseaux externes.

### 8.3 Étape 3 : créer un bridge domain

Associe le BD à la VRF. Configure le subnet ou la passerelle de couche 3 si nécessaire. Vérifie les paramètres de flooding, d’apprentissage et de forwarding adaptés au scénario. Tous les paramètres du BD ne sont pas nécessaires pour toutes les architectures ; utilise les valeurs définies dans le design et la documentation de la release.

### 8.4 Étape 4 : créer l’Application Profile et les EPG

Crée un profil applicatif et les EPG correspondants aux groupes de workloads. Associe les EPG au BD choisi. Configure les bindings des endpoints selon leur raccordement : statique, physique, virtualisé ou autre mécanisme pris en charge.

À cette étape, les objets logiques existent, mais le trafic réel dépend encore :
- de la connexion physique ;
- du VLAN/encapsulation et du domaine ;
- de l’interface et des profils d’accès ;
- de l’adresse IP et de la passerelle ;
- des contrats ou règles qui autorisent les flux.

### 8.5 Étape 5 : définir un filtre

Crée un filtre correspondant au service nécessaire, par exemple TCP destination port 8443 pour un service applicatif de test. Un filtre doit être aussi précis que possible. Évite les règles « any-any » lorsque l’application ne l’exige pas.

### 8.6 Étape 6 : créer un contrat avec sujet

Crée un contrat et un sujet qui utilisent le filtre. Donne au contrat un nom qui exprime son objectif, par exemple `Web-vers-App-HTTPS` ou `App-vers-DB-Service`. Des noms précis facilitent la revue, la supervision et le dépannage.

### 8.7 Étape 7 : provider et consumer

L’EPG qui met un service à disposition fournit le contrat (provider). L’EPG qui a besoin de ce service consomme le contrat (consumer). Dans cet exemple, EPG-App fournit le service applicatif, et EPG-Web consomme le contrat correspondant.

Cette relation de contrat indique quels EPG sont autorisés à échanger selon la définition du contrat. Elle ne signifie pas que tout le trafic physique ou toutes les adresses réseau sont modifiés pour prendre un sens unique. Un protocole de transport a besoin de réponses pour fonctionner ; la politique effective, le suivi d’état et les règles du contrat doivent être vérifiés selon le design.

### 8.8 Étape 8 : tester le fonctionnement et le refus

Teste au minimum :
- Web → App sur le port et le protocole autorisés ;
- App → DB sur le port autorisé ;
- Web → DB, qui doit échouer si aucun contrat ne l’autorise ;
- un autre port non autorisé entre les EPG ;
- résolution DNS et connectivité à la passerelle ;
- accès depuis un endpoint du même EPG si l’isolation intra-EPG est configurée.

Un test réussi ne suffit pas à prouver qu’un flux interdit est bien bloqué. Les tests positifs et négatifs font partie de la validation de politique.

### Schéma 5 — Application Web/App/DB avec contrats et flèches

<div class="aci-diagram">
<svg viewBox="0 0 1000 460" width="100%" role="img" aria-label="EPG Web, App et DB avec deux contrats autorisant des flux spécifiques et une communication Web vers DB refusée" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="aci5green" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#34d399"/></marker><marker id="aci5red" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#fb7185"/></marker></defs>
<rect x="30" y="90" width="260" height="140" rx="14" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="160" y="118" fill="#e5edf8" font-size="17" font-weight="bold" text-anchor="middle">EPG-Web</text><rect x="55" y="140" width="210" height="55" rx="8" fill="#0a1727" stroke="#38bdf8" stroke-width="1.2"/><text x="160" y="163" fill="#e5edf8" font-size="14" text-anchor="middle">Serveur Web</text><text x="160" y="182" fill="#a9bdd5" font-size="12" text-anchor="middle">Consomme l’API App</text>
<rect x="370" y="90" width="260" height="140" rx="14" fill="#0d2a27" stroke="#34d399" stroke-width="1.6"/><text x="500" y="118" fill="#e5edf8" font-size="17" font-weight="bold" text-anchor="middle">EPG-App</text><rect x="395" y="140" width="210" height="55" rx="8" fill="#0a1727" stroke="#34d399" stroke-width="1.2"/><text x="500" y="163" fill="#e5edf8" font-size="14" text-anchor="middle">Serveur applicatif</text><text x="500" y="182" fill="#a9bdd5" font-size="12" text-anchor="middle">Fournit l’API</text>
<rect x="710" y="90" width="260" height="140" rx="14" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.6"/><text x="840" y="118" fill="#e5edf8" font-size="17" font-weight="bold" text-anchor="middle">EPG-DB</text><rect x="735" y="140" width="210" height="55" rx="8" fill="#0a1727" stroke="#fbbf24" stroke-width="1.2"/><ellipse cx="770" cy="165" rx="12" ry="5" fill="none" stroke="#fbbf24" stroke-width="1.5"/><path d="M758 165 V179 C758 185 782 185 782 179 V165" fill="none" stroke="#fbbf24" stroke-width="1.5"/><text x="850" y="173" fill="#e5edf8" font-size="14" text-anchor="middle">Base de données</text>
<path class="flow" d="M290 155 H365" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci5green)"/><rect x="293" y="123" width="69" height="22" rx="5" fill="#07111e"/><text x="327" y="138" fill="#34d399" font-size="10.5" text-anchor="middle">Contrat 1 API</text>
<path class="flow" d="M630 155 H705" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci5green)"/><rect x="633" y="123" width="69" height="22" rx="5" fill="#07111e"/><text x="667" y="138" fill="#34d399" font-size="10.5" text-anchor="middle">Contrat 2 DB</text>
<path class="flow" d="M160 230 V300 H840 V230" fill="none" stroke="#fb7185" stroke-width="2.5" stroke-dasharray="6 5" marker-end="url(#aci5red)"/><circle cx="500" cy="300" r="13" fill="#3b111d" stroke="#fb7185" stroke-width="1.5"/><path d="M494 294 L506 306 M506 294 L494 306" stroke="#fb7185" stroke-width="2"/><text x="500" y="328" fill="#fb7185" font-size="13" text-anchor="middle" font-weight="bold">Web vers DB : refusé si aucun contrat ne l’autorise</text>
<rect x="100" y="365" width="800" height="55" rx="10" fill="#111d30" stroke="#334155" stroke-width="1.2"/><text x="500" y="388" fill="#e5edf8" font-size="13" text-anchor="middle">Provider : EPG cible • Consumer : EPG source • Contrat : relation de politique</text><text x="500" y="407" fill="#a9bdd5" font-size="12" text-anchor="middle">Les ports sont des exemples ; les filtres doivent refléter les besoins réels de l’application.</text>
<text x="30" y="447" fill="#a9bdd5" font-size="11">Vert : flux autorisés. Rouge : flux Web vers DB à bloquer.</text>
</svg>
</div>

Les flèches vertes montrent les communications autorisées dans l’exemple ; la flèche rouge représente un flux qui ne doit pas être autorisé par la politique prévue. La relation provider/consumer concerne l’usage du contrat ; il faut distinguer cette relation logique du sens des paquets d’une session TCP.

## 9. Comprendre les contrats sans créer de règles trop larges

### 9.1 Fournisseur et consommateur

L’EPG provider offre les services définis dans le contrat. L’EPG consumer peut utiliser ce service. Plusieurs EPG peuvent consommer un contrat lorsque la portée et le design l’autorisent. Un même EPG peut fournir et consommer différents contrats.

Cette réutilisation peut réduire la duplication des règles, mais les portées et exceptions doivent être comprises. Avant d’étendre un contrat au niveau tenant ou à une portée plus large, vérifie si tous les consommateurs doivent vraiment posséder le même accès.

### 9.2 Filtres précis

Pour un service web, un filtre peut définir TCP destination port 443. Pour une API interne, il peut viser un port particulier. Un filtre trop large accorde des communications supplémentaires qui peuvent ne pas être souhaitées.

Les filtres doivent correspondre au fonctionnement de l’application :
- protocole réellement utilisé ;
- port côté destination ;
- directions et retour nécessaires ;
- éventuellement combinaison de plusieurs entrées de filtre ;
- exceptions explicitement justifiées.

Ne suppose pas que le port standard d’un service est forcément celui utilisé dans ton environnement. Confirme la configuration de l’application et les logs.

### 9.3 Sujet et options de contrat

Le sujet organise les filtres et certains comportements associés. Les options et comportements disponibles varient selon les versions. Le débutant doit surtout savoir lire la relation contrat → sujet → filtre, puis consulter le guide de la release pour les options particulières.

### 9.4 Contrats et trafic externe

Pour relier des EPG internes à des réseaux externes, ACI utilise notamment des objets de type L3Out et des EPG d’extérieur. Les contrats et les relations de politique déterminent les flux entre les groupes internes et le réseau extérieur, selon le modèle déployé. Le border leaf héberge la connexion externe dans la conception habituelle.

Ne confonds pas une route externe et l’autorisation par contrat : la route indique comment atteindre la destination ; la politique décide quels flux sont permis. Il faut vérifier les deux.

### 9.5 Les exceptions à connaître

ACI possède des fonctions et des modèles de politique plus avancés que le contrat simple décrit ici : EPG préférés, objets communs, `vzAny`, politiques partagées, contrats inter-tenants, services L4-L7 et options de filtre avancées. Il ne faut pas les configurer comme raccourci avant de comprendre leurs effets et leur portée. Une règle partagée trop large peut élargir involontairement l’accès.

## 10. Relier ACI au réseau externe : Border Leaf et L3Out

### 10.1 Pourquoi un border leaf ?

Le border leaf est un leaf utilisé pour connecter la fabric à un réseau externe, par exemple le réseau de campus, un cœur IP, un firewall, un routeur WAN ou une autre infrastructure. Le point d’entrée externe est conçu pour échanger des routes et des paquets entre les contextes ACI appropriés et le reste du réseau.

Le terme « border » ne veut pas dire que tous les flux doivent nécessairement traverser un seul équipement. Le design peut utiliser plusieurs border leaf et chemins redondants selon les exigences.

### 10.2 L3Out

Un **L3Out** est un objet ACI utilisé pour définir une connectivité de couche 3 vers un réseau externe. Selon la conception, il peut inclure des interfaces, des profils de connectivité, des routes, des protocoles et des EPG représentant les destinations ou préfixes externes.

Les détails de routage et de publication de préfixes dépendent du protocole et des options choisies. Il faut savoir :
- quelles interfaces et quels équipements externes sont raccordés ;
- quelles routes sont apprises ou annoncées ;
- quels préfixes sont autorisés ;
- quel contexte VRF est associé ;
- comment les contrats permettent le trafic ;
- si les chemins et le retour sont symétriques.

### 10.3 Routes statiques ou BGP

Un réseau externe peut être raccordé par des routes statiques ou un protocole de routage tel que BGP, selon le design. Le routage dynamique peut simplifier la propagation et la redondance mais doit être filtré et surveillé. Les routes statiques peuvent convenir à des scénarios simples mais doivent être mises à jour et testées avec soin.

### 10.4 Plan de test L3Out

Pour valider une connexion :
1. vérifier l’état physique et les voisins ;
2. confirmer l’interface et l’adressage ;
3. examiner les routes apprises/annoncées ;
4. valider les préfixes et la route retour ;
5. confirmer le contrat ou la politique d’accès externe ;
6. tester le protocole et le port depuis une source autorisée ;
7. tester le refus depuis une source qui ne doit pas être autorisée ;
8. vérifier les événements et les compteurs.

### Schéma 6 — Border leaf et réseau externe

<div class="aci-diagram">
<svg viewBox="0 0 1000 425" width="100%" role="img" aria-label="Endpoint ACI, leaf, border leaf, routeur externe et réseau d'entreprise avec flux aller et retour fléchés" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="aci6green" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#34d399"/></marker><marker id="aci6blue" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#38bdf8"/></marker></defs>
<rect x="20" y="65" width="580" height="220" rx="16" fill="#0a1727" stroke="#60a5fa" stroke-width="1.7"/><text x="310" y="90" fill="#e5edf8" font-size="16" font-weight="bold" text-anchor="middle">Fabric ACI</text>
<rect x="50" y="130" width="155" height="95" rx="11" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="127" y="161" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Endpoint</text><text x="127" y="184" fill="#a9bdd5" font-size="12" text-anchor="middle">EPG applicatif</text><text x="127" y="205" fill="#a9bdd5" font-size="12" text-anchor="middle">IP privée</text>
<rect x="260" y="130" width="140" height="95" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="330" y="161" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Leaf interne</text><text x="330" y="184" fill="#a9bdd5" font-size="12" text-anchor="middle">Forwarding</text>
<rect x="445" y="130" width="135" height="95" rx="11" fill="#211d3a" stroke="#a78bfa" stroke-width="1.5"/><text x="512" y="161" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Border leaf</text><text x="512" y="184" fill="#c4b5fd" font-size="12" text-anchor="middle">L3Out / routes</text>
<rect x="670" y="130" width="140" height="95" rx="11" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><text x="740" y="161" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">Routeur / FW</text><text x="740" y="184" fill="#fcd34d" font-size="12" text-anchor="middle">Réseau externe</text>
<rect x="855" y="130" width="125" height="95" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="917" y="161" fill="#e5edf8" font-size="15" font-weight="bold" text-anchor="middle">LAN / WAN</text><text x="917" y="184" fill="#a9bdd5" font-size="12" text-anchor="middle">Préfixe distant</text>
<path class="flow" d="M205 176 H255" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci6green)"/><path class="flow" d="M400 176 H440" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci6green)"/><path class="flow" d="M580 176 H665" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci6green)"/><path class="flow" d="M810 176 H850" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#aci6green)"/>
<path class="flow" d="M917 230 V300 H127 V230" fill="none" stroke="#38bdf8" stroke-width="2.7" stroke-dasharray="7 5" marker-end="url(#aci6blue)"/><rect x="395" y="284" width="260" height="27" rx="6" fill="#07111e" stroke="#334155"/><text x="525" y="302" fill="#38bdf8" font-size="12" text-anchor="middle">Chemin retour logique (illustratif)</text>
<text x="20" y="355" fill="#a9bdd5" font-size="12">Flèches vertes : endpoint vers réseau externe via L3Out. Flèche bleue : retour logique vers l’endpoint.</text><text x="20" y="376" fill="#a9bdd5" font-size="12">Vérifier routes aller/retour, contrats, préfixes annoncés et règles sur les équipements externes.</text><text x="20" y="397" fill="#a9bdd5" font-size="12">Le retour est tracé sous les équipements pour être lisible ; il représente le chemin inverse, pas un câble distinct.</text>
</svg>
</div>

## 11. Hyperviseurs et intégration des workloads

### 11.1 Serveurs physiques

Pour un serveur physique, il faut rattacher le port ou le bundle au profil d’accès adapté et à l’EPG. La politique doit refléter le VLAN/encapsulation, la configuration du serveur et le mode de redondance.

Avant de conclure à une erreur de contrat, confirme d’abord que le serveur est correctement raccordé et identifié. Beaucoup de problèmes apparents de politique proviennent d’un endpoint affecté au mauvais EPG ou d’une configuration de port incompatible.

### 11.2 Machines virtuelles

Dans des environnements virtualisés supportés, l’intégration VMM permet à ACI de participer à l’association des réseaux logiques et des workloads. Les détails varient selon la plateforme de virtualisation, la version et le chemin d’intégration. Vérifie les domaines VMM, les pools VLAN, les profils, les contrôleurs et les exigences de compatibilité.

### 11.3 Mobilité des endpoints

Lorsqu’une VM migre d’un hyperviseur à un autre, ou qu’un workload change de port, les informations d’endpoint et la classification EPG doivent rester cohérentes. Les événements de mobilité, l’apprentissage de MAC/IP et les associations dynamiques peuvent aider à identifier la cause.

### 11.4 Distinguer problème d’accès et problème de politique

- Si l’endpoint ne rejoint pas la bonne EPG, vérifier le port, le VLAN, la liaison statique ou le domaine VMM.
- Si l’endpoint est classé correctement mais qu’un flux entre EPG échoue, vérifier les contrats, les filtres et la politique effective.
- Si le contrat est correct mais que le trafic ne rejoint pas la destination, vérifier IP, BD, VRF, route, apprentissage endpoint et le service cible.
- Si l’interface de gestion affiche des défauts, examiner les détails, les timestamps et les composants concernés.

## 12. Diagnostic ACI pour débutant

Le meilleur dépannage suit le chemin d’une communication. Une application qui ne fonctionne pas ne prouve pas que le contrat est fautif.

### 12.1 Étape 1 : identifier les endpoints

Détermine la source et la destination :
- adresse IP et MAC ;
- port et leaf auxquels elles sont connectées ;
- EPG attendu et EPG effectif ;
- BD associé ;
- VRF associée ;
- VLAN/encapsulation et domaine d’accès.

Vérifie que ces informations correspondent à la documentation. Si la source est dans le mauvais EPG, l’ajout d’un contrat ne corrige pas la classification.

### 12.2 Étape 2 : vérifier la fabric physique

Examine :
- état des leaf/spine ;
- liens et erreurs d’interface ;
- voisins et câblage ;
- état de la connectivité fabric ;
- défauts actifs ;
- configuration des bundles et des ports.

Si plusieurs endpoints raccordés au même leaf sont affectés, cherche des causes communes : lien, configuration de port, nœud ou policy group.

### 12.3 Étape 3 : vérifier le modèle logique

Vérifie les relations essentielles :
- l’EPG est dans le bon Application Profile ;
- l’EPG est associé au BD attendu ;
- le BD est lié à la VRF voulue ;
- les sous-réseaux/passerelles sont corrects ;
- le contrat est fourni par le bon EPG et consommé par le bon EPG ;
- le sujet et le filtre correspondent au protocole et au port réels ;
- les exceptions ou contrats partagés ne changent pas le comportement attendu.

### 12.4 Étape 4 : tester de manière ciblée

Fais un test positif (flux attendu autorisé) et un test négatif (flux interdit). Note source, destination, protocole, port, heure et résultat. Consulte les outils de visibilité et les logs pris en charge par la version ACI. Les fonctionnalités de troubleshooting varient selon les versions et le type de flux.

Évite de désactiver globalement les contrats ou d’ajouter un accès très large pour « vérifier ». Ce test pourrait masquer la vraie cause et créer une exposition. Modifie un seul élément à la fois, avec un plan de retour arrière.

### 12.5 Étape 5 : vérifier le service et le retour

Même quand la politique autorise un flux :
- l’adresse IP peut être incorrecte ;
- la passerelle peut être absente ;
- le serveur peut ne pas écouter ;
- le pare-feu local peut bloquer ;
- le port applicatif peut différer ;
- un problème DNS/TLS ou applicatif peut survenir ;
- le chemin retour peut être absent ou incompatible.

### Schéma 7 — Arbre de dépannage d’un flux ACI

<div class="aci-diagram">
<svg viewBox="0 0 1000 480" width="100%" role="img" aria-label="Arbre de diagnostic ACI avec étapes endpoint, contrat, BD VRF, routage et service, flèches directionnelles" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="aci7blue" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#38bdf8"/></marker><marker id="aci7green" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#34d399"/></marker></defs>
<rect x="330" y="15" width="340" height="55" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="500" y="38" fill="#e5edf8" font-size="15" text-anchor="middle" font-weight="bold">Flux ACI en échec</text><text x="500" y="56" fill="#a9bdd5" font-size="12" text-anchor="middle">Noter source, destination et port</text>
<path class="flow" d="M500 70 V92" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#aci7blue)"/><rect x="330" y="95" width="340" height="60" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.5"/><text x="500" y="120" fill="#e5edf8" font-size="14" text-anchor="middle" font-weight="bold">1. Endpoint dans le bon EPG ?</text><text x="500" y="140" fill="#c4b5fd" font-size="12" text-anchor="middle">Port, VLAN, domaine, classification</text>
<path class="flow" d="M330 125 H185 V186" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#aci7blue)"/><path class="flow" d="M670 125 H815 V186" fill="none" stroke="#34d399" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#aci7green)"/><text x="205" y="115" fill="#a9bdd5" font-size="12">Non</text><text x="785" y="115" fill="#a9bdd5" font-size="12">Oui</text>
<rect x="35" y="190" width="300" height="65" rx="10" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><text x="185" y="216" fill="#e5edf8" font-size="14" text-anchor="middle" font-weight="bold">Corriger le raccordement</text><text x="185" y="237" fill="#fcd34d" font-size="12" text-anchor="middle">Port, encapsulation, EPG</text>
<rect x="665" y="190" width="300" height="65" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="815" y="216" fill="#e5edf8" font-size="14" text-anchor="middle" font-weight="bold">2. Contrat adéquat ?</text><text x="815" y="237" fill="#a9bdd5" font-size="12" text-anchor="middle">Provider, consumer, filtre, port</text>
<path class="flow" d="M815 255 V277" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#aci7blue)"/><rect x="665" y="282" width="300" height="65" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="815" y="308" fill="#e5edf8" font-size="14" text-anchor="middle" font-weight="bold">3. BD / VRF / routes corrects ?</text><text x="815" y="329" fill="#a9bdd5" font-size="12" text-anchor="middle">Subnet, passerelle, chemin retour</text>
<path class="flow" d="M815 347 V369" fill="none" stroke="#34d399" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#aci7green)"/><rect x="665" y="374" width="300" height="65" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="815" y="400" fill="#e5edf8" font-size="14" text-anchor="middle" font-weight="bold">4. Service fonctionnel ?</text><text x="815" y="421" fill="#a9bdd5" font-size="12" text-anchor="middle">Port, pare-feu OS, DNS, application</text>
<text x="35" y="306" fill="#a9bdd5" font-size="12">À chaque étape :</text><text x="35" y="327" fill="#a9bdd5" font-size="12">tester, noter le résultat,</text><text x="35" y="348" fill="#a9bdd5" font-size="12">modifier une seule chose.</text><text x="35" y="390" fill="#a9bdd5" font-size="12">Ne désactive pas</text><text x="35" y="411" fill="#a9bdd5" font-size="12">toute la politique</text><text x="35" y="432" fill="#a9bdd5" font-size="12">pour diagnostiquer.</text>
</svg>
</div>

## 13. Défauts, événements et changements

### 13.1 Défaut n’est pas toujours panne de service

ACI peut afficher des défauts qui décrivent une configuration non conforme, un lien, une politique, un composant ou un événement. Certains défauts sont informatifs, d’autres exigent une action. Un défaut rouge ou orange doit être ouvert et analysé, pas seulement compté.

Pour chaque défaut, note :
- le texte et l’identifiant exacts ;
- le nœud ou l’objet concerné ;
- l’heure de début ;
- le changement récent éventuel ;
- les impacts observés ;
- les compteurs, logs et tests associés ;
- la remédiation envisagée et son risque.

### 13.2 Changement contrôlé

Une modification ACI peut avoir un impact sur plusieurs endpoints ou EPG si l’objet est partagé. Avant de changer un contrat, un filtre, un BD ou un profil d’accès, identifie tous les consommateurs. L’effet d’un objet partagé doit être compris avant l’application.

Bonnes pratiques :
- sauvegarder/exporter la configuration selon la procédure approuvée ;
- enregistrer l’état initial ;
- tester en lab ou préproduction ;
- approuver le changement par les responsables concernés ;
- prévoir un rollback précis ;
- surveiller les flux autorisés et refusés après le changement ;
- mettre à jour le diagramme et la matrice de flux.

### 13.3 Automatisation et API

Les API APIC peuvent servir à lire les objets, automatiser des changements et intégrer la fabric aux processus de déploiement. La structure des objets, les méthodes d’authentification, les versions d’API et les réponses d’erreur doivent suivre la documentation Cisco de la release.

Pour débuter, l’automatisation devrait privilégier des modifications limitées, idempotentes, journalisées et testées. Les identifiants d’automatisation doivent avoir un rôle minimal, des secrets protégés et un cycle de rotation. Ne colle pas des credentials dans un script versionné.

## 14. Erreurs fréquentes des débutants

**Confondre APIC et routeur de données.** L’APIC orchestre et gère ; les leaf/spine transfèrent les paquets.

**Brancher les serveurs sur les spine.** Dans l’architecture leaf-spine ACI habituelle, les endpoints sont raccordés aux leaf ; les spine relient les leaf.

**Penser que le tenant est le réseau.** Le tenant organise les objets de politique ; la VRF, le BD, les EPG, les connexions et les contrats ont des rôles distincts.

**Confondre BD et EPG.** Le BD correspond à un domaine de couche 2 et à ses paramètres ; l’EPG regroupe les endpoints partageant une politique.

**Oublier l’association BD–VRF.** Le BD doit être associé au contexte de routage attendu selon la configuration.

**Créer un contrat au mauvais endroit.** Un contrat doit être fourni/consommé par les EPG concernés et posséder les filtres adaptés.

**Utiliser un filtre trop large.** Cela peut autoriser des services non nécessaires et rendre les audits difficiles.

**Supposer qu’une route autorise le trafic.** Une route donne un chemin ; la politique de sécurité reste à vérifier.

**Supposer que tout flux intra-tenant est autorisé.** Les tenants contiennent des objets ; les autorisations entre EPG dépendent du modèle de politique et des exceptions configurées.

**Confondre port VLAN et EPG.** Le VLAN aide à identifier l’encapsulation d’accès, alors que l’EPG est un objet de politique.

**Désactiver tous les contrats pour dépanner.** Cette action masque la cause et élargit dangereusement les accès.

**Oublier le réseau externe.** Un L3Out, les routes, les filtres et les contrats vers les EPG externes doivent être compris séparément.

## 15. Atelier guidé : concevoir une application trois couches

### Objectif

Définir un modèle ACI pour une application web, sans entrer dans les commandes spécifiques à une version matérielle.

### Étape 1 — Décrire la topologie

Prévois plusieurs leaf reliés à plusieurs spine. Connecte les serveurs à des leaf et identifie les leaf qui serviront de border leaf pour le réseau externe. Documente les liens, les débits, les chemins redondants et les connexions des APIC.

### Étape 2 — Créer les objets logiques

Dans un tenant de travail, prépare une VRF et un ou plusieurs bridge domains selon l’isolation voulue. Crée un Application Profile avec `EPG-Web`, `EPG-App` et `EPG-DB`, puis associe chaque EPG au BD prévu. Les paramètres exacts dépendent des besoins de couche 2 et de couche 3.

### Étape 3 — Raccorder les endpoints

Pour chaque serveur, note le port physique ou la liaison virtuelle, l’encapsulation/VLAN, le domaine, le profil de port et l’EPG. Vérifie l’IP et la passerelle. Confirme dans l’APIC que l’endpoint est appris et associé à l’EPG attendu.

### Étape 4 — Construire les contrats

Prépare des filtres pour :
- HTTPS des clients vers le point d’entrée, si celui-ci est géré dans le périmètre ACI ;
- communication Web vers App sur le port réel de l’API ;
- communication App vers DB sur le port réel de la base ;
- supervision depuis les outils autorisés.

Crée les contrats et affecte les rôles provider/consumer. Note précisément quels flux sont attendus et lesquels doivent être bloqués.

### Étape 5 — Relier l’extérieur

Définis le L3Out, les interfaces et les routes nécessaires. Détermine quels préfixes sont importés et exportés, et comment le trafic externe est filtré. Vérifie le chemin retour et l’association au bon contexte.

### Étape 6 — Valider

Effectue des tests positifs et négatifs :
- requête utilisateur vers Web ;
- Web vers App ;
- App vers DB ;
- Web vers DB en direct (doit être bloqué si non prévu) ;
- flux d’administration depuis une source autorisée ;
- accès depuis un endpoint mal classé (ne doit pas hériter par erreur d’une politique permissive) ;
- connectivité externe et retour.

### Étape 7 — Documenter

Livrables :
- diagramme physique leaf/spine et raccordement serveur ;
- schéma logique Tenant/VRF/BD/EPG/Contracts ;
- matrice de flux ;
- liste des filtres et ports ;
- plan de test ;
- liste des défauts résiduels ;
- procédure de retour arrière.

## 16. Mini-évaluation

### Questions

1. Que signifie Cisco ACI ?
2. Quel est le rôle principal d’un leaf ?
3. Pourquoi les serveurs sont-ils habituellement reliés aux leaf plutôt qu’aux spine ?
4. Quel est le rôle du spine ?
5. Quelle est la responsabilité principale de l’APIC ?
6. Pourquoi ne doit-on pas décrire l’APIC comme un routeur traversé par chaque paquet ?
7. Quelle différence y a-t-il entre underlay et overlay ?
8. À quoi sert un tenant ?
9. Quel rôle joue une VRF ?
10. Quel rôle joue un bridge domain ?
11. À quoi sert un EPG ?
12. Que représente un contrat ?
13. Quelle est la différence entre un filtre et un contrat ?
14. Qu’indiquent provider et consumer ?
15. Une route suffit-elle à autoriser une connexion ?
16. À quoi sert un L3Out ?
17. Pourquoi faut-il confirmer qu’un endpoint appartient au bon EPG ?
18. Pourquoi est-il dangereux de désactiver globalement les contrats pour dépanner ?
19. Que faut-il contrôler quand un tunnel ou une connexion externe est actif mais que l’application ne répond pas ?
20. Pourquoi faut-il effectuer des tests positifs et négatifs ?

### Corrigé

1. Application Centric Infrastructure.
2. Connecter les endpoints à la fabric et assurer le forwarding/politique nécessaires.
3. Les leaf sont les points d’accès ; les spine constituent le transport entre leaf.
4. Fournir la connectivité de transport à haut débit entre les leaf.
5. Gérer, configurer, distribuer les politiques et superviser la fabric.
6. Les paquets sont transférés par les switches leaf/spine ; l’APIC est le contrôleur de gestion/politique.
7. L’underlay est le transport physique/IP ; l’overlay fournit les réseaux/logiques encapsulés au-dessus.
8. Organiser un domaine logique de politiques et de ressources ; ce n’est pas à lui seul un réseau privé.
9. Définir le contexte de routage de couche 3.
10. Définir un domaine de couche 2 et ses paramètres de forwarding/subnets selon la configuration.
11. Regrouper des endpoints partageant une politique.
12. Une relation de communication entre EPG selon des règles.
13. Le filtre spécifie protocole/ports ; le contrat organise le service/les règles et les relations provider/consumer.
14. Provider fournit le service ; consumer exprime l’usage du contrat par le groupe qui en a besoin.
15. Non. Il faut aussi une politique autorisante, un service actif et un chemin retour valide.
16. Définir la connectivité de couche 3 avec un réseau externe.
17. La classification conditionne la politique qui s’applique aux communications.
18. Cela masque la cause et peut autoriser des flux non désirés.
19. Routes, contrats, filtres, endpoints, adresse IP, passerelle, service et retour.
20. Un flux attendu doit fonctionner et un flux interdit doit échouer selon la politique.

## 17. Checklist avant la mise en production

### Fabric physique
- [ ] Topologie leaf-spine conforme au design et au matériel supporté.
- [ ] Liaisons et débits documentés, redondance testée.
- [ ] Endpoints raccordés aux leaf selon les politiques d’accès.
- [ ] Border leaf et connexions externes identifiés.
- [ ] Cluster APIC sain et accès d’administration protégés.

### Modèle logique
- [ ] Tenants, VRF, BD et EPG nommés de manière cohérente.
- [ ] Associations BD–VRF et EPG–BD vérifiées.
- [ ] Endpoints classés dans les EPG attendus.
- [ ] Contrats provider/consumer et filtres revus.
- [ ] Contrats partagés et exceptions comprennent une justification.
- [ ] L3Out, routes et EPG externes vérifiés si utilisés.

### Sécurité et exploitation
- [ ] Les ports autorisés sont documentés et aussi précis que possible.
- [ ] Les flux interdits ont été testés.
- [ ] Les événements et défauts actifs ont été examinés.
- [ ] Une sauvegarde/export et un retour arrière sont disponibles.
- [ ] Les changements sont approuvés et attribuables.
- [ ] Les API/identifiants d’automatisation sont protégés.
- [ ] Les procédures de dépannage distinguent physique, endpoint, politique et application.

## 18. Glossaire

- **ACI** : Application Centric Infrastructure, solution de réseau de data center pilotée par politiques.
- **APIC** : contrôleur central de gestion et de politique ACI.
- **BD (Bridge Domain)** : domaine logique de couche 2 avec des paramètres réseau associés.
- **Border leaf** : leaf utilisé pour relier la fabric ACI à un réseau externe dans le design.
- **Contract** : objet de politique qui définit une relation de communication entre EPG.
- **Consumer** : EPG qui consomme le service déclaré dans un contrat.
- **EPG (Endpoint Group)** : regroupement logique d’endpoints partageant une politique.
- **Endpoint** : entité raccordée ou associée à la fabric, par exemple un serveur ou une VM.
- **Filter** : critères de trafic, notamment protocole et ports, utilisés par les politiques de contrat.
- **L3Out** : objet ACI décrivant une connectivité de couche 3 vers l’extérieur.
- **Leaf** : commutateur qui raccorde les endpoints à la fabric.
- **Overlay** : réseau logique encapsulé au-dessus du réseau de transport.
- **Provider** : EPG qui fournit le service défini dans un contrat.
- **Spine** : commutateur qui fournit le transport entre les leaf dans la topologie de fabric.
- **Tenant** : conteneur logique de politiques et de ressources.
- **Underlay** : infrastructure de transport physique/IP de la fabric.
- **VRF / Context** : contexte de routage de couche 3.
- **VXLAN** : mécanisme d’encapsulation utilisé pour transporter des réseaux logiques au-dessus d’une infrastructure IP.

## 19. Références officielles pour poursuivre

Pour les menus, options et procédures de configuration, utilise en priorité la documentation Cisco correspondant à la version ACI déployée :

- Cisco ACI Design Guide : https://www.cisco.com/c/en/us/td/docs/dcn/whitepapers/cisco-aci-design-guide.html
- Cisco APIC Basic Configuration Guide 6.2(x) — Basic User Tenant Configuration : https://www.cisco.com/c/en/us/td/docs/dcn/aci/apic/6x/basic-configuration/cisco-apic-basic-configuration-guide-62x/basic-user-tenant-configuration-62x.html
- Cisco ACI Fundamentals 6.2(x) — ACI Policy Model : https://www.cisco.com/c/en/us/td/docs/dcn/aci/apic/6x/aci-fundamentals/cisco-aci-fundamentals-62x/policy-model-62x.html
- Cisco APIC Layer 2 Networking Configuration Guide 6.2(x) — Bridge domains and subnets : https://www.cisco.com/c/en/us/td/docs/dcn/aci/apic/6x/l2-configuration/cisco-apic-layer-2-networking-configuration-guide-62x/bridging-62x/bridge-domain-subnets.html
- Cisco ACI Initial Deployment Cookbook : https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/white_papers/Cisco-ACI-Initial-Deployment-Cookbook.html
- Cisco ACI Contract Guide : https://www.cisco.com/c/en/us/products/collateral/networking/cloud-networking/application-centric-infrastructure/contract-guide.html

Les procédures peuvent changer entre les versions. Confirme toujours les commandes, l’interface, les options et les exigences matérielles dans les guides de la release que tu utilises.

---

## À retenir

ACI associe une fabric physique leaf-spine et un modèle de politiques applicatives. Les leaf raccordent les endpoints ; les spine transportent le trafic entre les leaf ; l’APIC gère la fabric et distribue la politique sans être le chemin de forwarding de chaque paquet. Dans le modèle logique, la VRF fournit le contexte de routage, le bridge domain structure la couche 2, l’EPG regroupe les endpoints et les contrats décrivent les communications autorisées entre groupes.

**Règle graphique appliquée :** chaque schéma de circuit comporte des flèches directionnelles ; les équipements utiles sont représentés ou nommés ; les flux permis et refusés sont distincts ; les connexions logiques sont visuellement séparées des flux de données. Les schémas sont pédagogiques et ne remplacent pas le diagramme réel de ton installation.
