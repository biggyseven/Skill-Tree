# Architecture Spine/Leaf — Niveau Expert

**Niveau :** Expert  
**Prérequis :** maîtrise des bases Spine/Leaf, routage IP/BGP ou IGP, ECMP, VXLAN/EVPN, VRF, MTU, QoS et dépannage de réseau.  
**Objectif :** concevoir, dimensionner, sécuriser, automatiser et exploiter une fabric à grande échelle en validant les comportements de contrôle et de données en fonctionnement normal, en cas de panne et sous congestion.

> **Périmètre et prudence.** Les extraits de configuration sont des modèles conceptuels, pas des commandes prêtes à exécuter. Valide toujours les fonctions, la syntaxe, les limites de ressources et les procédures sur le matériel, le système d’exploitation réseau et la version réellement déployés.


## 1. Périmètre du niveau expert

Une fabric Spine/Leaf experte ne se résume pas à augmenter le nombre de switches ou à activer BGP EVPN. Il faut maîtriser les propriétés de bout en bout : capacité disponible pendant une panne, cohérence entre contrôle et forwarding, limites des tables matérielles, isolation des tenants, comportement du plan de données sous congestion, automatisation sûre, observabilité et scénario de retour arrière.

Le fil conducteur de ce cours est une fabric routée multi-tenant, à laquelle on peut associer un overlay VXLAN/EVPN. Ce n’est pas le seul modèle possible : certaines installations utilisent une fabric L3 pure, des overlays différents, ou un réseau de service séparé. La bonne architecture est celle qui répond aux exigences de disponibilité, de latence, de sécurité, de croissance et de compétences de l’équipe.

**Résultats attendus :** produire un design argumenté ; démontrer le comportement sous N−1 ; expliquer une décision BGP/EVPN ; calculer un budget de capacité ; diagnostiquer un écart entre RIB, FIB et tables overlay ; déployer un changement progressif ; documenter un incident reproductible.

> Les exemples sont des modèles conceptuels. Les noms de commandes, limites matérielles, fonctions EVPN et comportements de convergence changent selon les constructeurs, les ASIC et les versions logicielles. Les valeurs proposées ne constituent pas une garantie de production.


## 2. Repenser la fabric comme un graphe de capacité

### 2.1 Clos à trois étages et variantes multi-étages

Un Clos classique associe des étages d’accès, d’agrégation et de cœur. Une fabric Spine/Leaf moderne est souvent une réalisation à trois étages dans laquelle les Leaf raccordent les endpoints et chaque Leaf est connecté à chaque Spine. Un seul saut Spine sépare alors les Leaf, dans la topologie logique normale. Lorsque la densité ou la distance dépasse les possibilités de la fabric, une architecture à cinq étages peut introduire des super-spines ou des blocs interconnectés.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 500" width="100%" height="auto" role="img" aria-label="Fabric Clos à trois étages : quatre Leaf reliés à trois Spine, chaque Leaf dispose d’un chemin vers chaque Spine">
<defs><marker id="ex1arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#63d8ff"/></marker></defs>
<style>.ex1leaf{fill:#153c2d;stroke:#72e0a4;stroke-width:2}.ex1sp{fill:#173652;stroke:#63d8ff;stroke-width:2}.ex1box{rx:10}.ex1t{font:700 15px system-ui,sans-serif;fill:#f1f6ff;text-anchor:middle}.ex1s{font:12px system-ui,sans-serif;fill:#b7c8da;text-anchor:middle}.ex1path{fill:none;stroke:#63d8ff;stroke-width:2.2;stroke-dasharray:7 6;marker-end:url(#ex1arr)}.ex1path path{animation:ex1move 2.8s linear infinite}.ex1p2{opacity:.8}.ex1p2 path{animation-delay:-1.3s}@keyframes ex1move{to{stroke-dashoffset:-26}}@media(prefers-reduced-motion:reduce){.ex1path path{animation:none}}</style>
<rect x="25" y="18" width="850" height="173" rx="15" fill="#0d1a28" stroke="#294761"/><text x="450" y="42" class="ex1s">Étage Spine — transit IP, sans serveurs directement raccordés</text>
<rect class="ex1box ex1sp" x="100" y="72" width="170" height="70"/><text class="ex1t" x="185" y="101">SPINE 1</text><text class="ex1s" x="185" y="122">ECMP / routes</text><rect class="ex1box ex1sp" x="365" y="72" width="170" height="70"/><text class="ex1t" x="450" y="101">SPINE 2</text><text class="ex1s" x="450" y="122">ECMP / routes</text><rect class="ex1box ex1sp" x="630" y="72" width="170" height="70"/><text class="ex1t" x="715" y="101">SPINE 3</text><text class="ex1s" x="715" y="122">ECMP / routes</text>
<rect x="25" y="216" width="850" height="156" rx="15" fill="#0d211b" stroke="#2c674a"/><text x="450" y="239" class="ex1s">Étage Leaf — accès aux workloads et passerelles de sous-réseaux</text>
<g class="ex1path"><path d="M185 142L130 280"/><path d="M185 142L345 280"/><path d="M185 142L555 280"/><path d="M185 142L765 280"/><path d="M450 142L130 280"/><path d="M450 142L345 280"/><path d="M450 142L555 280"/><path d="M450 142L765 280"/><path d="M715 142L130 280"/><path d="M715 142L345 280"/><path d="M715 142L555 280"/><path d="M715 142L765 280"/></g>
<g><rect class="ex1box ex1leaf" x="60" y="270" width="140" height="64"/><text class="ex1t" x="130" y="296">LEAF 1</text><text class="ex1s" x="130" y="316">VTEP / GW</text><rect class="ex1box ex1leaf" x="275" y="270" width="140" height="64"/><text class="ex1t" x="345" y="296">LEAF 2</text><text class="ex1s" x="345" y="316">VTEP / GW</text><rect class="ex1box ex1leaf" x="485" y="270" width="140" height="64"/><text class="ex1t" x="555" y="296">LEAF 3</text><text class="ex1s" x="555" y="316">VTEP / GW</text><rect class="ex1box ex1leaf" x="695" y="270" width="140" height="64"/><text class="ex1t" x="765" y="296">LEAF 4</text><text class="ex1s" x="765" y="316">VTEP / GW</text></g>
<g stroke="#72e0a4" stroke-width="2.2" fill="none"><path d="M130 334V400"/><path d="M345 334V400"/><path d="M555 334V400"/><path d="M765 334V400"/></g><g fill="#202d3e" stroke="#72e0a4" stroke-width="1.5"><rect x="55" y="400" width="150" height="48" rx="8"/><rect x="270" y="400" width="150" height="48" rx="8"/><rect x="480" y="400" width="150" height="48" rx="8"/><rect x="690" y="400" width="150" height="48" rx="8"/></g><g class="ex1t"><text x="130" y="429">Rack / serveurs</text><text x="345" y="429">Rack / serveurs</text><text x="555" y="429">Rack / serveurs</text><text x="765" y="429">Rack / serveurs</text></g><text x="450" y="478" class="ex1s">Chemins de transit multiples ; les flèches figurent les adjacences possibles, pas un unique flux simultané.</text></svg></div>

Le schéma représente la topologie logique et les chemins possibles. Les lignes animées symbolisent les chemins de transit, et non un unique paquet qui se réplique sur toutes les liaisons. Le réseau doit conserver une séparation de rôle : les Spine assurent le transit entre les Leaf ; les Border Leaf peuvent fournir l’interconnexion externe, selon le design.

### 2.2 Invariants d’architecture

Écrire les invariants avant de choisir la configuration :

- chaque Leaf dispose de chemins de transit indépendants vers plusieurs Spine ;
- le nombre de chemins, la capacité et la latence sont connus en fonctionnement normal et après panne ;
- aucun point unique non intentionnel ne coupe un groupe entier de workloads ;
- la gestion hors bande ne dépend pas uniquement de la fabric qu’elle doit dépanner ;
- les routes externes ont une politique d’import/export documentée ;
- le plan d’adressage, les identifiants de tenants et les allocations de VNI sont uniques dans leur domaine de portée ;
- chaque modification critique a un test positif, un test négatif et un rollback.

Une topologie est redondante uniquement si les chemins sont aussi indépendants que nécessaire. Deux liens qui partagent le même conduit, le même panneau optique, la même alimentation ou le même ASIC ne représentent pas toujours deux domaines de panne indépendants. La redondance physique doit être décrite dans l’inventaire, pas déduite de la seule présence de deux câbles.

### 2.3 Séparer les domaines de panne

Définir les domaines au moins aux niveaux suivants : interface, câble/transceiver, line card ou ASIC, équipement, rack, alimentation, zone de refroidissement, rangée, site et plan de contrôle. La panne d’un Spine est différente de la perte d’un lien Leaf–Spine ; la perte d’un ASIC peut faire tomber plusieurs ports simultanément ; la panne d’un route reflector ne devrait pas nécessairement interrompre le forwarding déjà installé.

Documenter les dépendances communes évite les scénarios de haute disponibilité trompeurs : deux RR dans le même rack avec la même alimentation, deux border leaf reliés au même routeur externe, ou des uplinks apparemment distincts sur une unique carte ligne.

### 2.4 Les Spine ne sont pas des super-Leaf

Raccorder directement des serveurs aux Spine, y placer des services spécifiques ou leur faire assumer un rôle de bordure modifie les propriétés attendues. Cela peut être légitime dans certains designs, mais cela doit être explicite, pris en charge par la plateforme et intégré dans les règles de forwarding, de sécurité et d’exploitation. Une exception non documentée rend les chemins difficiles à raisonner et fragilise les automatismes qui supposent la symétrie du fabric.


## 3. Design underlay : routes, identifiants et simplicité opérationnelle

### 3.1 Objectifs et architecture d’adressage

L’underlay doit fournir une reachability IP prévisible entre loopbacks et, selon l’architecture, les autres adresses nécessaires à la fabric. Il n’a pas besoin de porter tous les réseaux de workloads. Un plan courant réserve des blocs distincts pour les liens Leaf–Spine, les loopbacks des Leaf, les loopbacks des Spine, la gestion hors bande et l’adressage des tenants. La séparation de ces blocs facilite les filtres et rend une route inattendue immédiatement visible.

En IPv4, des /31 ou /30 peuvent être employés sur des liens point-à-point, selon la prise en charge. L’adressage non numéroté réduit les allocations de transit et peut simplifier une fabric BGP, mais les possibilités et comportements de dépannage diffèrent selon les systèmes. Le plan doit dire comment identifier chaque interface, pas simplement attribuer des plages.

Une loopback sert d’identifiant logique stable, par exemple pour un Router ID, une session BGP ou un endpoint VTEP. Elle n’est pas une garantie de reachability : son adresse peut rester configurée localement alors que tous les chemins qui y mènent sont indisponibles. Il faut vérifier l’état de l’interface, sa présence dans la table de routage, les next-hops résolus et la programmation FIB.

### 3.2 eBGP underlay ou IGP

Un IGP (OSPF, IS-IS) construit un graphe de topologie au sein d’un domaine. Il est souvent familier aux équipes et peut fournir ECMP. BGP underlay, souvent eBGP entre Leaf et Spine, permet une approche explicite par voisinage et par politique ; il est décrit dans les retours d’expérience de déploiements data center à grande échelle, notamment le RFC 7938. Ce RFC est informatif, pas une obligation de conception.

**BGP eBGP underlay** peut présenter les avantages suivants :
- voisinages directs Leaf–Spine, souvent faciles à générer à partir de l’inventaire ;
- politiques de routes explicites et limites de propagation plus visibles ;
- séparation nette des AS selon le modèle retenu ;
- convergence et multipath alignés sur les fonctions supportées par la plateforme.

Les coûts opérationnels comprennent la conception des AS, les détails d’ASN par nœud ou par rôle, la politique de next-hop, les communautés, les filtres de préfixes, la gestion des route-maps et la compréhension des attributs BGP. Une erreur dans la politique peut supprimer une route ou la propager beaucoup trop largement.

**IGP underlay** est tout aussi valable lorsque l’équipe maîtrise ses aires, ses métriques, ses types de route et ses comportements de convergence. Une conception OSPF multi-aires ou IS-IS à grande échelle exige une discipline comparable. Éviter de multiplier les mécanismes sans besoin réel : un protocole connu et correctement exploité vaut mieux qu’un design prétendument élégant mais mal compris.

### 3.3 Politique et garde-fous BGP

Un voisin BGP établi ne signifie pas que les routes correctes sont acceptées, installées ou utilisées. L’exploitation doit contrôler le nombre de préfixes reçus, les familles d’adresses actives, les attributs, le next-hop, les communities et l’état des routes dans le RIB et le FIB.

Principes de base :

- utiliser des listes de préfixes et des politiques d’import/export explicites ;
- limiter les routes acceptées à ce qu’un voisin est censé annoncer ;
- ne pas accepter une route par défaut ou des préfixes Internet depuis la fabric sans décision d’architecture ;
- documenter la propagation des communautés et les règles d’agrégation ;
- vérifier le comportement de route refresh, de graceful restart et de convergence après session reset ;
- journaliser les changements de voisinage et les transitions de préfixes ;
- éviter un `permit any` temporaire qui devient permanent.

Dans une fabric eBGP, les détails de propagation du next-hop ou de l’AS_PATH peuvent différer selon le choix de design. Les recettes génériques ne remplacent pas le test de la version logicielle réelle. Une configuration est correcte si les routes voulues sont présentes, les routes interdites absentes, et si les mêmes propriétés restent vraies après panne et redémarrage.

### 3.4 Exemple conceptuel de voisinage eBGP

```text
LEAF-01
  interface Ethernet1/1 -> SPINE-01
  interface Ethernet1/2 -> SPINE-02
  loopback0             -> router-id / identifiant stable
  BGP AS 65101          -> voisin SPINE-01 AS 65001
                         -> voisin SPINE-02 AS 65002
  export underlay       -> loopback(s) attendues seulement
  import underlay       -> préfixes autorisés seulement
```

Ce pseudo-exemple n’est pas une syntaxe de configuration. Il montre le modèle de données à fournir à un générateur : équipement, interfaces, adresses, ASN local, voisin, ASN distant et politiques attachées. La validation doit contrôler les deux extrémités du lien, pas uniquement générer des lignes d’un côté.

### 3.5 ECMP et cohérence entre contrôle et forwarding

Plusieurs routes peuvent être de coût ou de préférence équivalents au plan de contrôle, mais le plan de données ne les utilisera pas forcément toutes. Il faut vérifier : l’égalité des attributs qui comptent pour la décision, le nombre maximal de next-hops ECMP supporté et configuré, la résolution de chaque next-hop récursif, les limites de groupes de next-hops de l’ASIC et l’état des ports physiques.

La route sélectionnée par BGP/IGP (RIB) et le groupe de next-hops programmé dans la FIB doivent être cohérents. Si un next-hop existe dans le RIB mais pas dans le forwarding hardware, le problème est différent d’une route absente du RIB. Ce découpage est fondamental dans les diagnostics d’expert.


## 4. Overlay VXLAN/EVPN : comprendre les objets et les états

### 4.1 Trois plans, trois catégories de questions

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 430" width="100%" height="auto" role="img" aria-label="Séparation logique des plans : fabric underlay, control plane BGP EVPN, overlay VXLAN et workloads">
<defs><marker id="ex2arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#63d8ff"/></marker></defs><style>.ex2b{stroke-width:2;rx:11}.ex2t{font:700 16px system-ui,sans-serif;fill:#f0f6ff;text-anchor:middle}.ex2s{font:12.5px system-ui,sans-serif;fill:#c0cedd;text-anchor:middle}.ex2p{fill:none;stroke:#63d8ff;stroke-width:2.5;stroke-dasharray:8 6;marker-end:url(#ex2arr)}.ex2p path{animation:ex2d 2.6s linear infinite}.ex2p2{stroke:#c8a6ff;marker-end:url(#ex2arr)}.ex2p2 path{animation-delay:-1.1s}@keyframes ex2d{to{stroke-dashoffset:-28}}@media(prefers-reduced-motion:reduce){.ex2p path{animation:none}}</style>
<rect x="25" y="20" width="850" height="92" rx="14" fill="#141a2b" stroke="#68539d"/><text class="ex2t" x="450" y="48">Workloads / services</text><text class="ex2s" x="450" y="72">VM · conteneurs · bare metal · stockage · appliances</text><text class="ex2s" x="450" y="92">Besoin applicatif : connectivité, isolation, latence, débit</text>
<rect x="25" y="150" width="410" height="105" rx="14" fill="#102a20" stroke="#48bd80" stroke-width="2"/><text class="ex2t" x="230" y="180">Overlay de données</text><text class="ex2s" x="230" y="204">VXLAN · VNI · VTEP · passerelle distribuée</text><text class="ex2s" x="230" y="226">Transporte les segments logiques au-dessus de l’IP</text>
<rect x="465" y="150" width="410" height="105" rx="14" fill="#172e45" stroke="#63d8ff" stroke-width="2"/><text class="ex2t" x="670" y="180">Control plane</text><text class="ex2s" x="670" y="204">BGP EVPN · MAC/IP · Type 2 / Type 3 / Type 5</text><text class="ex2s" x="670" y="226">Distribue l’information de reachability et de politique</text>
<rect x="25" y="305" width="850" height="90" rx="14" fill="#111f2b" stroke="#4789b5" stroke-width="2"/><text class="ex2t" x="450" y="336">Underlay IP</text><text class="ex2s" x="450" y="360">Leaf ↔ Spine · loopbacks · ECMP · MTU · convergence</text><text class="ex2s" x="450" y="380">Assure la reachability IP des VTEP ; ne porte pas la sémantique des tenants</text>
<g class="ex2p"><path d="M230 112V150"/><path d="M670 112V150"/><path d="M230 255V305"/></g><g class="ex2p ex2p2"><path d="M670 255V305"/><path d="M435 202H465"/></g></svg></div>

L’underlay détermine si les VTEP peuvent se joindre en IP. Le control plane EVPN distribue la reachability et certains attributs d’attachement. L’overlay VXLAN encapsule le trafic au sein d’un segment logique. Une panne apparente « VXLAN » peut donc se trouver sur n’importe lequel de ces plans : route vers le VTEP manquante, route EVPN absente, mauvaise association VLAN/VNI, table MAC incorrecte, MTU insuffisante ou règle de sécurité bloquante.

### 4.2 VXLAN et identifiants

Un VTEP encapsule une trame ou un paquet dans un tunnel VXLAN afin de traverser l’underlay IP. Le VNI identifie le segment overlay. Le VNI est distinct du VLAN ID ; une correspondance VLAN–VNI locale peut être configurée sur le Leaf. Le champ VNI de VXLAN est sur 24 bits, mais les limites pratiques sont souvent imposées bien avant par les ressources d’implémentation, les modèles de gestion et les contraintes d’exploitation.

Il faut maintenir une source de vérité des associations : tenant/VRF, VLAN local, L2 VNI, L3 VNI éventuel, sous-réseau, Anycast Gateway, VTEP, import/export RT et règles de filtrage. Les collisions d’identifiants ne se limitent pas à une valeur numérique répétée : une erreur de portée des Route Targets peut importer des routes dans un tenant inapproprié, même si les VNI semblent uniques.

### 4.3 EVPN : types de routes à reconnaître

EVPN est un plan de contrôle BGP qui distribue des informations de connectivité de couche 2 et de couche 3. Les types de routes les plus souvent évoqués dans les fabrics VXLAN sont :

- **Type 2 — MAC/IP Advertisement :** annonce d’une adresse MAC et, selon le cas, d’une adresse IP associée. Sert notamment à distribuer la reachability des endpoints ; il intervient aussi dans les mécanismes de mobilité.
- **Type 3 — Inclusive Multicast Ethernet Tag :** permet notamment la découverte des VTEP qui participent à un segment et s’inscrit dans la gestion du trafic BUM selon le modèle de réplication retenu.
- **Type 5 — IP Prefix Route :** annonce de préfixes IP, utile pour les scénarios de routage inter-sous-réseaux ou d’échange de routes IP dans une fabric EVPN, suivant l’architecture.

D’autres types existent, notamment pour la découverte Ethernet A-D et les segments Ethernet en cas de multihoming. Ne pas mémoriser seulement un numéro de route : savoir quelle information elle transporte, qui la produit, quels attributs déterminent son import et quel état local elle doit créer.

### 4.4 Route Reflectors : rôle et pièges

Les route reflectors (RR) limitent le nombre de sessions iBGP EVPN dans une fabric iBGP. Ils distribuent les routes de contrôle mais ne sont généralement pas dans le chemin de données. Une architecture avec deux RR peut améliorer la disponibilité du plan de contrôle, à condition que les clients se connectent aux deux selon le design et que les politiques de redondance et de placement soient correctement réalisées.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 430" width="100%" height="auto" role="img" aria-label="Architecture BGP EVPN avec deux route reflectors redondants auxquels se connectent les Leaf ; le trafic des données passe directement de Leaf à Spine">
<defs><marker id="ex4arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#c6a6ff"/></marker><marker id="ex4dataarr" markerWidth="8" height="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#63d8ff"/></marker></defs><style>.ex4t{font:700 15px system-ui,sans-serif;fill:#f1f6ff;text-anchor:middle}.ex4s{font:12px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.ex4n{stroke-width:2;rx:10}.ex4ctrl{fill:none;stroke:#c6a6ff;stroke-width:2.4;stroke-dasharray:7 6;marker-end:url(#ex4arr)}.ex4ctrl path{animation:ex4d 2.7s linear infinite}.ex4data{fill:none;stroke:#63d8ff;stroke-width:2.3;stroke-dasharray:4 6;marker-end:url(#ex4dataarr)}@keyframes ex4d{to{stroke-dashoffset:-26}}@media(prefers-reduced-motion:reduce){.ex4ctrl path{animation:none}}</style>
<rect x="80" y="30" width="300" height="88" class="ex4n" fill="#28213a" stroke="#c6a6ff"/><text class="ex4t" x="230" y="59">RR-1</text><text class="ex4s" x="230" y="82">Route Reflector EVPN</text><text class="ex4s" x="230" y="101">Plan de contrôle</text>
<rect x="520" y="30" width="300" height="88" class="ex4n" fill="#28213a" stroke="#c6a6ff"/><text class="ex4t" x="670" y="59">RR-2</text><text class="ex4s" x="670" y="82">Route Reflector EVPN</text><text class="ex4s" x="670" y="101">Plan de contrôle</text>
<g class="ex4ctrl"><path d="M230 118L170 210"/><path d="M230 118L390 210"/><path d="M670 118L510 210"/><path d="M670 118L730 210"/><path d="M380 75H520"/></g>
<g><rect x="80" y="210" width="180" height="74" class="ex4n" fill="#17344d" stroke="#63d8ff"/><text class="ex4t" x="170" y="239">Leaf-01</text><text class="ex4s" x="170" y="261">VTEP / gateway</text><rect x="300" y="210" width="180" height="74" class="ex4n" fill="#17344d" stroke="#63d8ff"/><text class="ex4t" x="390" y="239">Leaf-02</text><text class="ex4s" x="390" y="261">VTEP / gateway</text><rect x="420" y="320" width="180" height="74" class="ex4n" fill="#153c2d" stroke="#72e0a4"/><text class="ex4t" x="510" y="349">Spine pair</text><text class="ex4s" x="510" y="371">Underlay IP / ECMP</text><rect x="640" y="210" width="180" height="74" class="ex4n" fill="#17344d" stroke="#63d8ff"/><text class="ex4t" x="730" y="239">Leaf-03</text><text class="ex4s" x="730" y="261">VTEP / gateway</text></g>
<g class="ex4data"><path d="M170 284L450 320"/><path d="M390 284L480 320"/><path d="M730 284L570 320"/></g><text class="ex4s" x="450" y="420">Les RR échangent des routes EVPN ; ils ne sont pas obligatoirement sur le chemin du trafic applicatif.</text></svg></div>

Contrôler que les RR reçoivent toutes les familles EVPN nécessaires, préservent les extended communities attendues, annoncent aux clients les routes voulues et ne masquent pas une route utile par un choix d’attribut inattendu. La redondance ne suffit pas si deux RR ont la même cause commune ou s’ils sont alimentés par une source de configuration erronée.

### 4.5 Passerelle distribuée et IRB

Avec une passerelle Anycast distribuée, plusieurs Leaf présentent la même adresse IP et MAC de passerelle au sein du réseau logique prévu. Cela permet à un endpoint de continuer à utiliser la même passerelle lorsqu’il se déplace entre Leaf compatibles. Cependant, l’Anycast Gateway ne dispense pas de configurer correctement l’IP subnet, le routage, les VNI et les politiques de l’overlay.

L’IRB (*Integrated Routing and Bridging*) relie le forwarding L2 et L3. En routage distribué, le paquet peut être routé localement au Leaf source et envoyé vers un VTEP distant. Il existe plusieurs variantes, dont des modèles symétriques et asymétriques d’interconnexion L2/L3 dans EVPN. Ils n’ont pas les mêmes besoins de ressources, de configuration et de transport des informations de routage. Choisir une variante explicitement, vérifier sa prise en charge multi-constructeur et ne pas mélanger des hypothèses d’un modèle avec des commandes d’un autre.

### 4.6 Trajet d’un paquet et vérification par état

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 450" width="100%" height="auto" role="img" aria-label="Flux entre deux workloads dans deux sous-réseaux logiques : encapsulation VXLAN sur le Leaf source et décapsulation sur le Leaf destination, EVPN fournit la reachability">
<defs><marker id="ex3arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#63d8ff"/></marker><marker id="ex3ctrlarr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#c6a6ff"/></marker></defs><style>.ex3t{font:700 15px system-ui,sans-serif;fill:#f0f6ff;text-anchor:middle}.ex3s{font:12px system-ui,sans-serif;fill:#bfccdc;text-anchor:middle}.ex3node{stroke-width:2;rx:10}.ex3path{fill:none;stroke:#63d8ff;stroke-width:2.6;stroke-dasharray:7 6;marker-end:url(#ex3arr)}.ex3path path{animation:ex3d 2.4s linear infinite}.ex3ctrl{fill:none;stroke:#c6a6ff;stroke-width:2.1;stroke-dasharray:4 6;marker-end:url(#ex3ctrlarr)}.ex3ctrl path{animation:ex3d 3.2s linear infinite}@keyframes ex3d{to{stroke-dashoffset:-26}}@media(prefers-reduced-motion:reduce){.ex3path path,.ex3ctrl path{animation:none}}</style>
<rect x="35" y="35" width="225" height="115" class="ex3node" fill="#16392a" stroke="#6ddca0"/><text class="ex3t" x="147" y="66">Hôte A</text><text class="ex3s" x="147" y="89">10.10.10.11</text><text class="ex3s" x="147" y="111">VLAN 10 / VNI 10010</text><text class="ex3s" x="147" y="132">MAC-A</text>
<rect x="330" y="35" width="240" height="115" class="ex3node" fill="#17344d" stroke="#63d8ff"/><text class="ex3t" x="450" y="66">Leaf source / VTEP A</text><text class="ex3s" x="450" y="89">Apprend MAC-A localement</text><text class="ex3s" x="450" y="111">Route EVPN vers MAC-B</text><text class="ex3s" x="450" y="132">Encapsule VXLAN</text>
<rect x="635" y="35" width="230" height="115" class="ex3node" fill="#17344d" stroke="#63d8ff"/><text class="ex3t" x="750" y="66">Leaf destination / VTEP B</text><text class="ex3s" x="750" y="89">Décapsule VXLAN</text><text class="ex3s" x="750" y="111">Résout MAC-B localement</text><text class="ex3s" x="750" y="132">Transmet au port hôte</text>
<rect x="300" y="240" width="300" height="76" class="ex3node" fill="#28213a" stroke="#c6a6ff"/><text class="ex3t" x="450" y="269">BGP EVPN / control plane</text><text class="ex3s" x="450" y="291">Publie reachability MAC/IP et VTEP</text>
<rect x="635" y="345" width="230" height="70" class="ex3node" fill="#16392a" stroke="#6ddca0"/><text class="ex3t" x="750" y="373">Hôte B</text><text class="ex3s" x="750" y="396">10.10.20.25 · MAC-B</text>
<g class="ex3path"><path d="M260 92H330"/><path d="M570 92H635"/><path d="M750 150V345"/></g><g class="ex3ctrl"><path d="M450 150V240"/><path d="M600 278H670V150"/></g><text class="ex3s" x="450" y="185">Paquet IP interne</text><text class="ex3s" x="750" y="220">Paquet VXLAN dans l’underlay IP</text><text class="ex3s" x="450" y="431">EVPN apprend et distribue la reachability ; le trafic applicatif suit le plan de données.</text></svg></div>

Le chemin logique typique est : hôte source → Leaf source → encapsulation VXLAN (si destination distante) → underlay IP/ECMP → Leaf destination → décapsulation → hôte. Si la destination est locale au même Leaf et au même segment, un tunnel inter-VTEP n’est pas nécessaire. Si le paquet traverse un routeur virtuel ou une passerelle distribuée, la décision L3 peut modifier les en-têtes internes et le segment de destination.

Pour un flux interrompu, tester dans l’ordre :

1. l’endpoint source est-il présent et attaché au bon port/VLAN ?
2. le Leaf source connaît-il la MAC/IP destination ou la route IP requise ?
3. la route EVPN appropriée a-t-elle été reçue et importée ?
4. la destination VTEP est-elle joignable dans l’underlay ?
5. l’association VLAN–VNI et les valeurs d’encapsulation sont-elles correctes ?
6. le MTU permet-il le paquet encapsulé ?
7. la table de forwarding matérielle et les compteurs confirment-ils le chemin ?
8. une ACL, une politique de sécurité, une route retour ou un service intermédiaire bloque-t-il le retour ?

Cette séquence évite de modifier à l’aveugle des paramètres d’overlay alors que la source du problème est une reachability IP underlay.


## 5. EVPN multihoming, mobilité et cohérence MAC/IP

### 5.1 Pourquoi le multihoming est complexe

Raccorder un hôte, un hyperviseur, un serveur de stockage ou un équipement à deux Leaf peut permettre la résilience et le partage de charge. Mais deux chemins Ethernet actifs créent des risques de boucles, de duplication BUM, de désaccord sur le point d’attachement et de flapping de MAC. LACP agrège des liens entre deux équipements qui présentent une identité logique compatible ; MLAG/vPC est une implémentation de redondance spécifique aux plateformes ; EVPN multihoming définit un modèle de contrôle et de signalisation qui ne doit pas être assimilé automatiquement à MLAG.

EVPN multihoming peut utiliser un Ethernet Segment Identifier (ESI) pour représenter un segment raccordé à plusieurs PE/VTEP. Les modes Single-Active et All-Active ont des propriétés différentes. Le choix affecte la sélection du forwarder désigné pour certains flux BUM, les règles de split horizon, les chemins de données et la manière de converger après une panne.

### 5.2 MAC mobility et flapping

Une MAC qui se déplace peut être un événement normal de mobilité de VM ou de workload. Une MAC qui oscille rapidement entre ports peut indiquer un double raccordement mal conçu, une boucle L2, un hyperviseur mal configuré, un équipement qui émet depuis plusieurs chemins ou un problème de contrôle. Le plan de contrôle EVPN inclut des mécanismes pour annoncer et arbitrer la mobilité, mais il ne rend pas bénins les cycles de flapping.

Pour diagnostiquer, comparer l’historique des annonces EVPN, l’ESI éventuel, les entrées MAC locales, les compteurs par port et la chronologie des changements sur les hôtes. Ne pas masquer le problème en augmentant simplement un seuil ou en désactivant les protections de mobilité. Identifier si le mouvement est légitime, puis corriger l’attachement, le teaming ou la politique de multihoming.

### 5.3 Split horizon et trafic BUM

BUM regroupe broadcast, unknown unicast et multicast. Les fabrics doivent traiter ces flux en fonction du segment : réplication locale, ingress replication via la liste des VTEP ou multicast de l’underlay selon la solution. Une erreur dans les listes de VTEP, la signalisation EVPN ou le split horizon peut provoquer des pertes, des duplications ou une boucle. Les procédures de split horizon sont spécifiques à l’encapsulation et au modèle de multihoming ; le RFC 9746, publié en mars 2025, actualise les procédures EVPN concernées et autorise la sélection de mécanismes dans les cas qu’il couvre. Cela illustre pourquoi les experts vérifient l’état courant des normes et le support de leur équipement plutôt que d’appliquer un résumé ancien.

### 5.4 Tests de résilience multihoming

Un plan de test sérieux inclut : perte d’un membre LAG, perte d’un Leaf, rétablissement d’un port, reboot d’un hôte, MAC qui migre, retrait d’une route EVPN, perte d’un RR, perte d’un chemin underlay, et trafic BUM pendant chaque transition. Mesurer la perte, le temps jusqu’au rétablissement, la duplication éventuelle et l’évolution des tables. Les résultats doivent être comparés à un objectif défini, pas à la phrase « le réseau est redondant ».


## 6. Border Leaf, routage externe et interconnexion de fabrics

### 6.1 Rôle des Border Leaf

Les Border Leaf forment la frontière entre les workloads/fabric et des réseaux externes : campus, WAN, Internet, pare-feu, équilibrage de charge, stockage ou autre data center. Les interfaces externes, VRF, routes et politiques doivent être conçues comme un domaine d’exploitation particulier. Il est souvent pertinent de séparer les Leaf d’accès ordinaires des Border Leaf afin de contrôler les dépendances et la capacité, mais certains environnements utilisent des rôles convergés que la plateforme prend explicitement en charge.

Décrire les chemins d’aller et de retour. Un préfixe annoncé vers l’extérieur n’est pas suffisant si le réseau externe ne connaît pas la route retour ; réciproquement, un défaut dans une route de retour peut donner l’impression d’une panne applicative alors que le trafic aller fonctionne. Documenter les points d’application des politiques, les zones de sécurité et le comportement en cas de perte d’un Border Leaf.

### 6.2 Import/export et fuite de routes entre VRF

Une VRF fournit une séparation de table de routage, mais cette séparation peut être volontairement modifiée par du route leaking, des Route Targets ou une route par défaut partagée. Une mauvaise politique peut créer une fuite entre tenants et constituer un incident de sécurité. Pour chaque échange, décrire : source, destination, préfixes autorisés, sens, propriétaire et justification. Réaliser les tests négatifs : un tenant qui ne doit pas voir un préfixe ne doit pas pouvoir l’atteindre même si une route existe dans une autre VRF.

Les Route Targets contrôlent l’import/export de routes EVPN dans les modèles concernés ; ils ne remplacent ni une politique de sécurité de workload ni un pare-feu. Ne pas considérer l’existence d’un VRF comme un contrôle complet de tous les flux L2/L3. Le routage, les ACL, les politiques de sécurité et les éventuels services doivent être modélisés séparément.

### 6.3 Interconnexion multi-site / DCI

Pour connecter plusieurs fabrics, il faut choisir un modèle DCI explicite : routage IP L3 entre sites, VRF/L3VPN, EVPN Multi-Site pris en charge par la plateforme, ou extension contrôlée de segments L2. La solution dépend de la mobilité des workloads, des besoins de broadcast, de la latence, de la bande passante, de la souveraineté des données et de la tolérance aux partitions.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 450" width="100%" height="auto" role="img" aria-label="Deux fabrics spine leaf distinctes interconnectées via Border Leaf, transport IP ou couche DCI, et politiques inter-sites">
<defs><marker id="ex7arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#63d8ff"/></marker></defs><style>.ex7t{font:700 15px system-ui,sans-serif;fill:#f1f6ff;text-anchor:middle}.ex7s{font:12px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.ex7n{stroke-width:2;rx:10}.ex7p{fill:none;stroke:#63d8ff;stroke-width:2.5;stroke-dasharray:7 6;marker-end:url(#ex7arr)}.ex7p path{animation:ex7d 2.7s linear infinite}@keyframes ex7d{to{stroke-dashoffset:-26}}@media(prefers-reduced-motion:reduce){.ex7p path{animation:none}}</style>
<rect x="25" y="25" width="360" height="260" rx="15" fill="#0e241d" stroke="#347b58"/><text class="ex7t" x="205" y="51">SITE / FABRIC A</text><rect x="85" y="72" width="120" height="52" class="ex7n" fill="#16392a" stroke="#72e0a4"/><text class="ex7t" x="145" y="102">Leaf A1</text><rect x="225" y="72" width="120" height="52" class="ex7n" fill="#16392a" stroke="#72e0a4"/><text class="ex7t" x="285" y="102">Leaf A2</text><rect x="85" y="165" width="260" height="55" class="ex7n" fill="#17344d" stroke="#63d8ff"/><text class="ex7t" x="215" y="189">Spine pair A</text><text class="ex7s" x="215" y="207">Underlay / VXLAN EVPN local</text><path d="M145 124V165M285 124V165" fill="none" stroke="#63d8ff" stroke-width="2.3"/>
<rect x="515" y="25" width="360" height="260" rx="15" fill="#0e241d" stroke="#347b58"/><text class="ex7t" x="695" y="51">SITE / FABRIC B</text><rect x="575" y="72" width="120" height="52" class="ex7n" fill="#16392a" stroke="#72e0a4"/><text class="ex7t" x="635" y="102">Leaf B1</text><rect x="715" y="72" width="120" height="52" class="ex7n" fill="#16392a" stroke="#72e0a4"/><text class="ex7t" x="775" y="102">Leaf B2</text><rect x="575" y="165" width="260" height="55" class="ex7n" fill="#17344d" stroke="#63d8ff"/><text class="ex7t" x="705" y="189">Spine pair B</text><text class="ex7s" x="705" y="207">Underlay / VXLAN EVPN local</text><path d="M635 124V165M775 124V165" fill="none" stroke="#63d8ff" stroke-width="2.3"/>
<rect x="280" y="330" width="340" height="72" class="ex7n" fill="#30233a" stroke="#c6a6ff"/><text class="ex7t" x="450" y="359">Interconnexion DCI</text><text class="ex7s" x="450" y="381">Border Leaf · policy · routage · sécurité</text><g class="ex7p"><path d="M215 220L335 330"/><path d="M705 220L565 330"/></g><text class="ex7s" x="450" y="432">Le DCI exige un modèle explicite : L3VPN/VRF, extension L2, EVPN Multi-Site ou autre design supporté.</text></svg></div>

Étendre un domaine L2 à travers plusieurs sites peut simplifier certains déplacements, mais agrandit le domaine de panne et augmente l’impact des boucles, du BUM et de problèmes de mobilité. Lorsque l’application le permet, privilégier des frontières L3 plus nettes et une dépendance inter-site explicite. La continuité applicative ne doit pas reposer uniquement sur la persistance d’un VLAN étendu.

### 6.4 Résilience inter-site et split brain

Un lien DCI perdu peut provoquer une partition : les sites continuent à fonctionner localement mais ne se joignent plus. La conception doit définir ce qui reste autorisé, où se trouvent les passerelles et les services d’état, comment le DNS, le stockage et les bases de données se comportent et qui décide de la reprise. Le réseau ne peut pas, à lui seul, garantir la cohérence applicative ou empêcher le split-brain d’un cluster.

Les tests doivent couvrir la perte d’une seule liaison, de tous les liens d’un site, d’un Border Leaf, du control plane EVPN inter-site, d’une route externe et de la connectivité vers les services partagés. Les objectifs de RTO/RPO sont des exigences applicatives distinctes des temps de convergence réseau.


## 7. Dimensionnement, surabonnement et capacité N−1

### 7.1 Calcul de base

Le rapport de surabonnement au niveau d’un Leaf peut être approché par :

\[
R_{surabonnement}=\frac{\text{débit descendant agrégé}}{\text{débit montant agrégé}}
\]

Exemple purement illustratif : 32 ports serveurs à 25 Gb/s fournissent 800 Gb/s nominaux descendants. Si le Leaf a 8 uplinks à 100 Gb/s, le débit montant agrégé nominal vaut aussi 800 Gb/s, soit 1:1 avant toute autre contrainte. Mais ce calcul ne dit pas qu’un ASIC peut traiter simultanément tous les paquets au débit minimum, ni que les chemins ont assez de capacité au-delà du Leaf, ni que chaque flux sera réparti uniformément.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 410" width="100%" height="auto" role="img" aria-label="Dimensionnement d’une fabric : capacité descendante et montante, calcul de surabonnement et test N moins un">
<style>.ex6t{font:700 15px system-ui,sans-serif;fill:#f1f6ff;text-anchor:middle}.ex6s{font:12.5px system-ui,sans-serif;fill:#c2cedd;text-anchor:middle}.ex6n{stroke-width:2;rx:10}</style>
<rect x="25" y="25" width="265" height="165" rx="14" fill="#11283a" stroke="#63d8ff" stroke-width="2"/><text class="ex6t" x="157" y="55">Ports serveurs</text><text class="ex6s" x="157" y="82">32 × 25 Gb/s</text><text class="ex6t" x="157" y="108">800 Gb/s nominal</text><text class="ex6s" x="157" y="134">Capacité agrégée downlink</text><text class="ex6s" x="157" y="158">Ne suppose pas 100 % simultané</text>
<rect x="318" y="25" width="265" height="165" rx="14" fill="#153c2d" stroke="#72e0a4" stroke-width="2"/><text class="ex6t" x="450" y="55">Uplinks fabric</text><text class="ex6s" x="450" y="82">8 × 100 Gb/s</text><text class="ex6t" x="450" y="108">800 Gb/s nominal</text><text class="ex6s" x="450" y="134">Capacité montante théorique</text><text class="ex6s" x="450" y="158">Rapport brut : 1:1</text>
<rect x="610" y="25" width="265" height="165" rx="14" fill="#30233a" stroke="#c6a6ff" stroke-width="2"/><text class="ex6t" x="742" y="55">Test N−1</text><text class="ex6s" x="742" y="82">Perte d’un Spine / uplink</text><text class="ex6t" x="742" y="108">Capacité restante</text><text class="ex6s" x="742" y="134">Dépend du câblage réel</text><text class="ex6s" x="742" y="158">et des chemins admissibles</text>
<path d="M290 110H318" fill="none" stroke="#63d8ff" stroke-width="2.4"/><path d="M583 110H610" fill="none" stroke="#63d8ff" stroke-width="2.4"/>
<rect x="60" y="235" width="780" height="130" rx="14" fill="#111a27" stroke="#43566b" stroke-width="1.5"/><text class="ex6t" x="450" y="267">Attention à la différence entre ratio nominal et capacité garantie</text><text class="ex6s" x="450" y="295">Le débit utilisable dépend de l’ECMP, des hachages, des buffers, des oversubscriptions aval</text><text class="ex6s" x="450" y="317">et des pannes simultanées plausibles. Mesurer les hotspots par port et par flux.</text><text class="ex6s" x="450" y="340">Concevoir selon un scénario d’échec explicite, pas seulement selon le débit agrégé.</text></svg></div>

### 7.2 Calcul après panne

Il faut recalculer la capacité en retirant les ressources d’un scénario N−1 explicite. Si un Leaf dispose de 8 uplinks identiques et perd un uplink à 100 Gb/s, la capacité nominale restante est de 700 Gb/s, avant de considérer les limites de l’ASIC et les destinations. Si la panne concerne un Spine qui porte un lien par Leaf, la perte de capacité dépend de la distribution et du débit des uplinks concernés. Ce n’est pas toujours égal à une fraction simple du débit agrégé, notamment si des liens sont de vitesses différentes ou si le hachage se rééquilibre mal.

Un design qui promet 1:1 en fonctionnement normal mais surcharge un lien en cas de panne n’est pas nécessairement erroné ; il doit néanmoins documenter l’objectif. Par exemple : perte unique d’un Spine tolérée avec dégradation de débit mais sans saturation prolongée, ou débit garanti minimal après la panne. Définir le comportement acceptable évite de confondre redondance de connectivité et redondance de capacité.

### 7.3 ECMP et polarisation des flux

ECMP distribue les flux au moyen d’un hachage, généralement fondé sur des champs des en-têtes. Il répartit mieux un grand nombre de flux diversifiés que quelques flux massifs. Un seul flux peut rester limité à un seul chemin et ne pas utiliser la bande passante de plusieurs Spine. Les résultats dépendent de l’entropie, du hachage, du nombre de chemins, des champs disponibles et parfois des mécanismes de re-hachage.

La polarisation survient lorsque des hachages corrélés dirigent trop de flux sur la même branche. Mesurer les compteurs par lien, pas seulement l’utilisation agrégée du fabric. Une moyenne de 35 % peut masquer un uplink à 95 % et d’autres à 10 %. Rééquilibrer en ajoutant des chemins ou en modifiant des hachages doit faire l’objet d’un test de convergence et de stabilité.

### 7.4 Buffers, microbursts et congestion

La moyenne à une minute ne révèle pas toujours les microbursts. Des sources multiples peuvent envoyer un pic bref vers un seul port egress, provoquer un remplissage de buffer, de la mise en file d’attente, des drops ou une latence élevée. Examiner les compteurs d’egress drops, de tail drops, de WRED/ECN, de pause Ethernet et de saturation par classe de trafic selon ce que la plateforme expose.

Dans les environnements RoCE/RDMA, la QoS et la gestion de congestion exigent un design spécifique, avec des recommandations de la plateforme et tests adaptés. PFC peut éviter certaines pertes sur des classes déterminées, mais une pause mal conçue ou propagée peut provoquer des effets de head-of-line blocking, voire des congestion spreads. Il ne faut pas activer une configuration « lossless » par défaut sans comprendre les classes, les buffers, le contrôle de congestion et l’isolation des trafics.

### 7.5 Ressources matérielles autres que le débit

Les limites de production peuvent être les tables MAC, les préfixes IPv4/IPv6, les routes EVPN, les groupes ECMP, les ACL/TCAM, les interfaces tunnel, le nombre de VRF/VNI, les adjacences, les entries de neighbour et les compteurs télémétriques. Les maxima marketing ne sont pas forcément les maxima atteignables simultanément avec toutes les fonctionnalités activées. Construire une matrice de ressources pour le modèle exact de switch, la version logicielle et le profil des fonctionnalités. Prévoir une marge d’évolution au-delà du besoin du jour.

### 7.6 Capacité externe et border leaf

Une fabric interne rapide n’empêche pas la saturation à une frontière Internet, WAN, pare-feu ou DCI. Mesurer les flux north-south et east-west séparément. Dimensionner les border leaf pour la charge normale, les mises à jour de route, la perte d’un équipement et les politiques de sécurité. Un firewall en goulot d’étranglement peut annuler l’avantage d’une fabric avec une grande capacité interne.

### 7.7 Définir des SLO réseau

Choisir des objectifs mesurables : perte maximale tolérée sur une fenêtre, latence p95/p99, temps de convergence après perte de lien ou de Spine, délai d’installation d’une route, utilisation maximum durable d’un egress et taux d’erreur. Fixer les critères en lien avec les applications. Un SLO ne dit pas seulement « disponibilité 99,99 % » ; il décrit aussi le parcours, la fenêtre de mesure et la manière de détecter une violation.


## 8. MTU, encapsulation et fragmentation

### 8.1 Calcul de budget MTU

VXLAN ajoute des en-têtes externes IP/UDP/VXLAN autour de la trame interne. Le réseau de transit doit transporter le paquet encapsulé sans fragmentation indésirable ni drop silencieux. Le surcoût exact dépend des en-têtes externes, du type d’IP utilisé et du niveau Ethernet ; les valeurs de MTU acceptées diffèrent selon les équipements et la sémantique constructeur. Ne pas se limiter à supposer « MTU 9000 partout » : vérifier la taille effective acceptée sur tous les liens du chemin, les interfaces virtuelles, les hyperviseurs et les éventuelles appliances.

### 8.2 Vérification pratique

Tester avec des paquets de taille contrôlée, le bit DF lorsque applicable et des outils supportés. Comparer un petit paquet qui passe et un grand paquet qui échoue, puis isoler le lien ou la frontière où la taille est refusée. Pour IPv6, la gestion de la MTU et des messages ICMPv6 Packet Too Big est importante ; le filtrage aveugle d’ICMP peut casser la découverte de MTU de chemin. Documenter la MTU nominale et la MTU réellement testée.

### 8.3 Symptômes classiques

Un handshake TCP peut réussir tandis que certains transferts restent bloqués. Le ping par défaut passe mais les sauvegardes, les flux de stockage ou les gros transferts échouent. Les compteurs peuvent montrer des drops sans évidence claire au niveau applicatif. Une modification de MTU doit s’appliquer de manière cohérente et progressive ; modifier un seul segment du chemin peut déplacer le point d’échec plutôt que le résoudre.


## 9. Sécurité de la fabric et isolation des tenants

### 9.1 Sécurité par couches

Une segmentation correcte combine plusieurs contrôles : VRF et Route Targets pour l’isolation de routage ; VLAN/VNI pour les segments L2 ; politiques entre segments ; ACL de management ; filtrage des routes ; contrôles de port et segmentation des workloads ; plan d’accès opérateur protégé ; supervision des modifications. Aucun identifiant (VLAN, VNI, VRF ou tenant) n’est à lui seul une garantie de sécurité.

### 9.2 Plan de gestion

Restreindre SSH/HTTPS/API aux réseaux d’administration et aux identités autorisées. Utiliser AAA centralisé avec un compte de secours limité, des rôles à privilèges minimaux, une rotation des secrets, des clés et certificats gérés, ainsi que l’enregistrement d’audit. Le plan de gestion hors bande doit rester accessible quand le plan de données principal est défaillant. Les interfaces de management ne doivent pas exposer des services inutiles aux réseaux de workloads.

### 9.3 Contrôle du routage

Filtrer les préfixes reçus et annoncés, utiliser des politiques de communauté explicites, limiter les routes et vérifier les sessions. Une annonce accidentelle de route par défaut, d’agrégat trop large ou d’un préfixe d’administration peut causer une panne ou une fuite. Un contrôle de préfixe (« prefix limit ») peut atténuer une explosion de routes, mais il faut définir la réaction au dépassement et alerter avant la limite.

### 9.4 Menaces overlay

Risques à évaluer : mauvais import de Route Target, VNI dupliqué au mauvais périmètre, endpoint spoofing, MAC move anormal, annonce BGP malveillante ou erronée, configuration API non autorisée, désaccord de control plane, fuite inter-VRF, service de transit contourné et attaque du plan de management. Les fonctions de contrôle d’accès et d’anti-spoofing disponibles dépendent de la plateforme et du point où le trafic est contrôlé.

### 9.5 Tests négatifs

Chaque règle d’isolation doit être testée dans les deux sens. Vérifier qu’un tenant autorisé rejoint son service attendu et qu’un tenant non autorisé ne peut pas joindre la même destination. Vérifier également IPv6 lorsque le réseau le supporte ; une politique conçue uniquement autour d’IPv4 peut laisser un chemin IPv6 inattendu. Confirmer les routes et les policies réellement installées plutôt que de se fier à la seule présence d’un objet de configuration.

### 9.6 Mise à jour et gestion des vulnérabilités

Maintenir un inventaire de matériels, versions, licences et composants logiciels. Évaluer les avis de sécurité du constructeur et la compatibilité du train logiciel avec le matériel. Les upgrades doivent être testés sur une maquette ou un sous-ensemble représentatif, avec vérification des protocoles, des fonctions hardware, de la télémétrie et de la capacité. Définir une procédure de retour arrière sachant que certaines mises à niveau modifient les formats de base de données ou empêchent une réversion directe.


## 10. Automatisation comme chaîne de compilation et de validation

### 10.1 Source de vérité et modèle de données

Une automatisation sûre commence par des données déclaratives validées : nœuds, rôles, modèles hardware, ports, voisins, câbles, liens, adresses, ASN, loopbacks, VLAN/VNI, VRF, RT, gateway, tenants et politiques. Le système doit refuser un inventaire incomplet ou contradictoire avant de générer une configuration. Le nom du voisin et la vitesse du port doivent correspondre aux deux extrémités du lien.

Une source de vérité ne doit pas seulement stocker les valeurs : elle exprime aussi des invariants. Exemples : chaque Leaf non isolé a au moins deux chemins montants ; un VNI ne peut pas se trouver dans des mappings incompatibles ; une route externe n’est annoncée que depuis des Border Leaf dédiés ; tout préfixe d’une VRF est dans un registre de propriétaire ; un port access n’a pas de politique trunk par défaut.

### 10.2 Étapes de déploiement

Séparer au minimum : validation de données, rendu de configuration, linting/compilation, comparaison diff, pré-validation, application, vérification post-change et détection de dérive. Toute étape échouée doit arrêter le pipeline avant les changements risqués. Les modifications en production doivent être par lots, avec une canari représentative et un arrêt automatique si les critères se dégradent.

Un changement réseau n’est pas idempotent parce qu’un script se termine sans erreur. L’idempotence exige qu’une seconde exécution converge vers le même état, sans ajouter des objets dupliqués ou provoquer des transitions inattendues. L’état désiré doit être comparé à l’état effectif, et les différences non gérées doivent être déclarées.

### 10.3 Exemple de modèle déclaratif

```yaml
fabric:
  name: dc-a
  underlay:
    protocol: ebgp
    mtu: 9216          # valeur illustrative : vérifier la plateforme
  spines:
    - name: spine-01
      asn: 65001
    - name: spine-02
      asn: 65002
  leaves:
    - name: leaf-01
      asn: 65101
      uplinks:
        - peer: spine-01
          local_interface: Ethernet1/49
          peer_interface: Ethernet1/1
        - peer: spine-02
          local_interface: Ethernet1/50
          peer_interface: Ethernet1/1
```

Cet extrait est uniquement un schéma de données. Il ne fournit ni syntaxe d’équipement ni recette prête à appliquer. Pour être exploitable, le modèle doit préciser les IP de chaque extrémité, les vitesses attendues, le voisinage autorisé, les familles BGP, les politiques et les tests. Un validateur doit notamment détecter si deux liens ont le même sous-réseau, si une interface est assignée deux fois ou si un équipement manque dans l’inventaire.

### 10.4 Contrôles automatiques recommandés

- syntaxe et schéma : champs requis, types, valeurs permises ;
- intégrité référentielle : voisins qui existent, interfaces uniques, deux extrémités concordantes ;
- unicité : Router ID, VNI dans la portée définie, adresse IP, ASN selon politique ;
- cohérence de routage : préfixes autorisés, export/import, next-hop ;
- capacité : compte des ports, chemins disponibles, ratio et ressources estimées ;
- sécurité : aucune politique permissive accidentelle, aucune route de défaut inattendue ;
- tests de topologie : connectivité Leaf–Spine, chemin alternatif, scénario N−1 ;
- déploiement : diff court, fenêtres de changement, garde-fous et rollback connu.

### 10.5 API et contrôleurs

Les contrôleurs de fabric peuvent offrir API REST, modèles déclaratifs ou intégration à une source de vérité. L’API n’est pas une garantie que l’opération sera atomique ou qu’elle aura abouti dans le plan de données. Respecter les codes de retour, les états asynchrones, les limites de débit, l’authentification et la version du schéma. Après un `POST` ou `PATCH`, interroger l’état effectif et la santé de la fabric. Stocker les secrets dans un coffre, jamais dans les fichiers de configuration ou le contrôle de versions.

### 10.6 GitOps et dérive

Le dépôt de configuration doit conserver une trace du changement, de l’auteur, de la raison, des approbations, des tests et du résultat. La dérive peut être légitime (urgence) ou accidentelle ; le système ne doit pas écraser immédiatement un état manuel sans diagnostic. Prévoir un workflow d’urgence documenté, puis une réconciliation avec la source de vérité. Le commit ne vaut pas validation opérationnelle.


## 11. Observabilité : ne pas confondre état de contrôle et expérience applicative

### 11.1 Les quatre niveaux de vérification

1. **Physique :** état des interfaces, optiques, erreurs CRC, pertes de signal, température, alimentation.
2. **Routage :** adjacences, sessions BGP, routes reçues/acceptées, next-hops, ECMP et convergence.
3. **Forwarding matériel :** groupe de next-hops, tables MAC/ARP/ND, compteurs de drops, buffers, ACL et ressources ASIC.
4. **Service :** probes de connectivité, latence, perte, transaction applicative et métriques par tenant.

Une session BGP « Established » n’assure pas que le bon trafic circule. Un ping vers la loopback du voisin n’assure pas que le VNI, la politique ou la route retour d’un tenant fonctionne. Il faut des tests représentatifs de bout en bout et une capacité à localiser le premier point où l’état diverge.

### 11.2 Métriques et télémétrie

Collecter les métriques à la bonne granularité et conserver des compteurs de base avant incident. Les signaux utiles incluent utilisation par interface et classe, paquets perdus, microbursts si l’équipement les mesure, latence, erreurs physiques, état BGP, nombre de routes, nombre d’endpoints MAC/IP, événements de mobilité, usage de buffers, drops de lookup ou de ressources matérielles.

Éviter les cardinalités illimitées : une métrique par MAC/flow peut faire exploser le système de monitoring. Définir quelles séries sont agrégées en continu, lesquelles sont accessibles à la demande et combien de temps conserver les données fines. Horloges synchronisées et horodatages cohérents sont indispensables pour corréler le plan de contrôle, les switches, les hôtes et les applications.

### 11.3 Alarmes basées sur le symptôme

Un état de port down peut être utile, mais une alarme basée sur le symptôme applicatif apporte une autre dimension : perte de trafic entre deux zones, latence p99 dégradée, échec de transaction ou ratio de drops anormal. Combiner signaux réseau et probes applicatives permet de distinguer une panne de transport, une congestion localisée et un service applicatif en panne.

Éviter les seuils universels appliqués partout. Un egress à 85 % peut être normal dans un environnement stable avec un bon SLO, mais dangereux si les bursts et la latence sont déjà élevés. Construire des seuils à partir des objectifs du service, du comportement historique et des mesures par port/classe.

### 11.4 Runbook de collecte

Pour un incident, réunir : heure de début et fuseau ; zone touchée ; endpoints et préfixes ; modifications récentes ; état des liens ; logs de sessions ; routes RIB et FIB ; tables MAC/ARP/ND ; compteurs d’interface et de drops ; MTU ; politiques impliquées ; capture représentative si autorisée ; résultat d’un test de retour. Préserver les données avant de redémarrer un équipement ou de vider les compteurs.

### 11.5 Plan de données et symptômes asymétriques

Un chemin aller qui fonctionne et un retour qui échoue orientent vers une asymétrie de routage, une ACL directionnelle, un état de pare-feu, un ECMP différent, un MTU différent ou un problème de service. Examiner le chemin dans les deux sens. Dans des réseaux avec équipements stateful, l’asymétrie peut casser les sessions même quand IP reachability semble exister.


## 12. Convergence et résilience : raisonner sur une chaîne d’événements

### 12.1 Décomposer le temps de rétablissement

Le temps de convergence de bout en bout peut être décomposé conceptuellement : temps de détection + propagation du changement de contrôle + calcul/sélection de route + programmation du forwarding + éventuel rééquilibrage et récupération de l’application. Les composantes se chevauchent parfois ; le résultat doit être mesuré de bout en bout. Un timer très agressif peut réduire une partie du délai mais augmenter le risque de faux positifs, de churn et de charge du control plane.

BFD sert à détecter rapidement une défaillance du chemin entre équipements, indépendamment du protocole de routage. Les valeurs et le support hardware comptent. Quelques millisecondes annoncées dans une configuration ne garantissent pas une récupération applicative de quelques millisecondes. Tester sur le matériel et à l’échelle de la fabric, en incluant les effets de CPU, les tempêtes de sessions et la programmation des groupes ECMP.

### 12.2 Pré-calcul et convergence rapide

Certains systèmes maintiennent des chemins de secours ou des mécanismes de fast reroute. La possibilité de préinstaller une alternative dépend du protocole, de la topologie, des attributs et du support du système. La bascule peut être rapide si un next-hop déjà valide est activé dans l’ASIC ; elle sera différente si un nouveau calcul complet et une programmation de la FIB sont nécessaires.

Ne pas supposer que le simple fait d’avoir deux chemins BGP visibles signifie que le hardware basculera instantanément. Vérifier le groupe ECMP programmé, le comportement en perte de lien, le traitement d’un voisin qui reste « up » alors que le dataplane ne forwarde plus, et le mécanisme qui détecte une panne unidirectionnelle.

### 12.3 Tester différents types de panne

- shutdown administrativement un seul lien ;
- perte physique d’un transceiver ;
- panne d’un Spine complet ;
- blackhole silencieux où le lien reste up ;
- retrait d’une annonce de loopback ;
- interruption d’un RR ;
- suppression d’une route EVPN ;
- saturation d’un port egress ;
- perte d’un Border Leaf ;
- partition entre deux sites.

Chaque injection représente un mécanisme différent. Une panne de lien détectée par la couche physique ne prédit pas le comportement lors d’un blackhole où le signal reste présent. Pour chaque test, mesurer perte maximale, durée de perturbation, routes retirées, chemins de remplacement, saturation du chemin résiduel et temps de retour à l’état normal.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 430" width="100%" height="auto" role="img" aria-label="Panne d’un spine dans une fabric redondante : un chemin est retiré et le trafic continue via les chemins restants si capacité et convergence sont adéquates">
<defs><marker id="ex5arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#63d8ff"/></marker></defs><style>.ex5t{font:700 15px system-ui,sans-serif;fill:#f1f6ff;text-anchor:middle}.ex5s{font:12px system-ui,sans-serif;fill:#c1cfde;text-anchor:middle}.ex5n{stroke-width:2;rx:10}.ex5ok{fill:none;stroke:#63d8ff;stroke-width:2.7;stroke-dasharray:7 6;marker-end:url(#ex5arr)}.ex5ok path{animation:ex5d 2.6s linear infinite}.ex5bad{fill:none;stroke:#ff7e85;stroke-width:2.8;stroke-dasharray:7 6;opacity:.85}.ex5x{stroke:#ff7e85;stroke-width:4;stroke-linecap:round}@keyframes ex5d{to{stroke-dashoffset:-26}}@media(prefers-reduced-motion:reduce){.ex5ok path{animation:none}}</style>
<rect x="30" y="25" width="840" height="80" rx="12" fill="#13202e" stroke="#3f556b"/><text class="ex5t" x="450" y="54">Événement : perte de SPINE-2 ou d’un de ses liens</text><text class="ex5s" x="450" y="79">Détection → retrait de next-hop / recalcul → réinstallation du forwarding</text>
<rect x="60" y="145" width="170" height="64" class="ex5n" fill="#153c2d" stroke="#72e0a4"/><text class="ex5t" x="145" y="173">Leaf source</text><text class="ex5s" x="145" y="193">Flux vers Leaf B</text>
<rect x="345" y="145" width="180" height="64" class="ex5n" fill="#17344d" stroke="#63d8ff"/><text class="ex5t" x="435" y="173">SPINE-1</text><text class="ex5s" x="435" y="193">Chemin actif</text>
<rect x="345" y="250" width="180" height="64" class="ex5n" fill="#3d1e28" stroke="#ff7e85"/><text class="ex5t" x="435" y="278">SPINE-2</text><text class="ex5s" x="435" y="298">Panne / indisponible</text>
<rect x="675" y="145" width="170" height="64" class="ex5n" fill="#153c2d" stroke="#72e0a4"/><text class="ex5t" x="760" y="173">Leaf destination</text><text class="ex5s" x="760" y="193">Reçoit le flux</text>
<g class="ex5ok"><path d="M230 166L345 166"/><path d="M525 166L675 166"/></g><path class="ex5bad" d="M230 193L345 278L675 193"/><path class="ex5x" d="M405 262L465 302M465 262L405 302"/>
<rect x="80" y="350" width="740" height="53" rx="10" fill="#10271f" stroke="#347b58"/><text class="ex5s" x="450" y="372">Le basculement n’est pas « magique » : il dépend de la détection, des timers, du FIB/ASIC,</text><text class="ex5s" x="450" y="390">de la capacité restante et de l’absence de panne commune.</text></svg></div>

### 12.4 Flap, dampening et stabilité

Une interface ou un voisin qui monte et descend peut déclencher une succession de recalculs, retraits de routes et événements de contrôle. La solution durable est d’identifier la cause physique ou logicielle. Toute fonction de dampening ou de suppression de routes doit être évaluée soigneusement : elle peut améliorer la stabilité dans certains contextes, mais prolonger l’indisponibilité d’une route légitime. Mesurer l’impact au lieu de traiter le flap uniquement comme du bruit de journalisation.

### 12.5 Plan de test reproductible

Un test de résilience indique le point de départ, les flux injectés, les critères de réussite, la méthode d’observation, la panne injectée, la méthode de restauration et le résultat. Tester la même chose plusieurs fois sur une fabric stable. Une seule exécution réussie ne suffit pas si les temps de convergence varient selon l’état initial ou la taille des tables.


## 13. Congestion, QoS et fabric sensible à la latence

### 13.1 Le débit n’est pas l’unique objectif

Un datacenter peut être limité par la latence de queue, les pertes, les bursts ou les interactions de flux. Les applications requièrent des profils différents : stockage, bases de données, sauvegarde, trafic d’API, réplication, calcul distribué et flux RDMA. Appliquer une QoS uniforme sans classifier les besoins risque d’aggraver le partage de ressources.

### 13.2 Files d’attente et classes de trafic

Documenter comment les DSCP/CoS sont mappés sur les classes d’entrée, files egress et mécanismes de scheduling. Vérifier les règles aux points d’entrée, aux Leaf et au raccordement externe. Une valeur DSCP seule ne force pas un traitement garanti si l’équipement réécrit ou ignore ce marquage. Protéger la classification contre le marquage arbitraire d’un endpoint non fiable.

### 13.3 ECN, PFC et RoCE

Pour le trafic RDMA, les choix de congestion control, ECN, PFC et buffer doivent suivre la conception supportée du constructeur et les besoins applicatifs. PFC est un mécanisme de pause par priorité qui peut créer des effets secondaires s’il se propage de manière inattendue. Le but n’est pas d’« activer PFC partout », mais d’éviter pertes et congestion persistante avec une classification précise, un contrôle d’admission si approprié et une supervision des pauses.

Dans la validation, injecter les flux ciblés, mesurer les drops, marques ECN, pauses, latences p99 et effets sur les classes non concernées. Les tests doivent comprendre une surcharge contrôlée afin de s’assurer qu’une classe lossless ne paralyse pas les classes best-effort.

### 13.4 Microbursts

Utiliser des métriques de courte période et les fonctionnalités de buffer occupancy disponibles. Une mesure moyenne lisse peut manquer un burst court qui remplit une queue. Si le matériel ne peut pas exposer la granularité requise, le rapport d’observabilité doit clairement mentionner cette limite au lieu de présenter l’absence de métrique comme l’absence de congestion.


## 14. Gestion de configuration, mises à jour et changement sûr

### 14.1 Avant tout changement

Établir le service impacté, l’état de référence, le propriétaire de l’application, les dépendances, les critères d’acceptation, les risques, la fenêtre et le rollback. Sauvegarder l’état des configurations et les données qui permettent de comparer avant/après. Vérifier que l’accès hors bande marche et qu’une équipe peut intervenir sans utiliser uniquement le réseau modifié.

### 14.2 Déploiement par canari

Un canari doit être représentatif, mais assez isolé pour limiter l’impact. Déployer un petit groupe de Leaf ou une zone de workload, comparer les sessions, routes, ressources et probes, puis élargir si les critères restent corrects. Une modification qui ne concerne qu’une partie des devices peut tout de même affecter l’échange de routes global : la canarisation doit tester ce risque de blast radius.

### 14.3 Mise à niveau logicielle

Lire les notes de version, matrices de compatibilité, avis de sécurité, limitations connues, procédures de mise à niveau et de retour arrière. Vérifier les protocoles de contrôle, les fonctions ASIC, les APIs, la télémétrie, les automates et les licences après mise à niveau. Procéder par lots avec une séquence qui conserve assez de capacité pendant le redémarrage des équipements.

Ne pas mélanger sans test une mise à niveau logicielle, un changement de routage, la modification de MTU et le remaniement des VNI dans une même fenêtre. Si plusieurs changements sont indispensables, séparer les critères et prévoir des points de décision explicites.

### 14.4 Rollback réel

Un rollback n’est pas seulement le commit précédent. Il doit prendre en compte les dépendances déjà créées, les migrations de schéma, les routes apprises, les endpoints déplacés et les versions qui ne sont pas compatibles en retour. Tester la restauration dans un laboratoire représentatif. Définir les indicateurs qui déclenchent le rollback, son propriétaire et la situation où un rollback serait plus dangereux que le maintien de l’état actuel.

### 14.5 Migration d’un réseau traditionnel vers Spine/Leaf

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 390" width="100%" height="auto" role="img" aria-label="Migration progressive d’un réseau traditionnel vers une fabric Spine Leaf : inventaire, pilote, coexistence contrôlée, migration puis retrait de l’ancien réseau">
<defs><marker id="ex8arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#63d8ff"/></marker></defs><style>.ex8t{font:700 14px system-ui,sans-serif;fill:#f1f6ff;text-anchor:middle}.ex8s{font:12px system-ui,sans-serif;fill:#c1cedd;text-anchor:middle}.ex8n{stroke-width:2;rx:10}.ex8p{fill:none;stroke:#63d8ff;stroke-width:2.4;stroke-dasharray:7 6;marker-end:url(#ex8arr)}.ex8p path{animation:ex8d 2.6s linear infinite}@keyframes ex8d{to{stroke-dashoffset:-26}}@media(prefers-reduced-motion:reduce){.ex8p path{animation:none}}</style>
<g><rect x="25" y="45" width="150" height="98" class="ex8n" fill="#172e45" stroke="#63d8ff"/><text class="ex8t" x="100" y="74">1. Inventaire</text><text class="ex8s" x="100" y="97">Flux, VLAN,</text><text class="ex8s" x="100" y="116">dépendances</text><rect x="205" y="45" width="150" height="98" class="ex8n" fill="#172e45" stroke="#63d8ff"/><text class="ex8t" x="280" y="74">2. Pilote</text><text class="ex8s" x="280" y="97">Lab + tests</text><text class="ex8s" x="280" y="116">de panne</text><rect x="385" y="45" width="150" height="98" class="ex8n" fill="#30233a" stroke="#c6a6ff"/><text class="ex8t" x="460" y="74">3. Coexistence</text><text class="ex8s" x="460" y="97">Routage/filtrage</text><text class="ex8s" x="460" y="116">contrôlés</text><rect x="565" y="45" width="150" height="98" class="ex8n" fill="#153c2d" stroke="#72e0a4"/><text class="ex8t" x="640" y="74">4. Migration</text><text class="ex8s" x="640" y="97">Par lots</text><text class="ex8s" x="640" y="116">et validations</text><rect x="745" y="45" width="130" height="98" class="ex8n" fill="#153c2d" stroke="#72e0a4"/><text class="ex8t" x="810" y="74">5. Retrait</text><text class="ex8s" x="810" y="97">Ancienne infra</text><text class="ex8s" x="810" y="116">après preuve</text></g>
<g class="ex8p"><path d="M175 94H205"/><path d="M355 94H385"/><path d="M535 94H565"/><path d="M715 94H745"/></g>
<rect x="50" y="205" width="800" height="130" rx="14" fill="#111b29" stroke="#43566b"/><text class="ex8t" x="450" y="236">Garde-fous obligatoires</text><text class="ex8s" x="450" y="263">Plan de retour arrière testé · fenêtres de changement · critères de succès mesurables</text><text class="ex8s" x="450" y="286">Pas de migration simultanée de tous les gateways, VLAN et liens de transit</text><text class="ex8s" x="450" y="309">Un seul changement dominant à la fois, avec observabilité avant / pendant / après</text></svg></div>

Démarrer par la cartographie des VLAN, adresses, gateways, dépendances L2, services de sécurité, règles de firewall, flux externes, DNS/DHCP, outils de monitoring et applications sensibles. Les VLAN « inconnus » ne doivent pas être étendus par défaut vers la nouvelle fabric. Utiliser des lots applicatifs cohérents, contrôler le routage de coexistence et éviter les boucles L2 pendant la transition. Un plan de retour arrière doit indiquer comment restaurer les gateways et chemins, pas seulement comment remettre un câble.

### 14.6 Communication et post-mortem

Un changement réussi produit une preuve : diff, tests exécutés, mesures avant/après et décision d’acceptation. Un incident est documenté sans blâme, en séparant facteur déclenchant, conditions latentes, détection, impact, rétablissement et actions préventives. Transformer les leçons en contrôles automatiques lorsque possible.


## 15. Méthode de dépannage avancé

### 15.1 Construire des hypothèses falsifiables

Un diagnostic expert ne commence pas par un changement au hasard. Définir les symptômes précis : qui ne peut pas parler à qui, dans quel sens, depuis quand, pour quelles tailles de paquet et depuis quel emplacement. Formuler plusieurs hypothèses qui peuvent être confirmées ou éliminées par une commande ou une mesure. Préserver les preuves avant de vider les compteurs ou redémarrer un équipement.

### 15.2 Arbre de diagnostic

**Étape A — physique.** Interface opérationnelle ? erreurs CRC ? optique conforme ? vitesse et négociation attendues ? drops de buffers ?

**Étape B — reachability underlay.** Adjacences stables ? loopbacks dans la RIB ? next-hops résolus ? ECMP conforme ? MTU de lien correcte ?

**Étape C — control plane overlay.** Famille EVPN active ? routes Type 2/3/5 attendues reçues ? Route Targets corrects ? route importée dans le bon contexte ? MAC mobility ou flapping ?

**Étape D — forwarding.** Table MAC et voisins ARP/ND ? tunnel VTEP installé ? ACL/TCAM ? programmation du groupe de next-hops ? compteurs de drop ?

**Étape E — service.** Gateway et route retour ? DNS/DHCP ? politique de firewall ? service intermédiaire ? test applicatif et métriques ?

### 15.3 RIB vs FIB vs endpoint

Si la route est absente du RIB, regarder le protocole, les politiques et les attributs. Si elle est dans le RIB mais absente du FIB, regarder la résolution, les limites de ressources, l’installation hardware et les messages de programmation. Si la route est installée mais la trame est abandonnée, regarder l’ACL, l’encapsulation, le MTU, les compteurs egress et la destination réelle. Si le trafic arrive au serveur mais la session échoue, vérifier la route retour, le firewall stateful et l’application.

### 15.4 Exemple : un seul VLAN / VNI échoue

Si les autres VNIs fonctionnent, l’underlay global est moins suspect, sans être automatiquement innocent. Comparer une instance qui marche avec celle qui échoue : VLAN↔VNI, SVI/gateway, VRF, RT import/export, route EVPN, membership du VTEP, ACL, MTU et ressources. Vérifier qu’aucune configuration de mapping locale n’est divergente sur un seul Leaf. Le « fonctionne ailleurs » est un indice, pas une preuve.

### 15.5 Exemple : panne après perte d’un Spine

Confirmer l’événement physique et l’étendue réelle. Vérifier le retrait de la route/next-hop, la taille du groupe ECMP restant, l’occupation des uplinks survivants et les drops pendant le rééquilibrage. Si certaines applications échouent alors que d’autres restent saines, comparer leurs chemins, tailles de paquets, VNI, classes QoS et destinations. Rechercher une capacité N−1 sous-estimée, un groupe ECMP mal programmé, une politique BGP asymétrique ou un chemin partagé caché.

### 15.6 Exemple : control plane sain, data plane cassé

Les sessions BGP sont établies, les routes EVPN existent, mais les paquets n’arrivent pas. Vérifier la FIB, les entrées matérielles, les compteurs de tunnel, le MTU, la résolution de next-hop et les ACL. Une table de contrôle saine confirme seulement qu’une partie de la chaîne fonctionne. La preuve finale doit venir d’un paquet représentatif observé le long du chemin.

### 15.7 Quand escalader

Fournir un dossier qui contient une topologie, versions exactes, modèles hardware, chronologie, sortie des commandes supportées, compteurs avant/après, paquet représentatif, configuration des zones concernées et test minimal reproductible. Protéger les secrets et données sensibles. Éviter d’envoyer seulement un fichier de configuration géant sans indiquer le symptôme, le chemin et la différence attendue.


## 16. Atelier expert : concevoir et valider une fabric multi-tenant

### 16.1 Cahier des charges

Construire un datacenter composé de 4 Spine, 16 Leaf d’accès et 2 Border Leaf. Les workloads sont séparés en trois environnements : Web, Application et Base de données. Les contraintes sont :

- un minimum de chemins de transit défini par le design ;
- un scénario de perte d’un Spine sans perte complète de service ;
- isolation des environnements par VRF et politique ;
- overlay VXLAN/EVPN pour l’extension des segments autorisés ;
- accès externe contrôlé via les Border Leaf ;
- capacité post-panne calculée et validée ;
- automatisation du plan d’adressage et des associations VNI ;
- monitoring des routes, drops, latence et événements de mobilité.

### 16.2 Livrables avant configuration

1. Diagramme physique et logique ;
2. matrice des ports et des liens ;
3. plan d’adressage IP/loopback ;
4. choix underlay avec justification ;
5. ASN, peer groups et filtres ;
6. registre VRF/VNI/RT et gateway ;
7. modèle de routage externe et route leaking ;
8. matrice des flux autorisés et interdits ;
9. calcul de capacité normal/N−1 ;
10. plan d’essais et rollback.

### 16.3 Modèle logique de segmentation

Exemple pédagogique :

| Zone | VRF | Réseaux indicatifs | Politique attendue |
|---|---|---|---|
| Web | `VRF-WEB` | `10.10.10.0/24` | Web vers application seulement sur ports explicitement admis |
| Application | `VRF-APP` | `10.10.20.0/24` | App vers DB sur les ports nécessaires ; pas d’accès admin large |
| Base de données | `VRF-DB` | `10.10.30.0/24` | Entrées depuis App ; gestion depuis un réseau d’administration |
| Management | `VRF-MGMT` ou réseau OOB | plan réservé distinct | accès privilégié et journalisé |

Ces préfixes et noms sont fictifs. Les règles de flux doivent utiliser des ports et des protocoles définis par les exigences de l’application, pas une hypothèse implicite du modèle. Le routage entre VRF doit être explicitement autorisé par la topologie de services ou la méthode prise en charge ; ne pas relier les VRF simplement pour faciliter le ping.

### 16.4 Cas de test

- un hôte Web joint son gateway et le service applicatif autorisé ;
- le même hôte ne joint pas directement la base si la politique interdit ce chemin ;
- une source d’un tenant distinct ne peut pas joindre un endpoint DB ;
- un flux inter-Leaf fonctionne après déplacement contrôlé d’un endpoint ;
- la MAC et la route EVPN apparaissent au bon endroit et se retirent après déconnexion ;
- la perte d’un lien et d’un Spine est testée séparément ;
- une route externe non autorisée est refusée ;
- les paquets proche du MTU maximal fonctionnent dans les deux sens ;
- la saturation d’un egress déclenche l’alarme attendue ;
- un changement erroné dans l’inventaire est rejeté avant le déploiement.

### 16.5 Critères de réussite

Définir des valeurs numériques liées aux exigences réelles : perte maximale, convergence, latence p95/p99, niveau de drops, nombre de routes et état des sessions. Les critères ne doivent pas être inventés après les tests. Un test est réussi lorsque les mesures et les preuves montrent le comportement prévu, et échoué lorsqu’un comportement important n’est pas mesuré ou reste ambigu.

### 16.6 Rapport final

Le rapport doit contenir : version matérielle et logicielle, source de vérité, modifications appliquées, sorties de vérification, captures de télémétrie, résultats par cas, écarts, risques restants, rollback testé, signatures de validation et date de la prochaine revue de capacité.


## 17. Exploitation quotidienne : contrôles proactifs

Une checklist utile doit être courte dans l’usage quotidien et profonde lorsqu’un signal est anormal. Les contrôles périodiques peuvent couvrir :

- état des interfaces et tendances d’erreurs physiques ;
- disponibilité de tous les chemins attendus et groupes ECMP ;
- santé BGP, routes acceptées et variation anormale du nombre de préfixes ;
- nombre de routes EVPN et endpoints par segment ;
- flapping MAC, événements de mobilité, adjacency churn ;
- ressources hardware, TCAM, tables MAC/ARP/ND et groupes next-hop ;
- capacité par interface et indicateurs de microburst ;
- sauvegarde de configuration, dérive par rapport à la source de vérité ;
- résultats des probes applicatives ;
- statut des certificats, secrets, comptes opérateurs et correctifs de sécurité.

Un rapport de capacité mensuel ou trimestriel devrait comparer la charge actuelle aux seuils prévus à la conception : nombre de Leaf, nombre d’endpoints, préfixes, VNI/VRF, croissance de la consommation de buffers et ports nécessaires. La bonne date d’extension est celle où le risque et le délai d’approvisionnement le justifient, pas seulement quand le premier port est saturé.


## 18. Erreurs de conception expertes à éviter

**Ajouter des Spine sans recalculer la fabric.** Le nombre de ports, les chemins ECMP, la capacité des Leaf et les politiques doivent être revalidés.

**Avoir deux chemins mais une seule capacité réelle.** Le N−1 peut produire une congestion sévère ou mettre tous les flux sur le chemin survivant.

**Confondre route reçue et route utilisée.** RIB, FIB et état réel du dataplane ne sont pas équivalents.

**Supposer qu’EVPN corrige automatiquement une erreur de couche 2.** L’overlay ne rend pas inoffensives les boucles, les erreurs de multihoming ou les politiques de sécurité incorrectes.

**Utiliser Route Targets comme règle de sécurité applicative.** Ils contrôlent l’import/export des routes selon le modèle EVPN, mais ne remplacent pas une politique de flux.

**Déployer un changement global en une seule opération.** Une petite erreur d’inventaire peut affecter tous les Leaf si le pipeline ne contient pas de validations et de canaris.

**Ne tester que la panne du câble.** Un blackhole silencieux, la perte d’un RR, une panne ASIC, la saturation egress ou une route retour incorrecte ont des comportements différents.

**Mesurer seulement l’utilisation moyenne.** Les congestions localisées et les microbursts sont invisibles dans certaines agrégations.

**Utiliser une ancienne procédure EVPN sans vérifier les RFC et la version logicielle.** Les normes évoluent, comme le montre RFC 9746 ; le support dépend aussi du constructeur et de la version.

**Ne pas documenter l’exploitation en mode dégradé.** Le design doit préciser ce que le réseau garantit lors d’une panne, ce qui est sacrifié et quelles équipes doivent être informées.


## 19. Quiz expert avec corrigé

### Questions

1. Pourquoi faut-il mesurer séparément l’état de la RIB, de la FIB et des compteurs matériels ?
2. Quelle différence existe entre le rôle des Spine dans la fabric et celui des Route Reflectors EVPN ?
3. Quelle information transporte typiquement une route EVPN de Type 2 ?
4. Pourquoi un grand nombre de paths ECMP n’implique-t-il pas qu’un flux unique utilise leur débit agrégé ?
5. Quels risques existe-t-il lors d’une extension L2 entre deux sites ?
6. Pourquoi le test d’une perte de lien ne suffit-il pas à prouver la résilience ?
7. Quelles vérifications sont requises lorsqu’une route EVPN est reçue mais le trafic ne circule pas ?
8. Pourquoi le surabonnement calculé à partir du débit nominal ne garantit-il pas la capacité après panne ?
9. Quels contrôles doivent être effectués avant d’appliquer une configuration générée ?
10. Quelle est la limite d’une politique d’import/export EVPN dans la sécurité multi-tenant ?
11. Que faut-il observer pour diagnostiquer un problème de MTU VXLAN ?
12. Pourquoi deux route reflectors ne forment-ils pas nécessairement deux domaines de panne indépendants ?
13. Pourquoi PFC doit-il être conçu à l’échelle des classes et de la topologie plutôt qu’activé uniformément ?
14. Que doit contenir un rollback réellement exploitable ?
15. Quels critères mesurables utiliserez-vous pour valider une panne Spine ?

### Corrigé

1. La RIB décrit la sélection de routes au plan de contrôle ; la FIB décrit l’état de forwarding installé ; les compteurs montrent le comportement réel sur interfaces/ASIC. L’écart localise la panne.
2. Les Spine transportent le trafic du plan de données entre Leaf. Les RR distribuent des routes BGP EVPN et ne sont généralement pas dans le chemin du paquet applicatif.
3. Typiquement une annonce MAC et éventuellement IP associée, avec attributs d’attachement pertinents.
4. Le hachage se fait souvent par flux ; un seul flux utilise généralement un chemin à la fois, et l’entropie peut être faible.
5. Boucles et BUM étendus, plus grande blast radius, latence inter-site, problèmes de mobilité et dépendance à la DCI.
6. Le blackhole silencieux, la perte du control plane, la saturation, la panne matérielle ou un chemin retour défectueux peuvent se comporter différemment.
7. Vérifier import de route, Route Targets, reachability VTEP underlay, VLAN/VNI, MTU, FIB, ACL et compteurs de drops.
8. La perte d’un uplink ou d’un Spine modifie la capacité et le hachage ; les chemins restants peuvent être saturés ou inégalement utilisés.
9. Valider schéma, intégrité des liens, unicité IP/VNI/ID, politiques, capacité, diff, canari et rollback.
10. La politique contrôle l’import/export des routes selon EVPN ; elle ne remplace pas une ACL, une politique d’accès de workload ou un firewall.
11. Comparer paquets de tailles variables dans les deux sens, vérifier les interfaces/chemins du tunnel et s’assurer que les messages nécessaires de découverte MTU ne sont pas bloqués.
12. Ils peuvent partager rack, alimentation, logiciel, source de configuration ou chemin réseau.
13. Le traitement de pause par priorité peut causer blocage en tête de ligne ou propagation de congestion ; les classes, buffers et marquages doivent être cohérents.
14. État précédent sauvegardé, séquence, dépendances, critères de déclenchement, accès OOB, étapes de retour et preuve que cette réversion a été testée.
15. Perte maximale, durée, routes/next-hops retirés, capacité restante, drops, latence et probes applicatives, avec résultats reproductibles.


## 20. Références techniques et méthode de lecture

Les documents normatifs ou de conception doivent être lus pour la question précise qu’ils résolvent. Un RFC définit un protocole ou une procédure ; il ne garantit pas que toutes les plateformes la prennent en charge au même niveau, ni qu’une architecture soit idéale pour tous les environnements.

- **RFC 7938 — Use of BGP for Routing in Large-Scale Data Centers** (RFC informatif, août 2016) : https://www.rfc-editor.org/rfc/rfc7938.html
- **RFC 4271 — A Border Gateway Protocol 4 (BGP-4)** : https://www.rfc-editor.org/rfc/rfc4271.html
- **RFC 5880 — Bidirectional Forwarding Detection (BFD)** : https://www.rfc-editor.org/rfc/rfc5880.html
- **RFC 7432 — BGP MPLS-Based Ethernet VPN** : https://www.rfc-editor.org/rfc/rfc7432.html (document mis à jour par plusieurs RFC ultérieurs ; consulter la page de statut)
- **RFC 8365 — A Network Virtualization Overlay Solution Using EVPN** : https://www.rfc-editor.org/rfc/rfc8365.html (statut et mises à jour à vérifier)
- **RFC 9746 — BGP EVPN Multihoming Extensions for Split-Horizon Filtering** (mars 2025) : https://www.rfc-editor.org/rfc/rfc9746.html
- **Cisco — Nexus 9000 VXLAN BGP EVPN Data Center Fabrics Fundamental Design and Implementation Guide** (mis à jour le 13 juin 2025) : https://www.cisco.com/c/en/us/td/docs/dcn/whitepapers/cisco-vxlan-bgp-evpn-design-and-implementation-guide.html

Méthode conseillée : commencer par la vue d’architecture du constructeur pour comprendre l’implémentation, puis vérifier les comportements protocolaires dans les RFC pertinentes, puis valider les limites et commandes dans la documentation de la version réellement déployée. En cas de contradiction entre un guide ancien, un RFC mis à jour et les notes de version de l’équipement, ne pas copier une commande avant d’avoir identifié le modèle matériel, le train logiciel et la fonction exacte concernés.

## Conclusion

Être expert en Spine/Leaf signifie pouvoir expliquer et démontrer ce que le réseau fera en fonctionnement normal, pendant une panne, sous congestion et au cours d’un changement. La compétence ne se mesure pas au nombre de protocoles connus, mais à la capacité de concevoir des invariants simples, de les valider par des tests reproductibles, d’observer les écarts entre contrôle et données, de protéger les tenants et de restaurer rapidement un service avec des preuves. Une fabric robuste est une architecture dont les limites, les compromis et le mode dégradé sont compris de tous ceux qui l’exploitent.
