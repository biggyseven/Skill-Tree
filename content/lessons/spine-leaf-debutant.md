# Architecture Spine/Leaf — Niveau Débutant

**Niveau :** Débutant  
**Objectif :** comprendre l’architecture Spine/Leaf, savoir reconnaître ses composants, suivre le trajet d’un paquet et réaliser un petit schéma de fabric cohérent.

## 1. Pourquoi cette architecture existe-t-elle ?

Un réseau informatique relie des ordinateurs, des serveurs, des équipements de stockage, des pare-feu et des routeurs. Dans un petit bureau, quelques switches reliés entre eux peuvent suffire. Dans un centre de données (*data center*), des dizaines, des centaines ou davantage de serveurs doivent communiquer rapidement et de manière fiable.

Les applications modernes échangent beaucoup de données entre leurs propres composants. Un site web, par exemple, peut comporter un frontal Web, un serveur applicatif, une base de données et une plateforme de stockage. Les échanges entre serveurs du centre de données sont souvent appelés **trafic est-ouest**. Les échanges entre les serveurs et les utilisateurs, Internet ou un autre réseau sont couramment appelés **trafic nord-sud**.

Une architecture doit pouvoir transporter ces échanges sans créer trop de congestion, rester exploitable quand un lien ou un équipement tombe en panne, et évoluer lorsque de nouveaux serveurs arrivent. La topologie **Spine/Leaf** — également écrite *spine-leaf* ou *leaf-spine* — répond à ces objectifs grâce à deux rôles de commutation distincts :

- les **Leaf**, situés au bord de la fabric, relient les serveurs et les autres équipements terminaux ;
- les **Spine**, situés au cœur de la fabric, relient les Leaf entre eux.

Dans une architecture Spine/Leaf à deux niveaux classique, chaque Leaf se connecte à chacun des Spine. En revanche, les Leaf ne sont généralement pas reliés directement les uns aux autres, et les Spine ne sont généralement pas reliés directement entre eux au sein de la même fabric. Cette structure régulière rend le réseau plus prévisible et plus facile à étendre. [Cisco décrit ce principe dans sa documentation sur les fabrics de data center](https://www.cisco.com/c/en/us/td/docs/solutions/Enterprise/Data_Center/DC_Infra2_5/DCInfra_1.html).

## 2. Les mots essentiels

### 2.1 Switch

Un **switch** (commutateur) relie des appareils dans un réseau local. Il apprend les adresses MAC sur ses ports et utilise sa table de commutation pour envoyer une trame Ethernet vers le port approprié. Un switch peut également effectuer du routage IP s’il possède les fonctions nécessaires et si celles-ci sont configurées.

Un switch n’est pas un simple répartiteur électrique : il prend des décisions de transfert à partir des informations contenues dans les trames et, selon ses fonctions, dans les paquets IP.

### 2.2 Leaf

Un **Leaf** est le switch auquel les équipements terminaux se connectent généralement :

- serveurs physiques ;
- hyperviseurs qui hébergent des machines virtuelles ;
- baies de stockage ;
- pare-feu et répartiteurs de charge (*load balancers*) ;
- routeurs ou liaisons vers des réseaux externes, selon la conception ;
- certains équipements de gestion ou de services.

Un Leaf est parfois installé en haut d’une baie informatique. Cette position est appelée **Top of Rack (ToR)**. Dans d’autres installations, un switch dessert plusieurs baies depuis une rangée centrale ; on parle alors souvent d’**End of Row (EoR)**. ToR et EoR décrivent surtout un mode d’implantation, pas une fonction différente dans le modèle logique.

### 2.3 Spine

Un **Spine** est le switch de transit qui interconnecte les Leaf. Il n’est pas destiné à servir de switch d’accès direct aux serveurs dans une fabric à deux niveaux classique. Un paquet qui doit passer d’un Leaf à un autre transite par un Spine disponible.

Il est fréquent que chaque Leaf ait une liaison vers chaque Spine. Si une fabric comprend quatre Spine et six Leaf, on prévoit donc en principe quatre liaisons montantes par Leaf, une vers chaque Spine, à condition que le matériel, les ports et le plan de câblage le permettent.

### 2.4 Fabric

Une **fabric** est l’ensemble formé par les switches de la topologie et leurs interconnexions, exploités comme un réseau cohérent. L’expression *IP fabric* désigne souvent une fabric dont les liens entre switches transportent du routage IP. Des technologies d’overlay telles que VXLAN peuvent être ajoutées au-dessus, mais **Spine/Leaf décrit d’abord une topologie physique/logique ; ce n’est pas, à elle seule, un protocole**.

### 2.5 Lien montant et lien descendant

- **Lien descendant (downlink)** : lien qui part typiquement d’un Leaf vers un serveur, une baie de stockage ou un équipement terminal.
- **Lien montant (uplink)** : lien qui part d’un Leaf vers un Spine dans la fabric à deux niveaux.

Ces mots décrivent le rôle du lien dans le schéma, pas le sens de circulation des données : le trafic circule généralement dans les deux sens.

## 3. Lire le schéma de base

Le diagramme suivant montre trois Leaf et deux Spine. Chaque Leaf est relié aux deux Spine. Les serveurs sont connectés en dessous des Leaf.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 500" role="img" aria-label="Fabric Spine Leaf de base avec deux Spine, trois Leaf et des serveurs" width="100%" height="auto"><defs><marker id="sl1Arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67d9ff"/></marker><marker id="sl1ServerArrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#8ee6b0"/></marker></defs><style>.slbox{rx:12;stroke-width:2}.sllabel{font:600 16px system-ui,sans-serif;fill:#edf4ff;text-anchor:middle}.slsmall{font:13px system-ui,sans-serif;fill:#b5c2d4;text-anchor:middle}.slflow{fill:none;stroke:#67d9ff;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#sl1Arrow);animation:sl1Dash 2.5s linear infinite}.slaccess{fill:none;stroke:#8ee6b0;stroke-width:2.5;marker-end:url(#sl1ServerArrow)}@keyframes sl1Dash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.slflow{animation:none}}</style><rect x="40" y="22" width="820" height="180" rx="18" fill="#101b2b" stroke="#35516f" stroke-dasharray="5 6"/><text x="450" y="48" class="slsmall">Couche Spine — transit entre les Leaf</text><rect class="slbox" x="235" y="70" width="170" height="66" fill="#183b5b" stroke="#67d9ff"/><text x="320" y="98" class="sllabel">SPINE 1</text><text x="320" y="119" class="slsmall">Transit</text><rect class="slbox" x="495" y="70" width="170" height="66" fill="#183b5b" stroke="#67d9ff"/><text x="580" y="98" class="sllabel">SPINE 2</text><text x="580" y="119" class="slsmall">Transit</text><rect x="40" y="220" width="820" height="150" rx="18" fill="#111c27" stroke="#35516f" stroke-dasharray="5 6"/><text x="450" y="244" class="slsmall">Couche Leaf — accès aux équipements</text><g class="slflow"><path d="M320 136 L170 272"/><path d="M320 136 L450 272"/><path d="M320 136 L730 272"/><path d="M580 136 L170 272"/><path d="M580 136 L450 272"/><path d="M580 136 L730 272"/></g><g><rect class="slbox" x="95" y="265" width="150" height="58" fill="#193b2e" stroke="#8ee6b0"/><text x="170" y="289" class="sllabel">LEAF 1</text><text x="170" y="309" class="slsmall">Serveurs / racks</text><rect class="slbox" x="375" y="265" width="150" height="58" fill="#193b2e" stroke="#8ee6b0"/><text x="450" y="289" class="sllabel">LEAF 2</text><text x="450" y="309" class="slsmall">Serveurs / racks</text><rect class="slbox" x="655" y="265" width="150" height="58" fill="#193b2e" stroke="#8ee6b0"/><text x="730" y="289" class="sllabel">LEAF 3</text><text x="730" y="309" class="slsmall">Serveurs / racks</text></g><g stroke="#8ee6b0" stroke-width="2.5" fill="none"><path d="M170 323 L170 390"/><path d="M450 323 L450 390"/><path d="M730 323 L730 390"/></g><g fill="#202c3d" stroke="#8ee6b0" stroke-width="1.5"><rect x="102" y="390" width="136" height="36" rx="7"/><rect x="382" y="390" width="136" height="36" rx="7"/><rect x="662" y="390" width="136" height="36" rx="7"/></g><g class="sllabel"><text x="170" y="413">SERVEURS A</text><text x="450" y="413">SERVEURS B</text><text x="730" y="413">SERVEURS C</text></g><text x="450" y="466" class="slsmall">Chaque Leaf est relié à chaque Spine ; aucun Leaf n’est directement relié à un autre Leaf dans ce modèle.</text></svg></div>

**Comment lire ce schéma :**

1. Les serveurs sont connectés aux Leaf, pas directement aux Spine.
2. Chaque Leaf dispose de liens vers Spine 1 et Spine 2.
3. Les flèches bleues indiquent un exemple de trajet de transit vers les Leaf ; les liens réseau restent bidirectionnels en pratique.
4. Si Serveur A doit joindre Serveur C, et que les deux serveurs sont derrière des Leaf différents, le trafic peut passer par le Leaf 1, un Spine, puis le Leaf 3.

Le schéma est volontairement simplifié : il ne représente pas le routage, les VLAN, les adresses IP, le câblage redondant des serveurs ni les politiques de sécurité. Ces éléments dépendent de la conception choisie.

## 4. Les deux grandes couches en détail

### 4.1 Ce que fait un Leaf

Le Leaf est le point d’entrée dans la fabric. Lorsqu’un serveur envoie une trame Ethernet, le Leaf reçoit cette trame sur le port où le serveur est branché. Selon la conception, il peut :

- commuter une trame dans le même domaine de couche 2 ;
- effectuer un routage IP entre réseaux ;
- appliquer des listes de contrôle d’accès ou d’autres règles ;
- acheminer le trafic vers un Spine lorsque la destination se trouve derrière un autre Leaf ;
- signaler ou apprendre des informations d’accès et d’adressage selon le protocole utilisé.

Le détail dépend de la plateforme et de l’architecture. Dans une fabric IP classique, les Leaf réalisent souvent le routage de couche 3 vers les Spine. Dans une fabric avec overlay, les Leaf peuvent également être les points de terminaison des tunnels. Il ne faut pas supposer que toutes les installations Spine/Leaf utilisent VXLAN ou le même protocole de routage.

### 4.2 Ce que fait un Spine

Le Spine transporte les paquets entre les Leaf. Il est conçu pour fournir une capacité de transit importante et de nombreux ports de fabric. Dans le modèle de base, il ne sert pas de switch d’accès aux serveurs.

Un Spine ne « choisit » pas nécessairement un seul chemin fixe. Plusieurs liens de même coût peuvent exister entre les Leaf et les Spine. Les protocoles de routage et les mécanismes de répartition permettent de sélectionner ou d’utiliser plusieurs chemins quand la topologie et la configuration les rendent disponibles.

### 4.3 Pourquoi séparer ces rôles ?

La séparation est utile parce que les besoins des deux rôles sont différents. Les Leaf doivent offrir des ports adaptés aux serveurs et aux appliances. Les Spine doivent surtout interconnecter les Leaf avec de bonnes performances et une capacité de ports adaptée. Le fait de séparer les rôles évite de dépendre d’un seul équipement central pour une très grande partie des communications.

## 5. Comment un paquet traverse la fabric

Imaginons deux serveurs :

- **Serveur A**, adresse IP `10.10.1.10`, raccordé à Leaf 1 ;
- **Serveur B**, adresse IP `10.10.2.20`, raccordé à Leaf 3.

Pour simplifier, supposons que les deux serveurs doivent communiquer par routage IP et que les réseaux sont configurés correctement. Voici le trajet logique :

1. Le Serveur A détermine que la destination n’est pas dans son sous-réseau local. Il envoie le paquet à sa passerelle par défaut.
2. La passerelle est fournie ou atteinte via la configuration réseau du serveur et le Leaf associé, selon le design.
3. Le Leaf 1 consulte ses informations de routage. La destination se trouve derrière un autre Leaf : il envoie le paquet dans la fabric.
4. Un Spine transporte le paquet vers Leaf 3. Si plusieurs chemins de coût égal sont configurés, le réseau peut répartir les flux entre plusieurs chemins.
5. Leaf 3 remet le paquet au Serveur B sur le port d’accès approprié.
6. Le Serveur B renvoie sa réponse selon sa propre table de routage. Le chemin retour peut être différent si le réseau l’autorise et si les décisions de routage sont asymétriques.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-label="Trajet d’un paquet d’un serveur raccordé à Leaf 1 vers un serveur raccordé à Leaf 3 en passant par un Spine" width="100%" height="auto"><defs><marker id="sl2Arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#ffca74"/></marker></defs><style>.sl2box{rx:10;stroke-width:2}.sl2t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.sl2s{font:12px system-ui,sans-serif;fill:#bdc9d9;text-anchor:middle}.sl2route{fill:none;stroke:#ffca74;stroke-width:4;stroke-dasharray:9 7;marker-end:url(#sl2Arrow);animation:sl2Dash 2s linear infinite}@keyframes sl2Dash{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.sl2route{animation:none}}</style><rect x="30" y="75" width="150" height="76" class="sl2box" fill="#203047" stroke="#8ee6b0"/><text x="105" y="105" class="sl2t">Serveur A</text><text x="105" y="128" class="sl2s">10.10.1.10</text><rect x="250" y="75" width="150" height="76" class="sl2box" fill="#193b2e" stroke="#8ee6b0"/><text x="325" y="105" class="sl2t">Leaf 1</text><text x="325" y="128" class="sl2s">Entrée de la fabric</text><rect x="500" y="75" width="150" height="76" class="sl2box" fill="#183b5b" stroke="#67d9ff"/><text x="575" y="105" class="sl2t">Spine</text><text x="575" y="128" class="sl2s">Transit</text><rect x="720" y="75" width="150" height="76" class="sl2box" fill="#193b2e" stroke="#8ee6b0"/><text x="795" y="105" class="sl2t">Leaf 3</text><text x="795" y="128" class="sl2s">Sortie vers B</text><path d="M180 113 H250" class="sl2route"/><path d="M400 113 H500" class="sl2route"/><path d="M650 113 H720" class="sl2route"/><text x="450" y="36" class="sl2s">Trajet aller illustratif</text><path d="M795 151 V205 H105 V151" fill="none" stroke="#9baabe" stroke-width="2.5" stroke-dasharray="5 5"/><text x="450" y="229" class="sl2s">La réponse revient vers la source ; son chemin exact dépend du routage.</text><rect x="325" y="250" width="250" height="48" rx="9" fill="#202c3d" stroke="#73849b"/><text x="450" y="270" class="sl2t">Serveur B : 10.10.2.20</text><text x="450" y="288" class="sl2s">Derrière Leaf 3</text><path d="M795 151 V274 H575" fill="none" stroke="#8ee6b0" stroke-width="2.2"/><text x="708" y="264" class="sl2s">Livraison locale</text></svg></div>

### 5.1 Le rôle des adresses MAC et IP

Une trame Ethernet transporte un paquet IP. Les adresses MAC servent au transfert de couche 2 sur un segment Ethernet, tandis que les adresses IP identifient les interfaces et réseaux de couche 3. Lorsqu’un paquet est routé, les en-têtes Ethernet sont adaptés à chaque saut de couche 2, alors que les adresses IP source et destination du paquet restent normalement les mêmes, sauf mécanismes comme le NAT.

Cette différence aide à comprendre les captures réseau. Une adresse MAC visible sur un lien entre switches n’est pas forcément celle du serveur d’origine : elle dépend du type de trafic et du point d’observation. Le détail varie entre une fabric routée, une fabric VXLAN/EVPN et une fabric pilotée par une solution comme Cisco ACI.

### 5.2 Le plan de données et le plan de contrôle

Le **plan de données** transfère effectivement les trames et les paquets. Le **plan de contrôle** calcule ou distribue les informations nécessaires au transfert, par exemple les routes IP. La gestion et la télémétrie relèvent d’autres fonctions de contrôle et d’exploitation selon la plateforme.

Il n’est pas nécessaire de maîtriser tous les protocoles dès le début, mais retiens ce point : un câble connecté ne garantit pas que le trafic circulera. Les interfaces doivent être actives, les routes ou tables de transfert doivent être cohérentes et les politiques doivent autoriser les échanges attendus.

## 6. Spine/Leaf et architecture traditionnelle à trois niveaux

Dans beaucoup de réseaux d’entreprise classiques, le modèle hiérarchique comprend **Accès**, **Distribution** et **Cœur (Core)**. L’accès connecte les utilisateurs et équipements ; la distribution agrège les switches d’accès et applique souvent des politiques ; le cœur fournit le transport rapide entre les blocs du réseau.

Spine/Leaf possède plutôt deux rôles principaux : Leaf et Spine. Il est particulièrement utile quand de nombreux serveurs communiquent régulièrement entre eux. Dans une conception bien construite, un échange entre deux Leaf différents traverse généralement un Leaf d’origine, un Spine, puis le Leaf de destination : le nombre de sauts de fabric reste prévisible.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 355" role="img" aria-label="Comparaison d’un réseau hiérarchique à trois couches et d’une fabric Spine Leaf à deux couches" width="100%" height="auto"><style>.sl3b{rx:10;stroke-width:2}.sl3t{font:600 14px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.sl3s{font:12px system-ui,sans-serif;fill:#b9c7d9;text-anchor:middle}.sl3line{fill:none;stroke:#8ca4c4;stroke-width:2.2}</style><text x="225" y="27" class="sl3t">Modèle hiérarchique classique</text><text x="675" y="27" class="sl3t">Spine/Leaf</text><g><rect x="125" y="45" width="200" height="48" class="sl3b" fill="#183b5b" stroke="#67d9ff"/><text x="225" y="74" class="sl3t">Cœur (Core)</text><rect x="125" y="130" width="200" height="48" class="sl3b" fill="#3b2d58" stroke="#c7a4ff"/><text x="225" y="159" class="sl3t">Distribution</text><rect x="125" y="215" width="200" height="48" class="sl3b" fill="#193b2e" stroke="#8ee6b0"/><text x="225" y="244" class="sl3t">Accès</text><path d="M225 93 V130 M225 178 V215 M225 263 V287" class="sl3line"/><rect x="145" y="287" width="160" height="42" rx="8" fill="#202c3d" stroke="#73849b"/><text x="225" y="313" class="sl3t">Utilisateurs / serveurs</text></g><g><rect x="575" y="45" width="200" height="48" class="sl3b" fill="#183b5b" stroke="#67d9ff"/><text x="675" y="74" class="sl3t">Spine</text><rect x="575" y="145" width="200" height="48" class="sl3b" fill="#193b2e" stroke="#8ee6b0"/><text x="675" y="174" class="sl3t">Leaf</text><path d="M625 93 L625 145 M675 93 V145 M725 93 L725 145" class="sl3line"/><path d="M625 193 V225 M675 193 V225 M725 193 V225" class="sl3line"/><rect x="560" y="225" width="230" height="48" rx="8" fill="#202c3d" stroke="#73849b"/><text x="675" y="254" class="sl3t">Serveurs / stockage / appliances</text><text x="675" y="310" class="sl3s">Rôles distincts et chemins réguliers</text></g><path d="M425 40 V332" stroke="#34465d" stroke-width="1.5" stroke-dasharray="4 5"/><text x="450" y="345" class="sl3s">Schémas simplifiés : le choix dépend des besoins, pas d’une règle universelle.</text></svg></div>

| Critère | Réseau hiérarchique à trois niveaux | Spine/Leaf |
|---|---|---|
| Couches principales | Accès, distribution, cœur | Leaf, Spine |
| Usage courant | Campus, réseaux d’entreprise, réseaux d’accès | Centres de données, environnements de serveurs |
| Chemins est-ouest | Peuvent traverser plusieurs niveaux selon le design | Réguliers entre Leaf distincts dans une fabric à deux niveaux |
| Extension | Ajout de switches à la couche appropriée | Ajout de Leaf et, selon la capacité disponible, de Spine |
| Limite | Peut devenir complexe si les flux serveur-à-serveur augmentent | Demande un plan de câblage et de capacité rigoureux |

Ces deux approches ne s’excluent pas. Un campus d’entreprise peut être hiérarchique et être raccordé à un data center Spine/Leaf. Le choix dépend des flux, du nombre de ports, des distances, du coût, des exigences opérationnelles et des compétences de l’équipe.

## 7. Pourquoi chaque Leaf se connecte-t-il à chaque Spine ?

Cette règle crée un maillage complet entre les deux couches. Dans un exemple avec trois Leaf et deux Spine, chaque Leaf possède deux liaisons montantes. Il existe donc six interconnexions Leaf-Spine : `3 Leaf × 2 Spine = 6 liens`, en supposant une liaison par paire.

Le nombre de liens est une bonne première façon de vérifier un dessin. Si un Leaf n’a aucun lien vers Spine 2 alors que le design demande que chaque Leaf rejoigne chaque Spine, ce Leaf ne respecte pas la topologie voulue. Il faut distinguer cette vérification du contrôle de capacité : un lien peut être présent mais sous-dimensionné ou mal configuré.

### 7.1 Calcul rapide du nombre de liens

Dans le cas simple d’une liaison par paire Leaf-Spine :

**Nombre de liens Leaf-Spine = nombre de Leaf × nombre de Spine.**

Exemples :

- 4 Leaf et 2 Spine : `4 × 2 = 8` liens ;
- 8 Leaf et 4 Spine : `8 × 4 = 32` liens ;
- 12 Leaf et 6 Spine : `12 × 6 = 72` liens.

Ce calcul est uniquement un comptage topologique. Il ne veut pas dire qu’un seul lien suffit en capacité pour tous les usages. Certains designs utilisent plusieurs liens physiques par paire, des liens agrégés, des ports de vitesses différentes ou des câbles breakout. Il faut alors compter chaque lien physique et respecter les capacités et contraintes du matériel.

### 7.2 Limites de ports

Le nombre de Leaf qu’une fabric peut prendre en charge dépend notamment :

- du nombre de ports utilisables sur les Spine ;
- du nombre de ports montants prévus par Leaf ;
- du nombre de ports réservés à d’autres besoins ;
- des vitesses et modes compatibles avec les transceivers et câbles ;
- de la capacité de commutation et des fonctions supportées par les équipements ;
- des contraintes de redondance et de maintenance.

Par exemple, si chaque Leaf doit utiliser quatre ports montants et que le Spine choisi n’a que 32 ports adaptés disponibles pour ce rôle, on ne peut pas déduire que la fabric accueillera simplement `32 × 4` Leaf. Dans le modèle standard, ces 32 ports Spine sont partagés entre les Leaf ; le calcul de capacité dépend donc du nombre de liaisons dont chaque Leaf a besoin et du nombre de Spine.

## 8. Redondance : que se passe-t-il en cas de panne ?

La redondance signifie que plusieurs composants ou chemins sont disponibles pour réduire l’impact d’une défaillance. Avec deux Spine, un Leaf est physiquement raccordé aux deux. Si le lien d’un Leaf vers un Spine tombe en panne, le Leaf peut conserver une liaison vers l’autre Spine. Si un Spine entier tombe en panne, chaque Leaf correctement câblé peut rester relié au Spine restant.

Cette résilience n’est pas automatique dans toutes les circonstances. Le réseau doit détecter la panne, recalculer ou ajuster le transfert et disposer d’une capacité suffisante sur les chemins restants. Les protocoles, les temporisations, les politiques et les limites des équipements influencent le comportement réel.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 380" role="img" aria-label="Exemple de fabric redondante où Spine 2 est indisponible mais des chemins via Spine 1 restent disponibles" width="100%" height="auto"><defs><marker id="sl4Arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#8ee6b0"/></marker></defs><style>.sl4b{rx:10;stroke-width:2}.sl4t{font:600 15px system-ui,sans-serif;fill:#edf4ff;text-anchor:middle}.sl4s{font:12px system-ui,sans-serif;fill:#b8c6d9;text-anchor:middle}.sl4ok{fill:none;stroke:#8ee6b0;stroke-width:3;marker-end:url(#sl4Arrow);stroke-dasharray:8 6;animation:sl4Dash 2.5s linear infinite}.sl4dead{fill:none;stroke:#ff6b78;stroke-width:3;stroke-dasharray:5 6;opacity:.8}@keyframes sl4Dash{to{stroke-dashoffset:-28}}@media(prefers-reduced-motion:reduce){.sl4ok{animation:none}}</style><rect x="140" y="24" width="220" height="65" class="sl4b" fill="#183b5b" stroke="#67d9ff"/><text x="250" y="52" class="sl4t">SPINE 1</text><text x="250" y="72" class="sl4s">Disponible</text><rect x="540" y="24" width="220" height="65" class="sl4b" fill="#38232a" stroke="#ff6b78" stroke-dasharray="7 5"/><text x="650" y="52" class="sl4t">SPINE 2</text><text x="650" y="72" class="sl4s">Panne simulée</text><g><rect x="85" y="210" width="180" height="62" class="sl4b" fill="#193b2e" stroke="#8ee6b0"/><text x="175" y="237" class="sl4t">LEAF 1</text><text x="175" y="257" class="sl4s">Serveur A</text><rect x="360" y="210" width="180" height="62" class="sl4b" fill="#193b2e" stroke="#8ee6b0"/><text x="450" y="237" class="sl4t">LEAF 2</text><text x="450" y="257" class="sl4s">Serveur B</text><rect x="635" y="210" width="180" height="62" class="sl4b" fill="#193b2e" stroke="#8ee6b0"/><text x="725" y="237" class="sl4t">LEAF 3</text><text x="725" y="257" class="sl4s">Serveur C</text></g><g class="sl4ok"><path d="M250 89 L175 210"/><path d="M250 89 L450 210"/><path d="M250 89 L725 210"/></g><g class="sl4dead"><path d="M650 89 L175 210"/><path d="M650 89 L450 210"/><path d="M650 89 L725 210"/></g><text x="450" y="143" class="sl4s">Les chemins verts restent disponibles dans cet exemple</text><text x="450" y="320" class="sl4t">La continuité dépend aussi de la détection de panne</text><text x="450" y="346" class="sl4s">Il faut vérifier capacité restante, routage, convergence et alarmes.</text></svg></div>

### 8.1 Tolérance à la panne ne veut pas dire absence d’interruption

Un chemin de secours ne signifie pas toujours que les applications ne remarqueront rien. Lorsqu’un lien ou un équipement tombe, le réseau a besoin d’un mécanisme pour constater l’événement et mettre à jour ses chemins. Certains flux peuvent perdre quelques paquets pendant cette convergence. Les flux établis peuvent aussi être affectés par des politiques de sécurité, des sessions stateful ou des limites de capacité.

### 8.2 Quelles pannes faut-il considérer ?

Une étude correcte examine au moins :

- la panne d’un lien entre un Leaf et un Spine ;
- la panne complète d’un Spine ;
- la perte de l’alimentation ou d’un composant d’un switch ;
- la panne d’un port serveur ;
- la panne d’un serveur ou d’une carte réseau ;
- une erreur de configuration qui retire une route ou désactive un port ;
- une surcharge, même lorsque tous les liens sont techniquement actifs.

Dans de nombreux déploiements, les serveurs importants sont eux-mêmes raccordés à deux Leaf. Cette redondance d’accès nécessite une conception adaptée, par exemple un mécanisme de multihoming pris en charge par la plateforme. Deux câbles vers deux switches ne peuvent pas être branchés arbitrairement sans vérifier les exigences de couche 2, les mécanismes de haute disponibilité et la configuration du serveur.

## 9. Répartition du trafic et ECMP

**ECMP** signifie *Equal-Cost Multipath*, ou chemins multiples de coût égal. Lorsqu’une destination est accessible par plusieurs routes de même coût, certains protocoles et équipements peuvent répartir différents flux entre ces chemins. Une fabric Spine/Leaf est bien adaptée à cette approche parce qu’un Leaf peut avoir plusieurs chemins vers les autres Leaf via différents Spine.

ECMP ne veut pas nécessairement dire qu’un même paquet est copié sur chaque chemin. Généralement, le réseau choisit un chemin pour un flux, souvent à partir d’un hachage de certains champs d’en-tête. Ce mécanisme aide à préserver l’ordre des paquets d’un flux tout en utilisant plusieurs chemins entre de nombreux flux.

### 9.1 Pourquoi ne pas répartir chaque paquet au hasard ?

Si chaque paquet d’une même conversation suit un chemin différent avec des délais variables, les paquets pourraient arriver dans le désordre. Certains protocoles, notamment TCP, peuvent en être affectés. Les mécanismes de hachage cherchent donc souvent à garder les paquets d’un flux sur un chemin cohérent, tout en répartissant un ensemble de flux.

### 9.2 ECMP n’égalise pas toujours parfaitement l’utilisation

L’équilibrage dépend du nombre de flux, de leurs caractéristiques, de la fonction de hachage et de la disponibilité des chemins. Quelques flux très volumineux peuvent se retrouver sur un même lien, même si plusieurs liens sont disponibles. Ce phénomène est parfois appelé **polarisation** ou déséquilibre de trafic. Des fonctions de hachage avancées, des réglages adaptés et la surveillance peuvent améliorer la situation ; ils ne garantissent pas forcément une distribution parfaite.

### 9.3 Vitesse et surabonnement

Le **surabonnement** (*oversubscription*) compare la capacité totale des ports côté serveurs à la capacité des liens montants. Prenons un Leaf avec 48 ports serveur de 25 Gbit/s et quatre uplinks de 100 Gbit/s. La capacité théorique cumulée des ports serveurs est `48 × 25 = 1 200 Gbit/s`. La capacité cumulée des uplinks est `4 × 100 = 400 Gbit/s`. Le ratio côté serveur/côté fabric vaut `1 200 / 400 = 3:1`.

Un ratio de 3:1 ne signifie pas que chaque application disposera d’un tiers de sa vitesse. Il indique qu’une charge simultanée pleine de tous les ports serveurs dépasserait la capacité cumulée de ces uplinks si tout le trafic devait sortir du Leaf. En pratique, une partie du trafic peut rester locale au Leaf, et tous les ports ne transmettent pas forcément à pleine vitesse en même temps.

Il faut aussi tenir compte de la vitesse réellement négociée, des capacités de commutation, des limites de buffers, du type de trafic et des objectifs de performance. Le bon ratio n’est pas universel : il dépend du profil applicatif, du budget et des exigences de niveau de service.

## 10. Les notions IP de base dans une fabric Spine/Leaf

L’architecture indique comment les switches sont disposés. Elle ne fixe pas automatiquement le plan d’adressage ou le protocole de routage.

### 10.1 Sous-réseau et passerelle

Un serveur dispose généralement d’une adresse IP, d’un masque ou préfixe et d’une passerelle par défaut lorsqu’il doit joindre des réseaux différents. La passerelle est le prochain saut vers les destinations hors du sous-réseau local. Dans de nombreuses fabric IP, les Leaf assurent le routage de passerelle pour les réseaux de serveurs, mais des architectures différentes sont possibles.

Exemple pédagogique :

- Serveur A : `10.10.1.10/24`, passerelle `10.10.1.1` ;
- Serveur B : `10.10.2.20/24`, passerelle `10.10.2.1`.

Les adresses appartiennent à deux sous-réseaux IPv4 différents. Une communication entre les serveurs doit donc être routée, à condition que les passerelles et routes soient correctement configurées et que les règles de sécurité autorisent la communication.

### 10.2 Routage entre Leaf et Spine

Dans une fabric IP routée, les liaisons Leaf-Spine sont souvent des liens de couche 3. Les switches échangent des informations de routage à l’aide d’un protocole dynamique, par exemple eBGP ou OSPF, selon la conception. Il existe aussi des configurations plus simples ou des designs fondés sur d’autres mécanismes.

Ne retiens pas « Spine/Leaf = BGP » comme une règle absolue. Spine/Leaf désigne la structure. BGP et OSPF sont des choix possibles pour le routage ; le protocole exact dépend des objectifs, de la plateforme et des compétences d’exploitation.

### 10.3 Plan d’adressage des liaisons

Les liaisons point à point entre switches peuvent utiliser de petits sous-réseaux, souvent en IPv4 `/31` lorsque les équipements et pratiques de conception le permettent. Ce préfixe fournit deux adresses utilisables sur un lien point à point. Certains environnements emploient IPv6 ou d’autres conventions. Le plan doit être documenté et cohérent.

Pour un débutant, le plus important est de comprendre que chaque interface routée doit avoir une configuration IP valide, que les deux extrémités doivent être compatibles, et qu’une adresse IP seule ne crée pas une route vers toutes les autres destinations.

## 11. Couche 2, VLAN, VXLAN : notions à ne pas confondre

### 11.1 VLAN

Un **VLAN** sépare logiquement des domaines de couche 2 sur une infrastructure Ethernet. Il sert notamment à segmenter les équipements et domaines de broadcast. Les VLAN sont courants dans les réseaux de campus et peuvent également exister aux ports d’accès d’une fabric.

### 11.2 VXLAN

**VXLAN** est une technologie d’encapsulation qui permet de transporter des trames Ethernet dans des paquets UDP/IP, généralement au-dessus d’un réseau IP. On parle souvent d’overlay VXLAN au-dessus d’un underlay IP. Dans plusieurs designs, les Leaf assurent les fonctions de VTEP, c’est-à-dire les points de terminaison de tunnel VXLAN.

Cependant, toutes les fabrics Spine/Leaf n’emploient pas VXLAN. Certaines sont de simples fabrics IP routées ; d’autres utilisent EVPN pour distribuer des informations de contrôle relatives à l’overlay ; Cisco ACI emploie son propre modèle de politique et des mécanismes spécifiques. Pour cette raison, le schéma de base d’un Spine/Leaf ne doit pas laisser croire que VXLAN est obligatoire.

### 11.3 Underlay et overlay

- **Underlay** : réseau de transport sous-jacent qui fournit la connectivité entre les équipements de la fabric.
- **Overlay** : réseau logique construit au-dessus de l’underlay, souvent à l’aide d’encapsulation et de mécanismes de contrôle complémentaires.

Une panne de l’underlay peut rendre l’overlay inaccessible, même si la configuration logique de ce dernier semble inchangée. Le diagnostic consiste donc à vérifier d’abord les liens, interfaces et routes de transport, puis les tunnels, tables d’apprentissage, segments et politiques de l’overlay.

## 12. Accès aux réseaux externes

Une fabric ne vit pas isolée. Elle doit souvent communiquer avec le réseau d’entreprise, Internet, des services partagés, des pare-feu ou d’autres centres de données. L’architecture peut utiliser des Leaf de bord (*border leaf*) ou d’autres équipements de frontière selon le design.

Un Leaf de bord est un Leaf choisi pour connecter la fabric à des réseaux extérieurs. Cela ne signifie pas que tous les Leaf ont ce rôle. Séparer les fonctions aide à clarifier les routes externes, les politiques de sécurité et la capacité des liens de sortie.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 350" role="img" aria-label="Une paire de Leaf de bord relie la fabric Spine Leaf à un pare-feu et au réseau externe" width="100%" height="auto"><defs><marker id="sl5Arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#ffca74"/></marker></defs><style>.sl5b{rx:10;stroke-width:2}.sl5t{font:600 15px system-ui,sans-serif;fill:#edf4ff;text-anchor:middle}.sl5s{font:12px system-ui,sans-serif;fill:#bdc9d9;text-anchor:middle}.sl5flow{fill:none;stroke:#ffca74;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#sl5Arrow);animation:sl5Dash 2.4s linear infinite}@keyframes sl5Dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.sl5flow{animation:none}}</style><rect x="30" y="25" width="570" height="275" rx="16" fill="#101b2b" stroke="#35516f" stroke-dasharray="5 5"/><text x="315" y="50" class="sl5s">Fabric Spine/Leaf interne</text><rect x="85" y="80" width="180" height="52" class="sl5b" fill="#183b5b" stroke="#67d9ff"/><text x="175" y="111" class="sl5t">Spine</text><rect x="65" y="190" width="210" height="60" class="sl5b" fill="#193b2e" stroke="#8ee6b0"/><text x="170" y="216" class="sl5t">Leaf serveurs</text><text x="170" y="237" class="sl5s">Charges applicatives</text><rect x="350" y="190" width="215" height="60" class="sl5b" fill="#3b2d58" stroke="#c7a4ff"/><text x="457" y="216" class="sl5t">Leaf de bord</text><text x="457" y="237" class="sl5s">Border Leaf</text><path d="M175 132 V190 M265 106 H310 V220 H350" fill="none" stroke="#8ca4c4" stroke-width="2.5"/><path d="M275 220 H350" class="sl5flow"/><rect x="660" y="80" width="195" height="60" class="sl5b" fill="#382b1d" stroke="#ffca74"/><text x="757" y="107" class="sl5t">Pare-feu / routeur</text><text x="757" y="126" class="sl5s">Contrôle selon le design</text><rect x="660" y="205" width="195" height="60" class="sl5b" fill="#202c3d" stroke="#73849b"/><text x="757" y="232" class="sl5t">Réseau externe</text><text x="757" y="251" class="sl5s">Entreprise / Internet</text><path d="M565 220 H620 V110 H660" class="sl5flow"/><path d="M757 140 V205" class="sl5flow"/><text x="450" y="328" class="sl5s">Les routes retour et les politiques de sécurité doivent aussi être correctes.</text></svg></div>

Les points de contrôle à vérifier sont :

1. Le lien physique vers l’équipement externe est opérationnel.
2. Les adresses IP et le routage sur les deux extrémités sont cohérents.
3. Les routes vers les réseaux distants existent, et le réseau distant connaît le chemin retour.
4. Le pare-feu et les politiques autorisent les protocoles et ports nécessaires.
5. La capacité du lien externe est suffisante.

Un trafic peut sortir de la fabric mais échouer au retour. Le diagnostic doit donc examiner les deux directions et ne pas se limiter au premier saut.

## 13. Capacité et choix des équipements

Il est tentant de choisir des switches en se basant seulement sur le nombre de ports. Pourtant, le dimensionnement d’une fabric tient compte de plusieurs paramètres :

- nombre de serveurs et de ports par serveur ;
- débit requis par port serveur ;
- nombre de liaisons montantes par Leaf ;
- vitesse de chaque uplink ;
- besoins de redondance ;
- volume de trafic est-ouest ;
- trafic vers les réseaux extérieurs ;
- latence visée et exigences applicatives ;
- disponibilité des modules optiques, câbles et ports compatibles ;
- croissance future et marge pour la maintenance.

### 13.1 Exemple de dimensionnement préliminaire

Une petite installation doit raccorder 36 serveurs, chaque serveur ayant une liaison Ethernet de 10 Gbit/s. On envisage deux Leaf avec 48 ports d’accès chacun et deux Spine. Chaque Leaf dispose de deux uplinks de 100 Gbit/s, une liaison vers chaque Spine.

**Ce que l’on peut dire :**

- les 36 serveurs peuvent être répartis entre les deux Leaf selon la disponibilité des ports et le plan d’adressage ;
- deux Spine offrent deux chemins de transit physiques, si chaque Leaf se connecte bien aux deux ;
- chaque Leaf possède 200 Gbit/s de capacité montante théorique agrégée avec deux liens de 100 Gbit/s ;
- le ratio et les performances réelles dépendront de la circulation locale, des flux et des caractéristiques des équipements.

**Ce qu’on ne peut pas conclure sans autres informations :**

- que tous les serveurs pourront utiliser leur débit maximal simultanément vers n’importe quelle destination ;
- qu’il n’y aura jamais de perte de paquets ;
- que la panne d’un seul Spine sera sans aucune interruption visible ;
- que n’importe quel module optique ou câble sera compatible ;
- que la paire de Leaf suffit pour tous les besoins de haute disponibilité de l’application.

Le dimensionnement précis doit suivre les fiches techniques et guides de conception du fabricant choisi. Les vitesses, densités de ports et fonctions diffèrent selon les modèles et versions logicielles.

### 13.2 Débit théorique et débit utile

Un lien annoncé à 100 Gbit/s ne garantit pas à lui seul un débit applicatif soutenu de 100 Gbit/s dans chaque situation. Le résultat varie selon les tailles de paquets, les protocoles, l’encapsulation, les capacités de transfert, les fonctionnalités activées, les limitations du serveur et les congestions éventuelles. Pour le niveau débutant, garde en tête qu’une somme de débits de ports n’est pas une mesure de performance applicative complète.

## 14. Comment dessiner correctement une topologie Spine/Leaf

Un schéma réseau doit permettre à quelqu’un d’autre de comprendre le câblage sans devoir deviner. Une représentation correcte doit notamment :

1. séparer visuellement les couches Spine et Leaf ;
2. relier chaque Leaf à chaque Spine prévu par le design ;
3. montrer les serveurs sous les Leaf ;
4. différencier les liens internes de fabric et les liaisons externes ;
5. expliquer le sens d’un flux avec des flèches uniquement lorsqu’un trajet est illustré ;
6. indiquer si les flèches montrent un exemple de trajet de données et non le sens physique exclusif d’un lien ;
7. éviter les croisements inutiles, les étiquettes sur les lignes et les liens qui semblent toucher le mauvais équipement ;
8. préciser le nombre et la vitesse des liaisons lorsqu’il s’agit d’un schéma de capacité ;
9. ajouter une légende pour les couleurs, les lignes pointillées et les équipements ;
10. signaler les hypothèses et les éléments non représentés.

Une flèche de flux et une ligne de câblage ne veulent pas dire la même chose. Une ligne de câblage indique qu’un lien existe. Une flèche peut indiquer le sens d’un paquet ou d’un échange donné. Sur un schéma d’infrastructure, dessiner toutes les lignes avec une flèche peut donner l’impression trompeuse qu’un lien est unidirectionnel. Dans les diagrammes de ce cours, les flèches sur les chemins animés illustrent un trajet d’exemple ; les connexions physiques restent bidirectionnelles, sauf cas spécifique documenté.

## 15. Mise en pratique : créer une petite fabric

### Scénario

Tu dois concevoir un petit réseau de laboratoire pour raccorder trois groupes de serveurs :

- groupe Web : deux serveurs ;
- groupe Applicatif : deux serveurs ;
- groupe Base de données : deux serveurs.

Tu disposes de deux Spine et de trois Leaf. Le design impose que chaque Leaf rejoigne les deux Spine. Chaque groupe de serveurs est raccordé à un Leaf dédié dans le premier schéma logique.

### Étape 1 — Dessiner le matériel

Place deux Spine en haut, trois Leaf au milieu et les six serveurs en dessous. Relie chaque Leaf aux deux Spine. Ajoute ensuite les connexions des serveurs à leur Leaf. Vérifie le nombre de liens : avec trois Leaf et deux Spine, six liens Leaf-Spine sont attendus si une seule liaison est prévue par paire.

### Étape 2 — Identifier les sous-réseaux

Attribue un sous-réseau à chaque groupe si la segmentation souhaitée l’exige. Par exemple, pour un exercice uniquement :

- Web : `10.20.10.0/24` ;
- Applicatif : `10.20.20.0/24` ;
- Base de données : `10.20.30.0/24`.

Ce sont des exemples de documentation, pas une recommandation universelle. Le plan réel doit tenir compte des adresses déjà utilisées, des passerelles, des services partagés et des politiques de sécurité.

### Étape 3 — Définir les flux permis

Avant de configurer, écris les communications attendues. Exemple pédagogique :

| Source | Destination | Autorisation attendue | Exemple d’usage |
|---|---|---|---|
| Utilisateurs autorisés | Web | Oui | HTTPS vers le site |
| Web | Applicatif | Oui | Port d’application défini par l’équipe |
| Applicatif | Base de données | Oui | Port du moteur de base de données |
| Web | Base de données directement | Non, par défaut dans cet exercice | Réduire les accès directs |
| Réseau non autorisé | Serveurs internes | Non | Limiter l’exposition |

Le tableau définit une intention. Il ne configure pas les règles. Les numéros de ports exacts dépendent des applications et doivent être validés par leur documentation.

### Étape 4 — Vérifier l’accès et le routage

Contrôle d’abord les liaisons physiques et l’état des interfaces, puis les adresses IP, les passerelles et les routes. Vérifie que les serveurs rejoignent leur passerelle et que les Leaf apprennent ou possèdent les routes nécessaires. Ne commence pas par modifier plusieurs politiques en même temps : change un élément, teste, observe le résultat et conserve une trace.

### Étape 5 — Tester les chemins positifs et négatifs

Un test positif vérifie qu’un flux autorisé fonctionne. Un test négatif vérifie qu’un flux interdit échoue comme prévu. Une bonne validation comprend les deux. Si tous les flux fonctionnent, cela peut indiquer que les règles sont trop permissives ; si aucun flux ne fonctionne, la cause peut être le câblage, l’adressage, le routage ou la sécurité.

### Étape 6 — Tester la redondance avec méthode

Dans un vrai laboratoire, planifie une fenêtre de test, informe les personnes concernées et prévois une procédure de retour arrière. Coupe un seul lien prévu au test, observe les alarmes et le comportement des flux, puis rétablis le lien avant de tester une autre panne. Ne désactive pas plusieurs composants simultanément sans plan : tu ne pourrais pas attribuer clairement la cause du résultat.

## 16. Dépannage méthodique

Quand une communication ne passe pas, progresse de la couche physique vers les fonctions logiques. Cette méthode limite les changements inutiles.

### 16.1 Étape A — Vérifier le physique

- Les deux extrémités du lien sont-elles connectées aux bons ports ?
- Les voyants et l’état de l’interface indiquent-ils un lien actif ?
- Les modules optiques et câbles sont-ils compatibles avec les ports et les vitesses ?
- Une interface est-elle désactivée administrativement ?
- Les erreurs CRC, pertes ou changements d’état sont-ils anormaux ?

Un lien peut être en état actif tout en subissant des erreurs. Il faut consulter les compteurs et les journaux, pas seulement se fier au voyant.

### 16.2 Étape B — Vérifier la topologie

- Chaque Leaf rejoint-il le Spine attendu ?
- Les liens sont-ils connectés au bon équipement ?
- Le nombre de liens correspond-il au dessin ?
- Un changement de câblage récent a-t-il été documenté ?
- Une panne de Spine a-t-elle supprimé une partie des chemins prévus ?

Compare l’état réel de la fabric au schéma de référence. Le schéma doit être mis à jour après les changements autorisés.

### 16.3 Étape C — Vérifier l’adressage et le routage

- L’adresse IP et le masque du serveur sont-ils corrects ?
- La passerelle est-elle joignable ?
- La table de routage contient-elle un chemin vers le réseau destination ?
- Les interfaces routées des deux extrémités sont-elles correctement adressées ?
- Le protocole de routage est-il opérationnel et les routes sont-elles installées ?
- Le réseau distant possède-t-il le chemin retour ?

Ne confonds pas la réponse à un ping avec le bon fonctionnement de tous les services. ICMP peut être filtré alors qu’un port applicatif fonctionne, ou au contraire un ping peut réussir alors que le service attendu ne répond pas.

### 16.4 Étape D — Vérifier la politique

Un flux peut échouer alors que les routes sont correctes. Vérifie les listes de contrôle d’accès, les règles de pare-feu, les politiques de segmentation, les groupes de sécurité ou les contrats de plateforme selon la solution utilisée.

Vérifie les deux sens lorsqu’un pare-feu avec suivi d’état ou une politique directionnelle intervient. Confirme que le protocole, le port, la source et la destination correspondent exactement à la règle prévue. Évite d’autoriser temporairement tous les flux comme réflexe de dépannage : cela peut masquer la cause et introduire un risque.

### 16.5 Étape E — Vérifier la capacité et les compteurs

Des pertes peuvent apparaître en cas de congestion ou de problème physique. Observe l’utilisation des liens, les files d’attente, les compteurs de drops, les erreurs, la latence et les tendances dans le temps. Une seule capture instantanée peut manquer un pic bref ; compare l’observation aux heures où l’application rencontre réellement le problème.

### 16.6 Utiliser une matrice de diagnostic

| Symptôme | Causes possibles | Première vérification |
|---|---|---|
| Aucun lien physique | Câble, optique, port désactivé, vitesse incompatible | État des interfaces et diagnostics optiques |
| Le serveur ne joint pas sa passerelle | VLAN/port d’accès, IP, masque, passerelle, politique locale | Configuration IP et port du Leaf |
| Même Leaf, communication impossible | Segment ou politique locale, mauvais VLAN, service indisponible | Table MAC, adressage et règles |
| Communication entre deux Leaf impossible | Lien Leaf-Spine, routes, MTU selon l’encapsulation, politique | État des uplinks, routes et tests de bout en bout |
| Aller fonctionne, retour échoue | Route retour, règle directionnelle, routage asymétrique, pare-feu | Tables de routage et journaux dans les deux sens |
| Connexion lente ou intermittente | Congestion, erreurs physiques, hachage déséquilibré, serveur surchargé | Compteurs, utilisation des liens et mesures applicatives |
| Panne d’un Spine sans reprise attendue | Lien de secours absent/inactif, convergence, configuration | Cartographie des liens et état du routage |

## 17. Bonnes pratiques de conception et d’exploitation

### 17.1 Documenter avant de câbler

Maintiens une liste des switches, ports, numéros de baies, liens, vitesses, modules optiques et destinations. Utilise des noms cohérents tels que `LEAF-01`, `LEAF-02`, `SPINE-01` et `SPINE-02`. Évite de nommer les appareils uniquement selon une position temporaire si elle risque de changer.

### 17.2 Standardiser sans copier aveuglément

Les configurations standards limitent les différences accidentelles. Toutefois, ne copie pas une configuration sans examiner les adresses, identifiants, rôles, ports et paramètres propres à l’équipement. Un modèle réutilisable doit prévoir les variables et les validations.

### 17.3 Garder une marge de capacité

Ne dimensionne pas une fabric uniquement à partir des besoins mesurés aujourd’hui. Prends en compte l’augmentation du nombre de serveurs, les sauvegardes, les mises à jour, les pics de trafic et les changements d’application. La marge doit être chiffrée et documentée, pas choisie au hasard.

### 17.4 Surveiller la santé du réseau

Les éléments utiles comprennent l’état des liens, les erreurs, les pertes, l’utilisation, la température et l’alimentation des équipements, les sessions de routage, les changements de topologie et les alarmes. Configure des seuils proportionnés à l’environnement : un seuil trop sensible crée du bruit, un seuil trop élevé retarde la détection.

### 17.5 Faire des changements réversibles

Avant un changement, rédige : objectif, périmètre, dépendances, risque, plan de test, fenêtre d’intervention et procédure de retour arrière. Modifie une partie limitée du réseau puis vérifie le résultat. La fabric est interconnectée ; une modification apparemment locale peut toucher plusieurs services.

### 17.6 Sécuriser l’administration

Restreins les accès de gestion aux personnes et réseaux autorisés. Utilise des comptes individuels, une authentification forte lorsque disponible, des rôles adaptés, des journaux et des sauvegardes de configuration. Le plan d’administration ne doit pas être confondu avec les chemins de données des applications.

## 18. Idées reçues à éviter

**« Spine/Leaf est un protocole. »** Non. C’est une architecture de topologie ; les protocoles de routage, l’overlay et les politiques sont des choix séparés.

**« Les serveurs se branchent sur les Spine. »** Dans le modèle classique à deux niveaux, les serveurs se connectent aux Leaf. Certains designs multi-tiers peuvent ajouter des couches, mais ils ne doivent pas être confondus avec la topologie de base.

**« Deux Spine garantissent zéro interruption. »** Non. Ils offrent des chemins alternatifs lorsque le câblage, les protocoles et la capacité sont conçus pour cela. Une détection de panne, une convergence ou une limitation de capacité peut toujours affecter le service.

**« Tous les flux sont répartis à parts égales. »** Non. ECMP peut partager des flux entre chemins de coût égal, mais le hachage et les caractéristiques des flux influencent la distribution.

**« VXLAN est obligatoire. »** Non. VXLAN est une technologie couramment utilisée dans certains designs d’overlay ; une fabric Spine/Leaf peut aussi être une architecture IP routée sans VXLAN.

**« Si le ping passe, le réseau est parfait. »** Non. Il faut aussi vérifier les services, ports, performances, règles de sécurité, perte de paquets et comportements en cas de panne.

**« Tous les Leaf doivent avoir les mêmes serveurs. »** Non. Les Leaf peuvent connecter des types d’équipements et des profils de ports différents, selon les contraintes du design. La standardisation est utile, mais n’impose pas une uniformité absolue.

## 19. Glossaire

- **Adresse MAC :** identifiant de couche 2 utilisé dans les trames Ethernet.
- **Adresse IP :** adresse logique utilisée pour communiquer au niveau IP.
- **Bande passante / débit de lien :** capacité nominale de transport d’un lien, par exemple 100 Gbit/s.
- **BD / broadcast :** domaine dans lequel une trame de broadcast de couche 2 est diffusée ; sa portée dépend de la segmentation et de la conception.
- **Border Leaf :** Leaf chargé de relier la fabric à des réseaux externes dans certains designs.
- **Clos :** famille de structures de réseau multi-étages dont l’architecture Leaf-Spine moderne est un exemple courant.
- **ECMP :** mécanisme qui permet d’utiliser plusieurs chemins de routage de coût égal.
- **EoR :** *End of Row*, équipement qui dessert une rangée de baies.
- **Est-ouest :** échanges entre serveurs ou composants internes d’un data center.
- **Fabric :** ensemble cohérent de switches et de liens interconnectés.
- **Latence :** délai entre l’émission et la réception des données.
- **Leaf :** switch d’accès à la fabric, généralement connecté aux serveurs et appliances.
- **Nord-sud :** échanges entre le data center et l’extérieur.
- **Overlay :** réseau logique construit au-dessus d’un réseau de transport.
- **Oversubscription :** rapport entre capacité agrégée en entrée et capacité disponible vers un niveau supérieur.
- **Spine :** switch de transit reliant les Leaf.
- **ToR :** *Top of Rack*, switch installé dans ou au sommet d’une baie.
- **Underlay :** réseau de transport sous-jacent.
- **Uplink :** lien montant d’un Leaf vers un Spine dans le modèle de base.
- **VLAN :** segmentation logique de couche 2.
- **VTEP :** point de terminaison d’un tunnel VXLAN.
- **VXLAN :** technologie d’encapsulation de trames Ethernet dans UDP/IP.

## 20. Quiz de validation

Réponds avant de consulter le corrigé.

1. Quel est le rôle principal d’un Leaf ?
2. Quel est le rôle principal d’un Spine ?
3. Dans une fabric classique à deux niveaux, un serveur se connecte-t-il au Spine ou au Leaf ?
4. Combien de liens Leaf-Spine faut-il dans le modèle simple pour quatre Leaf et trois Spine, avec une seule liaison par paire ?
5. Que signifie le trafic est-ouest ?
6. Que signifie ECMP ?
7. Deux Spine suffisent-ils à garantir l’absence de toute interruption en cas de panne ?
8. Une architecture Spine/Leaf impose-t-elle VXLAN ?
9. Pourquoi faut-il vérifier le chemin retour ?
10. Cite trois vérifications à réaliser avant de conclure qu’un problème vient du routage.

### Corrigé

1. Le Leaf connecte les serveurs et autres équipements terminaux à la fabric.
2. Le Spine assure le transit entre Leaf.
3. Au Leaf dans le modèle de base.
4. `4 × 3 = 12` liens.
5. Le trafic entre des composants internes, par exemple deux serveurs du data center.
6. *Equal-Cost Multipath* : plusieurs chemins de coût égal.
7. Non. Il faut aussi des liens opérationnels, un mécanisme de convergence, des routes cohérentes et une capacité suffisante.
8. Non. VXLAN est une option technologique utilisée dans certains designs.
9. Parce que le réseau distant doit également savoir comment retourner vers la source et parce que les politiques peuvent différer dans chaque sens.
10. Exemples : état physique des interfaces, adressage IP/masque, passerelle, routes, port/VLAN, règles de sécurité, compteurs d’erreurs et disponibilité du service.

## 21. Exercices pratiques

### Exercice A — Vérification de topologie

Dessine trois Spine et cinq Leaf en utilisant une seule liaison par paire. Calcule le nombre de liens. Ensuite, retire le Spine 2 de ton schéma et identifie quels liens restent. Explique pourquoi la perte d’un Spine ne doit pas nécessairement isoler les serveurs si les autres liaisons sont opérationnelles.

**Attendu :** `3 × 5 = 15` liaisons dans le dessin complet. Après retrait du Spine 2, il reste deux liaisons Spine par Leaf, soit dix liens vers les deux Spine restants.

### Exercice B — Analyse d’une communication

Serveur A est connecté à Leaf 1. Serveur B est connecté à Leaf 2. Ils sont dans des sous-réseaux différents. Liste les contrôles à effectuer avant de conclure que l’uplink Leaf-Spine est en cause.

**Attendu :** vérifier l’état des ports et du lien serveur, le VLAN ou réseau d’accès, l’adresse et le masque, la passerelle, le service de destination, les routes aller et retour, les politiques et les compteurs. Les détails exacts dépendent de l’architecture.

### Exercice C — Ratio de surabonnement

Un Leaf possède 32 ports serveurs de 10 Gbit/s et quatre uplinks de 40 Gbit/s. Calcule la capacité théorique agrégée côté serveurs et côté uplinks puis le ratio simplifié.

**Correction :** `32 × 10 = 320 Gbit/s` côté serveurs ; `4 × 40 = 160 Gbit/s` côté uplinks ; `320 / 160 = 2`, donc un ratio théorique de **2:1**. Cela ne prédit pas à lui seul le débit d’une application ni la distribution réelle du trafic.

### Exercice D — Petit plan de câblage

Prépare un tableau comportant au minimum : identifiant du switch source, port source, identifiant du switch destination, port destination, vitesse, type de câble ou optique, rôle du lien et état observé. Remplis-le pour deux Spine et trois Leaf. Ajoute une ligne par lien physique. Fais vérifier ton tableau par une autre personne avant toute intervention réelle.

### Exercice E — Diagnostic écrit

Un serveur arrive à joindre sa passerelle mais ne peut pas joindre un serveur derrière un autre Leaf. Écris une séquence de diagnostic sans modifier immédiatement la configuration.

**Attendu :** confirmer la destination et le service testé ; vérifier le routage et le chemin retour ; vérifier les liaisons Leaf-Spine et les sessions de routage ; examiner les règles de sécurité ; lire les compteurs et journaux ; comparer avec un flux qui fonctionne ; puis proposer un changement limité, testé et réversible.

## 22. Résumé à retenir

L’architecture Spine/Leaf organise un data center autour de deux rôles : le **Leaf** relie les équipements terminaux et le **Spine** transporte le trafic entre les Leaf. Dans une fabric à deux niveaux standard, chaque Leaf est connecté à chaque Spine, ce qui donne des chemins réguliers et permet de concevoir de la redondance. Le nombre de chemins, la vitesse des liens, le routage, ECMP, l’overlay éventuel et les politiques de sécurité sont des sujets distincts qu’il faut concevoir ensemble.

Le schéma physique explique où se trouvent les équipements et comment ils sont reliés ; il ne suffit pas à prouver qu’un flux fonctionne. Pour diagnostiquer, vérifie dans l’ordre le câblage et l’état des interfaces, la topologie, l’adressage, les routes, les politiques, puis la capacité et les compteurs. Pour concevoir correctement, documente les liens, dimensionne les uplinks en fonction des applications, teste les scénarios de panne et prévois une procédure de retour arrière.

## 23. Pour aller plus loin

Ces ressources officielles apportent des détails sur les fabrics de data center et leurs variantes. Les guides des fabricants sont à consulter avec la référence exacte du matériel et de la version logicielle déployée.

- [Cisco — Massively Scalable Data Center Network Fabric Design and Operation](https://www.cisco.com/c/en/us/td/docs/solutions/Enterprise/Data_Center/DC_Infra2_5/DCInfra_1.html) : principes de fabric IP, Leaf-Spine, routage ECMP et considérations de capacité.
- [Cisco — Network Topology](https://www.cisco.com/c/en/us/learn/topics/networking/what-is-network-topology.html) : présentation des topologies de réseau, dont Spine-and-Leaf.
- [Cisco — Application Centric Infrastructure Design Guide](https://www.cisco.com/c/en/us/td/docs/dcn/whitepapers/cisco-application-centric-infrastructure-design-guide.html) : exemple d’application de cette topologie dans une fabric Cisco ACI. Ce guide décrit une solution particulière ; ses fonctionnalités propres ne sont pas automatiquement présentes dans toutes les fabrics Spine/Leaf.
- [Cisco — Nondisruptive Data Center System Maintenance Best Practices](https://www.cisco.com/c/en/us/products/collateral/switches/nexus-9000-series-switches/white-paper-c11-743731.html) : notions de fabric IP, VXLAN/EVPN et bonnes pratiques de maintenance.

**Règle finale :** commence par comprendre les deux couches, dessine tous les liens attendus, suis un paquet étape par étape, puis valide séparément le physique, le routage, les politiques et les performances. Une bonne topologie facilite le réseau ; une configuration et une exploitation rigoureuses le rendent fiable.
