<style>
.aci2-diagram{width:100%;max-width:100%;overflow-x:auto;margin:1.25rem 0;padding:.75rem;border:1px solid #263b54;border-radius:14px;background:#080f19;color:#e8eef7;box-sizing:border-box}
.aci2-diagram svg{display:block;width:100%;height:auto;min-width:760px}
.aci2-diagram .flow{stroke-dasharray:8 7;animation:aci2Dash 1.8s linear infinite}
.aci2-diagram .pulse{animation:aci2Pulse 2.2s ease-in-out infinite}
@keyframes aci2Dash{to{stroke-dashoffset:-30}}
@keyframes aci2Pulse{0%,100%{opacity:.55}50%{opacity:1}}
@media(max-width:720px){.aci2-diagram svg{min-width:760px}}
@media(prefers-reduced-motion:reduce){.aci2-diagram *{animation:none!important}}
</style>
# Cisco ACI : Fabric et Politiques — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Domaine :** Réseaux de data center, fabric leaf-spine, modèle de politiques Cisco ACI  
**Prérequis :** connaître les rôles des leaf/spine, APIC, tenants, VRF, bridge domains, EPG et contrats. Ce cours approfondit la résolution des politiques, le chemin des paquets, l’accès externe et le diagnostic.

## Objectifs pédagogiques

À la fin du cours, tu devrais pouvoir :
- reconstruire le chemin d’un flux entre deux endpoints connectés à des leaf différents ;
- distinguer les relations de containment et les relations entre objets ACI ;
- concevoir des contrats minimaux entre EPG ;
- expliquer le rôle du pcTag et des zoning-rules sans confondre control plane et dataplane ;
- analyser les relations entre BD, VRF, sous-réseaux et passerelles ;
- diagnostiquer un flux bloqué en séparant problème de connectivité et problème de politique ;
- préparer une modification avec critères de validation et retour arrière.

> **Analogie :** le modèle ACI ressemble à un système de transport dont les terminaux, les lignes et les règles d’accès sont décrits séparément. Les endpoints sont les voyageurs, la fabric transporte les paquets, les EPG les classe, les contrats définissent les flux permis, et les leaf appliquent la politique résolue. Une route disponible ne signifie pas qu’un trajet est autorisé par la politique.


## 1. Réviser les fondamentaux sans rester au niveau débutant

### 1.1 Deux plans à distinguer

Le **plan de gestion** est utilisé pour définir et observer la configuration, généralement via l’APIC et ses API. Le **plan de contrôle** échange ou maintient les informations nécessaires à la fabric : découverte, reachability des endpoints, routes et état des liens selon les mécanismes ACI. Le **plan de données** est le chemin matériel qui transporte réellement les paquets et applique les règles programmées.

Ces plans coopèrent, mais ils ne sont pas interchangeables. Une configuration présente dans l’interface ne prouve pas à elle seule que le dataplane la traite comme prévu. Il faut vérifier la résolution de la politique, son déploiement sur les leaf concernés, puis les compteurs ou traces disponibles.

### 1.2 La topologie leaf-spine et les limites du chemin

Les endpoints se connectent normalement aux leaf. Les spine assurent la connectivité entre leaf. Dans la topologie leaf-spine ACI standard, les liens leaf-spine forment le tissu de transport ; on ne doit pas dessiner un chemin normal de données qui saute directement d’un leaf à un autre ou passe par un spine relié directement à un serveur.

Un flux entre deux endpoints sur le même leaf peut être traité localement. Un flux entre deux leaf utilise le fabric underlay et l’encapsulation overlay appropriée. Le chemin exact dépend de la localisation des endpoints, de la topologie et de la résolution de forwarding ; il ne faut donc pas présenter un seul spine comme un passage obligatoire dans tous les cas, car le fabric peut utiliser plusieurs chemins ECMP.


<div class="aci2-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 450" role="img" aria-label="Schéma technique Cisco ACI" preserveAspectRatio="xMidYMid meet"><defs><marker id="a2blue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#38bdf8"/></marker><marker id="a2green" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#34d399"/></marker><marker id="a2amber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#fbbf24"/></marker><marker id="a2red" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#fb7185"/></marker></defs><text x="500" y="28" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21">Schéma 1 — Chemin physique et logique d’un flux inter-leaf</text><rect x="95" y="48" width="810" height="280" rx="18" fill="#0b1726" stroke="#64748b" stroke-dasharray="7 6"/><text x="500" y="70" text-anchor="middle" fill="#93c5fd" font-size="16" font-family="Arial" font-weight="700">Fabric ACI (underlay + overlay VXLAN)</text><rect x="220" y="88" width="160" height="60" rx="12" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="300.0" y="113" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Spine 1</text><text x="300.0" y="133" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Transit IP</text><rect x="620" y="88" width="160" height="60" rx="12" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="700.0" y="113" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Spine 2</text><text x="700.0" y="133" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Transit IP</text><rect x="125" y="225" width="180" height="65" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="215.0" y="250" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Leaf A</text><text x="215.0" y="270" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">VTEP source</text><rect x="410" y="225" width="180" height="65" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="500.0" y="250" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Leaf B</text><text x="500.0" y="270" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">VTEP transit/destination</text><rect x="695" y="225" width="180" height="65" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="785.0" y="250" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Leaf C</text><text x="785.0" y="270" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Autre endpoint</text><path d="M250 225 L285 148" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><path d="M285 148 L460 225" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><path d="M300 148 L520 225" fill="none" stroke="#38bdf8" stroke-width="2.4" class="flow" marker-end="url(#a2blue)"/><path d="M700 148 L520 225" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><path d="M700 148 L785 225" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><rect x="110" y="350" width="210" height="55" rx="12" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="215.0" y="375" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Serveur source</text><text x="215.0" y="395" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">EPG-Web / VLAN local</text><rect x="390" y="350" width="220" height="55" rx="12" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="500.0" y="375" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Serveur destination</text><text x="500.0" y="395" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">EPG-App / autre leaf</text><rect x="680" y="350" width="210" height="55" rx="12" fill="#302313" stroke="#fbbf24" stroke-width="1.6"/><text x="785.0" y="375" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Serveur tiers</text><text x="785.0" y="395" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">EPG-DB / isolé par défaut</text><path d="M215 350 L215 291" fill="none" stroke="#34d399" stroke-width="2.4" class="flow" marker-end="url(#a2green)"/><path d="M500 350 L500 291" fill="none" stroke="#34d399" stroke-width="2.4" class="flow" marker-end="url(#a2green)"/><path d="M785 350 L785 291" fill="none" stroke="#fbbf24" stroke-width="2.4" class="flow" marker-end="url(#a2amber)"/><text x="500" y="430" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="13">Le trafic inter-leaf traverse un spine ; le spine ne se connecte pas directement aux endpoints.</text></svg></div>


### 1.3 Underlay, overlay et VXLAN

L’**underlay** est l’infrastructure IP qui relie les équipements de la fabric et permet aux VTEP de se joindre. L’**overlay** fournit la représentation logique des segments et des politiques au-dessus de cette infrastructure. Dans ACI, VXLAN est un mécanisme central de transport overlay ; il permet de transporter le trafic logique entre points de terminaison de la fabric sans devoir étendre chaque VLAN de bout en bout sur tout le réseau physique.

Sur le leaf d’entrée, ACI identifie l’endpoint et son groupe, applique la politique pertinente et encapsule le trafic pour le transport fabric lorsque nécessaire. Le leaf de sortie reçoit le paquet, retire l’encapsulation et transmet le paquet vers l’endpoint destinataire. Les détails internes dépendent de la plateforme et de la version ; le modèle utile pour le dépannage est de distinguer l’encapsulation du transport, la classification des endpoints et la décision de politique.

### 1.4 Pourquoi les flèches des schémas comptent

Dans une fabric, une ligne sans direction peut être comprise comme une simple liaison physique, un flux de données ou une relation d’objet. Ces significations doivent être séparées :
- **liaison physique** : lien leaf-spine, souvent bidirectionnel en pratique, dessiné comme une liaison sans flèche de flux si l’objectif est uniquement la topologie ;
- **flux de paquets** : flèche orientée de la source vers la destination ;
- **relation d’objet** : trait indiquant une association de configuration, pas le trajet d’un paquet ;
- **règle de contrat** : relation provider/consumer et filtres applicables, pas un tunnel réseau.

Les schémas de ce cours indiquent explicitement le sens des flux lorsqu’il est important. Les lignes pointillées animées représentent des flux logiques, tandis que les liaisons de structure restent statiques. Aucun point animé isolé n’est utilisé comme substitut d’un chemin : l’animation est appliquée aux véritables traits du diagramme.

## 2. Le modèle d’objets : containment, association et portée

### 2.1 Tenant : conteneur logique, pas réseau privé à lui seul

Un tenant regroupe les politiques et objets logiques d’une organisation, d’une application ou d’un domaine administratif. Il peut contenir plusieurs VRF, BD, Application Profiles, EPG, contrats, filtres et objets de connectivité externe. Un tenant représente une frontière de gestion et de politique ; il ne signifie pas automatiquement qu’un réseau IP privé distinct a été créé.

Le tenant `common` contient des objets partagés disponibles selon les règles de résolution et les relations configurées. Il faut éviter de placer des objets dans `common` uniquement pour contourner un problème de résolution : un objet partagé doit avoir une intention claire, un propriétaire et une portée documentée.

### 2.2 VRF / Context

Une VRF est un domaine de forwarding Layer 3. Elle contient l’espace de routage dans lequel les préfixes sont interprétés et les décisions de routage prises. Une VRF peut être associée à plusieurs BD ; ces BD peuvent représenter différents sous-réseaux ou segments de niveau 2 qui partagent le même domaine de routage.

Deux endpoints dans la même VRF peuvent avoir une possibilité de routage IP entre eux, mais cela ne veut pas dire que leur communication inter-EPG est autorisée. En mode de politique enforced, la segmentation ACI impose généralement un contrat pour la communication entre EPG distincts. Il faut donc analyser séparément la reachability L2/L3 et l’autorisation de sécurité.

### 2.3 Bridge Domain

Le BD définit un domaine de bridging et porte des options influençant le comportement Layer 2 et, selon la configuration, la fonction de routage et l’apprentissage IP. Il est associé à une VRF. Les sous-réseaux et passerelles configurés sous le BD déterminent notamment les paramètres IP utilisés par les endpoints de ce segment.

Un BD n’est pas synonyme d’EPG. Le BD définit des propriétés de connectivité L2/L3 ; l’EPG classe des endpoints qui partagent une politique. Plusieurs EPG peuvent être associés au même BD dans certains designs. Cette séparation est importante : deux endpoints dans le même BD peuvent appartenir à des EPG distincts et donc relever de politiques différentes.

### 2.4 Application Profile et EPG

Un Application Profile regroupe des EPG correspondant souvent aux couches d’une application : Web, App, DB, services de support. Ce regroupement facilite la lecture et l’administration, mais il n’impose pas à lui seul les autorisations entre groupes.

Un EPG rassemble des endpoints qui partagent des exigences de politique. Les endpoints peuvent être des serveurs physiques, des machines virtuelles ou d’autres entités prises en charge. L’appartenance peut être liée à un chemin statique, à un domaine d’intégration ou à des mécanismes dynamiques selon le type de déploiement.

Un EPG est une abstraction de politique, pas un appareil physique ni nécessairement un VLAN unique à travers toute la fabric. Les détails d’association entre EPG, domaine, VLAN pool, AEP et chemin doivent être cohérents pour que l’EPG soit effectivement déployé là où les endpoints se connectent.

### 2.5 Relations explicites entre objets

Le modèle ACI contient à la fois des objets parents-enfants et des relations entre objets qui ne sont pas dans une hiérarchie directe. Par exemple, un EPG référence un BD par une relation ; un EPG peut consommer ou fournir un contrat ; un BD référence une VRF. Un schéma pédagogique doit donc éviter de présenter tous les objets comme une simple chaîne parent-enfant.

**Règle de lecture :** demande-toi si le trait signifie « contient », « référence », « consomme », « fournit » ou « transporte le paquet ». Si la réponse n’est pas claire, le schéma est ambigu.


<div class="aci2-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 420" role="img" aria-label="Relations entre objets Cisco ACI" preserveAspectRatio="xMidYMid meet"><defs><marker id="b" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#38bdf8"/></marker><marker id="g" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#34d399"/></marker><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#fbbf24"/></marker></defs><text x="500" y="28" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21">Schéma 2 — Objets et relations de politique ACI</text><rect x="390" y="48" width="220" height="48" rx="11" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="500.0" y="72" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">Tenant</text><text x="500.0" y="91" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Conteneur logique</text><path d="M500 96 L500 122" fill="none" stroke="#38bdf8" stroke-width="2.3" marker-end="url(#b)"/><rect x="390" y="122" width="220" height="50" rx="11" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="500.0" y="146" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">VRF / Context</text><text x="500.0" y="165" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Domaine de routage L3</text><path d="M500 172 L500 205" fill="none" stroke="#38bdf8" stroke-width="2.3" marker-end="url(#b)"/><rect x="390" y="205" width="220" height="50" rx="11" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="500.0" y="229" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">Bridge Domain</text><text x="500.0" y="248" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Segment L2 ; associé à une VRF</text><path d="M390 72 L225 72 L225 105" fill="none" stroke="##34d399" stroke-width="2.3" marker-end="url(#g)"/><rect x="70" y="105" width="310" height="56" rx="11" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="225.0" y="129" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">Application Profile</text><text x="225.0" y="148" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Contient les EPG de l’application</text><path d="M225 161 L225 195" fill="none" stroke="#38bdf8" stroke-width="2.3" marker-end="url(#b)"/><rect x="70" y="195" width="310" height="56" rx="11" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="225.0" y="219" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">EPG Web / App / DB</text><text x="225.0" y="238" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Appartient à l’Application Profile</text><path d="M390 230 L350 230" fill="none" stroke="##38bdf8" stroke-width="2.3" stroke-dasharray="7 6" class="flow" marker-end="url(#b)"/><path d="M610 230 L650 230" fill="none" stroke="##38bdf8" stroke-width="2.3" stroke-dasharray="7 6" class="flow" marker-end="url(#b)"/><rect x="650" y="202" width="280" height="56" rx="11" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="790.0" y="226" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">Subnet / passerelle BD</text><text x="790.0" y="245" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Paramètres IP associés au BD</text><path d="M225 251 L225 300" fill="none" stroke="#38bdf8" stroke-width="2.3" marker-end="url(#b)"/><rect x="70" y="300" width="310" height="58" rx="11" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="225.0" y="324" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">Association EPG → BD</text><text x="225.0" y="343" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Relation de référence, pas parenté</text><rect x="650" y="300" width="280" height="58" rx="11" fill="#302313" stroke="#fbbf24" stroke-width="1.6"/><text x="790.0" y="324" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">Contrat → Subject → Filter</text><text x="790.0" y="343" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Politique de communication EPG</text><path d="M380 329 L650 329" fill="none" stroke="#fbbf24" stroke-width="2.3" stroke-dasharray="7 6" class="flow" marker-end="url(#a)"/><text x="500" y="390" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="13">Tenant contient les objets ; les traits latéraux indiquent des associations distinctes.</text></svg></div>


## 3. Contrats : transformer une exigence en politique ACI

### 3.1 Le modèle provider / consumer

Un contrat décrit les communications qu’un EPG provider offre à un EPG consumer. Le provider expose un service ; le consumer consomme ce service. Cette relation exprime l’intention de politique et ne signifie pas que les paquets ne circulent que dans un sens au niveau applicatif : le trafic de réponse peut être traité selon les règles et mécanismes applicables au flux, aux filtres et à la plateforme.

Exemple : l’EPG-Web consomme un contrat HTTPS fourni par l’EPG-App. Le contrat définit le protocole TCP et le port destination 443. L’EPG-App ne doit pas être autorisé à initier arbitrairement tous les flux vers l’EPG-Web simplement parce qu’il est provider d’un contrat HTTPS. Il faut comprendre le sens des filtres et le modèle de communication voulu.

### 3.2 Contract, subject, filter et filter entry

Un contrat peut contenir un ou plusieurs subjects. Le subject associe les filtres et définit notamment la manière dont leur direction est interprétée. Un filtre regroupe des critères de correspondance ; les entrées de filtre peuvent décrire le protocole, les ports L4 et d’autres champs pris en charge.

Pour un besoin « Web vers App sur HTTPS », documente au minimum :
1. EPG consumer : `EPG-Web` ;
2. EPG provider : `EPG-App` ;
3. protocole : TCP ;
4. port : 443 côté destination ;
5. direction du filtre et comportement attendu pour les réponses ;
6. éventuelles exigences de logging, de priorité et de réutilisation ;
7. flux qui doivent rester interdits.

Ne crée pas un filtre « any » simplement parce qu’un test ne fonctionne pas. Cela peut masquer la cause et élargir dangereusement la surface d’accès. Commence par vérifier l’apprentissage des endpoints, le routage et la correspondance des ports.

### 3.3 Politique allow-list et refus par défaut

Le modèle ACI est généralement conçu autour d’une approche allow-list : les communications entre EPG distincts sont permises selon les contrats et les politiques configurés. En l’absence de contrat applicable, le trafic inter-EPG est généralement bloqué lorsque la VRF est en mode enforced. Il existe des mécanismes et exceptions de conception — par exemple preferred groups, `vzAny`, VRF unenforced ou services partagés — qui modifient la portée de la politique ; ils doivent être compris et documentés, pas utilisés par défaut comme raccourci.

La communication au sein d’un même EPG n’a pas besoin d’un contrat inter-EPG standard. Cela ne remplace pas les contrôles de sécurité de l’hôte, les pare-feu locaux ou les contrôles applicatifs. L’appartenance au même EPG ne signifie pas que l’application est intrinsèquement sûre.

### 3.4 Réutilisation et portée des contrats

Un contrat peut être réutilisé par plusieurs EPG. Cette réutilisation diminue la duplication mais peut créer une dépendance cachée : modifier un contrat partagé peut affecter de nombreux consommateurs et fournisseurs. Avant une modification, recherche toutes les relations du contrat, identifie les flux existants, puis teste les cas attendus et les cas qui doivent rester refusés.

Les contrats inter-tenants et services partagés nécessitent une attention supplémentaire : les relations de contrat, les objets de service partagé, les sous-réseaux et leur portée doivent correspondre à la conception. Ne suppose pas qu’un contrat créé dans un tenant est automatiquement consommable par tous les autres tenants.

### 3.5 Taboo, exceptions et preferred groups

Les mécanismes avancés qui affinent ou remplacent le comportement allow-list standard peuvent rendre une politique difficile à lire. Les taboo contracts, les exceptions de contrat et les preferred groups ont des comportements et des limites propres aux versions et plateformes. Utilise-les seulement si le besoin est explicite et après lecture de la documentation correspondant à la release installée.

Le bon objectif est de rendre la politique compréhensible : quels EPG peuvent communiquer, quel contrat le permet, quel filtre correspond au paquet et pourquoi le flux est autorisé ou refusé. Une politique qui ne peut être expliquée simplement devient coûteuse à dépanner.


<div class="aci2-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 465" role="img" aria-label="Schéma technique Cisco ACI" preserveAspectRatio="xMidYMid meet"><defs><marker id="a2blue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#38bdf8"/></marker><marker id="a2green" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#34d399"/></marker><marker id="a2amber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#fbbf24"/></marker><marker id="a2red" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#fb7185"/></marker></defs><text x="500" y="28" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21">Schéma 3 — Résolution d’un contrat entre EPG</text><rect x="55" y="100" width="190" height="72" rx="12" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="150.0" y="125" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Client Web</text><text x="150.0" y="145" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">EPG-Web · consumer</text><rect x="405" y="100" width="190" height="72" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="500.0" y="125" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Application</text><text x="500.0" y="145" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">EPG-App · provider</text><rect x="755" y="100" width="190" height="72" rx="12" fill="#302313" stroke="#fbbf24" stroke-width="1.6"/><text x="850.0" y="125" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Base de données</text><text x="850.0" y="145" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">EPG-DB · provider</text><rect x="270" y="230" width="190" height="78" rx="12" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="365.0" y="255" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Contrat Web-App</text><text x="365.0" y="275" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Subject HTTPS · TCP/443</text><rect x="620" y="230" width="190" height="78" rx="12" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="715.0" y="255" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Contrat App-DB</text><text x="715.0" y="275" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Subject SQL · TCP/5432</text><path d="M150 172 L320 230" fill="none" stroke="#34d399" stroke-width="2.4" class="flow" marker-end="url(#a2green)"/><path d="M500 172 L405 230" fill="none" stroke="#38bdf8" stroke-width="2.4" class="flow" marker-end="url(#a2blue)"/><path d="M500 172 L710 230" fill="none" stroke="#38bdf8" stroke-width="2.4" class="flow" marker-end="url(#a2blue)"/><path d="M850 172 L710 230" fill="none" stroke="#fbbf24" stroke-width="2.4" class="flow" marker-end="url(#a2amber)"/><text x="365" y="337" text-anchor="middle" fill="#34d399" font-family="Arial,sans-serif" font-size="14">HTTPS autorisé</text><text x="710" y="337" text-anchor="middle" fill="#34d399" font-family="Arial,sans-serif" font-size="14">SQL autorisé depuis App</text><rect x="300" y="365" width="400" height="52" rx="12" fill="#341722" stroke="#fb7185" stroke-width="1.6"/><text x="500.0" y="390" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">EPG-Web → EPG-DB</text><text x="500.0" y="410" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Pas de contrat dédié : refus par défaut en VRF enforced</text><path d="M150 172 L250 365 L300 390" fill="none" stroke="#fb7185" stroke-width="2.4" class="flow" marker-end="url(#a2red)"/><text x="500" y="445" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="13">Le contrat décrit les flux ; l’EPG désigne les endpoints concernés.</text></svg></div>


## 4. De l’intention APIC au dataplane : pcTag et zoning-rules

### 4.1 Classification des endpoints

L’APIC gère le modèle d’objets et la fabric apprend les endpoints et leur localisation. La politique utilise des identifiants internes de classification, souvent évoqués sous le terme **pcTag**, pour représenter les groupes ou classes de politique dans les règles déployées. Le pcTag n’est pas une adresse IP que l’administrateur doit configurer sur le serveur ; c’est un élément interne du modèle de politique ACI.

La classification dépend de la politique et des relations résolues. Si un endpoint est classé dans le mauvais EPG, un contrat pourtant correct peut ne pas s’appliquer au flux observé. Avant d’ajuster le contrat, vérifie le port, l’encapsulation, le domaine, le binding statique ou dynamique et l’EPG réellement associé à l’endpoint.

### 4.2 Zoning-rules

Les zoning-rules sont des règles de sécurité installées sur les leaf pour appliquer la politique entre classes d’endpoints. Elles représentent la traduction opérationnelle d’une partie du modèle de contrats et de relations. Le diagnostic peut inclure l’inspection des règles, des compteurs et des logs, selon la version, la plateforme et les droits d’accès.

Une règle installée n’est pas une preuve universelle que le paquet attendu correspond à cette règle. Les critères doivent coïncider : source, destination, protocole, ports, sens, EPG réellement appris et chemin du paquet. Les règles peuvent être générées par différentes fonctionnalités de politique ; il faut interpréter leur origine et leur portée plutôt que rechercher uniquement un nom de contrat.

### 4.3 Pourquoi le plan de données doit être testé séparément

Un flux peut échouer pour plusieurs raisons indépendantes :
- le serveur n’envoie pas de paquet ou utilise une mauvaise passerelle ;
- l’endpoint n’est pas appris ou se trouve dans le mauvais EPG ;
- le VLAN d’encapsulation ou le binding ne correspond pas ;
- la route ou le subnet n’est pas correct ;
- le contrat ne couvre pas le protocole ou le port réellement utilisé ;
- la politique est correcte, mais une ACL d’hôte, un pare-feu externe ou l’application bloque le trafic ;
- un service externe ou une route retour manque.

Le diagnostic doit suivre cet ordre logique : prouver que la source existe et est classée correctement, confirmer la reachability, puis inspecter la politique de sécurité. Cela évite de traiter chaque incident comme un problème de contrat.


<div class="aci2-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 465" role="img" aria-label="Schéma technique Cisco ACI" preserveAspectRatio="xMidYMid meet"><defs><marker id="a2blue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#38bdf8"/></marker><marker id="a2green" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#34d399"/></marker><marker id="a2amber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#fbbf24"/></marker><marker id="a2red" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#fb7185"/></marker></defs><text x="500" y="28" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21">Schéma 4 — De la politique aux règles installées sur les leaf</text><rect x="45" y="85" width="200" height="65" rx="12" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="145.0" y="110" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">APIC</text><text x="145.0" y="130" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Modèle et intention</text><rect x="300" y="85" width="200" height="65" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="400.0" y="110" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Résolution politique</text><text x="400.0" y="130" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">EPG / contrat / filtre</text><rect x="555" y="85" width="190" height="65" rx="12" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="650.0" y="110" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Classification</text><text x="650.0" y="130" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">pcTag / endpoint</text><rect x="800" y="85" width="155" height="65" rx="12" fill="#302313" stroke="#fbbf24" stroke-width="1.6"/><text x="877.5" y="110" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Leaf</text><text x="877.5" y="130" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Zoning rules</text><path d="M245 118 L300 118" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><path d="M500 118 L555 118" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><path d="M745 118 L800 118" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><rect x="95" y="235" width="235" height="75" rx="12" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="212.5" y="260" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Source EPG</text><text x="212.5" y="280" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">pcTag source + endpoint</text><rect x="385" y="235" width="230" height="75" rx="12" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="500.0" y="260" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Filtre de contrat</text><text x="500.0" y="280" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Protocole / ports / direction</text><rect x="670" y="235" width="235" height="75" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="787.5" y="260" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Destination EPG</text><text x="787.5" y="280" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">pcTag destination + endpoint</text><path d="M330 272 L385 272" fill="none" stroke="#34d399" stroke-width="2.4" class="flow" marker-end="url(#a2green)"/><path d="M615 272 L670 272" fill="none" stroke="#38bdf8" stroke-width="2.4" class="flow" marker-end="url(#a2blue)"/><rect x="260" y="360" width="480" height="55" rx="12" fill="#302313" stroke="#fbbf24" stroke-width="1.6"/><text x="500.0" y="385" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Zoning-rule active sur le leaf</text><text x="500.0" y="405" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Permet ou refuse le flux selon la politique résolue</text><path d="M500 310 L500 360" fill="none" stroke="#fbbf24" stroke-width="2.4" class="flow" marker-end="url(#a2amber)"/><text x="500" y="445" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="13">L’APIC programme la politique ; le dataplane des leaf traite les paquets.</text></svg></div>


## 5. BD, VRF et routage inter-segments

### 5.1 Séparer segment L2, domaine L3 et groupe de politique

Un BD définit un domaine de bridging et ses options de forwarding. Une VRF définit un domaine de routage. Un EPG définit une classe de politique. Ces objets sont liés, mais ils répondent à des questions différentes :
- **BD :** comment le segment L2 se comporte-t-il et où se situe la passerelle ?
- **VRF :** dans quel domaine les routes et préfixes sont-ils interprétés ?
- **EPG :** quelles règles de politique s’appliquent aux endpoints ?

Plusieurs BD peuvent être rattachés à une même VRF. Cela permet le routage entre sous-réseaux différents au sein du même domaine L3, sous réserve de la configuration et de la politique. Le contrat peut toujours être nécessaire entre EPG distincts, même lorsque les deux BD partagent une VRF.

### 5.2 Sous-réseaux et passerelles

La passerelle anycast ACI est associée à la conception de BD et est présentée aux endpoints selon la configuration. Vérifie l’adresse de passerelle, le masque, l’absence de doublons et la correspondance entre le sous-réseau du serveur et le BD attendu. Un mauvais masque peut faire croire à un endpoint que la destination est locale, ce qui provoque une résolution ARP plutôt qu’un envoi vers la passerelle.

Les options du BD — routage, apprentissage IP, traitement des unknown unicast, flooding ARP et autres paramètres — modifient le comportement opérationnel. Elles ne doivent pas être changées sans comprendre la topologie et le besoin. Par exemple, un changement de mode de traitement de l’unknown unicast peut être perturbateur ; il faut vérifier les prérequis et les effets sur les endpoints.

### 5.3 VRF enforced et unenforced

Le mode de politique de la VRF influence la manière dont les communications entre EPG sont traitées. En mode enforced, la politique de contrats constitue le modèle normal de contrôle d’accès. En mode unenforced, les communications peuvent être beaucoup plus permissives et les attentes de filtrage changent ; il ne faut pas considérer ce mode comme une simple correction temporaire sans analyse de risque.

Avant de diagnostiquer une absence de contrat, vérifie le mode de la VRF, la relation entre EPG et BD, les routes et la portée de la politique. Une différence entre environnements peut provenir d’une option de VRF ou d’un preferred group, plutôt que d’une différence dans le filtre.


<div class="aci2-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 450" role="img" aria-label="Relation VRF bridge domains et EPG" preserveAspectRatio="xMidYMid meet"><defs><marker id="b" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#38bdf8"/></marker><marker id="g" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#34d399"/></marker><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#fbbf24"/></marker></defs><text x="500" y="28" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21">Schéma 5 — BD, VRF et passerelle par défaut</text><rect x="390" y="55" width="220" height="54" rx="11" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="500.0" y="79" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">VRF-Prod</text><text x="500.0" y="98" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Domaine de routage commun</text><path d="M450 109 L245 150" fill="none" stroke="#38bdf8" stroke-width="2.3" marker-end="url(#b)"/><path d="M550 109 L755 150" fill="none" stroke="#38bdf8" stroke-width="2.3" marker-end="url(#b)"/><rect x="80" y="150" width="330" height="64" rx="11" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="245.0" y="174" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">BD-Web</text><text x="245.0" y="193" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">10.10.10.0/24 · GW 10.10.10.1</text><rect x="590" y="150" width="330" height="64" rx="11" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="755.0" y="174" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">BD-App</text><text x="755.0" y="193" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">10.10.20.0/24 · GW 10.10.20.1</text><path d="M245 214 L245 245" fill="none" stroke="#34d399" stroke-width="2.3" stroke-dasharray="7 6" class="flow" marker-end="url(#g)"/><path d="M755 214 L755 245" fill="none" stroke="#34d399" stroke-width="2.3" stroke-dasharray="7 6" class="flow" marker-end="url(#g)"/><rect x="80" y="245" width="330" height="60" rx="11" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="245.0" y="269" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">EPG-Web</text><text x="245.0" y="288" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Endpoint exemple : 10.10.10.21</text><rect x="590" y="245" width="330" height="60" rx="11" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="755.0" y="269" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">EPG-App</text><text x="755.0" y="288" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Endpoint exemple : 10.10.20.31</text><path d="M410 275 L590 275" fill="none" stroke="#fbbf24" stroke-width="2.3" stroke-dasharray="7 6" class="flow" marker-end="url(#a)"/><text x="500" y="233" text-anchor="middle" fill="#fbbf24" font-family="Arial,sans-serif" font-size="12">Flux inter-BD si routage + policy</text><rect x="250" y="345" width="500" height="52" rx="11" fill="#341722" stroke="#fb7185" stroke-width="1.6"/><text x="500.0" y="369" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="16" font-weight="700">Contrat entre EPG distincts</text><text x="500.0" y="388" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Le routage IP seul ne garantit pas l’autorisation ACI</text><text x="500" y="425" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="13">Plusieurs BD peuvent référencer la même VRF ; chaque EPG référence son BD.</text></svg></div>


## 6. Connectivité externe avec L3Out

### 6.1 Rôle d’un L3Out

Un L3Out relie un tenant ACI à un réseau Layer 3 externe via un ou plusieurs leaf de bordure. Il peut utiliser des routes statiques ou des protocoles de routage pris en charge, selon la conception. Le L3Out comprend des objets de connectivité, des interfaces ou chemins, des paramètres de routage et des objets d’EPG externes qui classifient les préfixes ou réseaux externes.

Il faut distinguer trois questions :
1. le peering et l’échange de routes sont-ils opérationnels ?
2. la route vers la destination et la route retour sont-elles présentes et cohérentes ?
3. la politique ACI autorise-t-elle le flux entre l’EPG interne et l’EPG externe ?

Une adjacence BGP établie ne garantit pas que les préfixes attendus soient reçus ou installés. De même, une route installée ne garantit pas que la politique de sécurité autorise le trafic.

### 6.2 Route aller et route retour

Le trafic aller peut atteindre le réseau externe, mais la réponse peut échouer si le routeur externe ne connaît pas le préfixe interne ou si la route retour pointe ailleurs. Pour tout test, documente source, destination, protocole, port, leaf de bordure, next-hop, route aller, route retour et politique appliquée.

Évite les diagrammes qui montrent une flèche unique vers l’extérieur sans représenter la possibilité d’un retour. Pour la documentation d’un flux bidirectionnel, indique explicitement le sens initial et le chemin de réponse, sans laisser croire que la même route physique ou le même next-hop est toujours utilisé dans les deux sens.

### 6.3 Préfixes externes et classification

Les objets L3Out EPG permettent d’associer des préfixes externes à une classe de politique. Les relations provider/consumer et les contrats doivent correspondre au modèle de sécurité souhaité. Vérifie les sous-réseaux annoncés, les critères de classification, les contrats et les éventuelles politiques de route control. Les détails de configuration dépendent de la release ACI et du protocole de routage retenu.

### 6.4 Checklist de mise en service L3Out

- interfaces et VLAN/encapsulation conformes au design ;
- voisinage de routage opérationnel si un protocole dynamique est utilisé ;
- routes attendues reçues, sélectionnées et installées ;
- route retour connue du réseau externe ;
- préfixes externes associés aux bons objets ;
- contrat correspondant au protocole et au port de l’application ;
- tests de connectivité et de sécurité documentés ;
- plan de retour arrière prêt avant les modifications de route control.


<div class="aci2-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 420" role="img" aria-label="Schéma technique Cisco ACI" preserveAspectRatio="xMidYMid meet"><defs><marker id="a2blue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#38bdf8"/></marker><marker id="a2green" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#34d399"/></marker><marker id="a2amber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#fbbf24"/></marker><marker id="a2red" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#fb7185"/></marker></defs><text x="500" y="28" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21">Schéma 6 — Sortie vers un réseau externe via L3Out</text><rect x="65" y="95" width="220" height="70" rx="12" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="175.0" y="120" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">EPG interne</text><text x="175.0" y="140" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">10.20.1.20 / EPG-App</text><rect x="390" y="95" width="220" height="70" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="500.0" y="120" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Leaf de bordure</text><text x="500.0" y="140" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">L3Out · interface L3</text><rect x="715" y="95" width="220" height="70" rx="12" fill="#302313" stroke="#fbbf24" stroke-width="1.6"/><text x="825.0" y="120" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Routeur externe</text><text x="825.0" y="140" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">BGP / OSPF / routes statiques</text><path d="M285 130 L390 130" fill="none" stroke="#34d399" stroke-width="2.4" class="flow" marker-end="url(#a2green)"/><path d="M610 130 L715 130" fill="none" stroke="#fbbf24" stroke-width="2.4" class="flow" marker-end="url(#a2amber)"/><text x="337" y="115" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Fabric / VXLAN</text><text x="660" y="115" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="12">Peering L3</text><rect x="90" y="255" width="240" height="68" rx="12" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="210.0" y="280" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">L3Out EPG</text><text x="210.0" y="300" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Préfixes externes classifiés</text><rect x="380" y="255" width="240" height="68" rx="12" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="500.0" y="280" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Contrat / policy</text><text x="500.0" y="300" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Flux autorisés vers l’extérieur</text><rect x="670" y="255" width="240" height="68" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="790.0" y="280" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Routes installées</text><text x="790.0" y="300" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Vérifier adjacence et préfixes</text><path d="M285 165 L210 255" fill="none" stroke="#38bdf8" stroke-width="2.4" class="flow" marker-end="url(#a2blue)"/><path d="M330 289 L380 289" fill="none" stroke="#a78bfa" stroke-width="2.4" class="flow" marker-end="url(#a2blue)"/><path d="M620 289 L670 289" fill="none" stroke="#38bdf8" stroke-width="2.4" class="flow" marker-end="url(#a2blue)"/><text x="500" y="390" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="13">Un L3Out fournit la connectivité L3 externe ; les politiques de sécurité restent à vérifier.</text></svg></div>


## 7. Troubleshooting : diagnostiquer sans élargir les droits au hasard

### 7.1 Collecter les faits avant de modifier

Avant toute modification, rassemble : IP source et destination, MAC si disponible, ports source/destination, protocole, EPG source/destination, BD et VRF, leaf d’entrée et de sortie, chemin de connexion, heure du test et résultat attendu. Précise si le problème est nouveau, intermittent ou limité à un type de trafic.

Le test doit être reproductible. Une commande ping seule ne prouve pas le fonctionnement de TCP/443, d’une session SQL ou d’un protocole applicatif. Les ICMP, DNS, TCP et UDP peuvent relever de filtres distincts. Le test doit correspondre au flux réel.

### 7.2 Étape 1 : vérifier les endpoints et l’accès

Confirme que les endpoints sont appris et localisés sur les leaf attendus. Vérifie l’état du port, le VLAN d’encapsulation, le domaine, l’AEP, le binding statique ou la source d’intégration dynamique. Si l’endpoint est absent ou dans un mauvais EPG, le contrat peut être correct tout en restant sans effet sur le flux voulu.

Ne commence pas par supprimer et recréer le contrat. Cela peut introduire un changement de politique inutile et ne corrige pas une erreur d’accès, de VLAN ou de classification.

### 7.3 Étape 2 : vérifier le forwarding L2/L3

Pour un flux dans le même segment, vérifie l’adressage, le masque, le comportement ARP et les informations d’apprentissage. Pour un flux entre sous-réseaux, vérifie la passerelle, le BD, la VRF, les routes et les préfixes. Pour une destination externe, ajoute la vérification de l’adjacence et de la route retour.

Il faut séparer « la destination est-elle atteignable selon le plan de routage ? » de « la politique autorise-t-elle le flux ? ». Un traceroute peut être incomplet à cause du traitement des TTL ou des réponses ICMP ; il ne suffit pas à prouver un défaut du fabric.

### 7.4 Étape 3 : vérifier le contrat et le filtre

Vérifie le rôle provider/consumer, le contrat effectivement lié, le subject, le filtre, le protocole et les ports. Compare le port destination réellement utilisé par l’application au port défini dans le filtre. Vérifie aussi la direction du filtre et l’effet du mode de politique de la VRF.

Un service HTTPS peut utiliser TCP/443, mais le port 443 ne prouve pas que l’application parle TLS correctement. Inversement, un service sur un port personnalisé ne sera pas autorisé par un filtre HTTPS standard s’il ne correspond pas à la règle.

### 7.5 Étape 4 : examiner la règle installée et les journaux

Selon les versions et le contexte d’accès, les outils peuvent inclure la consultation des zoning-rules sur le leaf, les compteurs, les logs de contrat et les vues de dépannage de l’APIC. Les noms et syntaxes de commandes varient : consulte le guide de troubleshooting correspondant à la release installée avant de copier une commande issue d’une autre version.

L’objectif est de relier le flux observé à une règle précise : classe source, classe destination, protocole, ports et action. Vérifie si la règle attendue existe, si une règle plus spécifique s’applique, et si les compteurs changent pendant le test. Si le flux est autorisé par ACI mais échoue toujours, poursuis vers le pare-feu de l’hôte, l’application, le réseau externe ou le retour de trafic.

### 7.6 Erreurs fréquentes et leur correction

| Symptôme | Causes à vérifier en premier | Action prudente |
|---|---|---|
| Endpoint absent | Port down, mauvais VLAN, binding ou domaine | Vérifier accès et apprentissage avant le contrat |
| Ping fonctionne, application échoue | Filtre L4, port réel, service arrêté | Tester le port applicatif exact et consulter les compteurs |
| Même VRF, mais flux inter-EPG bloqué | Contrat manquant ou mauvais rôle | Confirmer provider/consumer et le filtre |
| Flux interne vers externe en échec | L3Out, route retour, classification externe, contrat | Vérifier routes dans les deux sens et policy |
| Fonctionne depuis un leaf, pas depuis un autre | Localisation endpoint, programmation, chemin, différence d’accès | Comparer l’état de l’endpoint et les règles sur les leaf impliqués |
| Après changement de BD, incident généralisé | Options BD, subnet, passerelle, flooding, routage | Revenir au dernier état connu si l’impact est élevé |
| Contrat très large résout le test | Mauvaise hypothèse sur le flux ou filtre trop strict | Identifier le flux exact puis réduire le filtre au minimum requis |


<div class="aci2-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500" role="img" aria-label="Schéma technique Cisco ACI" preserveAspectRatio="xMidYMid meet"><defs><marker id="a2blue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#38bdf8"/></marker><marker id="a2green" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#34d399"/></marker><marker id="a2amber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#fbbf24"/></marker><marker id="a2red" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#fb7185"/></marker></defs><text x="500" y="28" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21">Schéma 7 — Arbre de diagnostic d’un flux bloqué</text><rect x="350" y="55" width="300" height="55" rx="12" fill="#211b3a" stroke="#a78bfa" stroke-width="1.6"/><text x="500.0" y="80" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">Flux source → destination en échec</text><text x="500.0" y="100" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Noter IP, ports, EPG, leaf ingress/egress</text><path d="M500 110 L500 145" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><rect x="330" y="145" width="340" height="55" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="500.0" y="170" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">1. Endpoints appris ?</text><text x="500.0" y="190" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Vérifier MAC/IP, port, VLAN, EPG</text><path d="M500 200 L500 230" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><rect x="330" y="230" width="340" height="55" rx="12" fill="#10263a" stroke="#38bdf8" stroke-width="1.6"/><text x="500.0" y="255" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">2. Routage / BD / VRF corrects ?</text><text x="500.0" y="275" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Passerelle, subnet, route, adjacency</text><path d="M500 285 L500 315" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><rect x="330" y="315" width="340" height="55" rx="12" fill="#302313" stroke="#fbbf24" stroke-width="1.6"/><text x="500.0" y="340" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">3. Contrat et filtre correspondent ?</text><text x="500.0" y="360" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Consumer/provider, TCP/UDP, port, sens</text><path d="M500 370 L500 400" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#a2blue)"/><rect x="330" y="400" width="340" height="55" rx="12" fill="#0b2b27" stroke="#34d399" stroke-width="1.6"/><text x="500.0" y="425" text-anchor="middle" fill="#f8fafc" font-size="17" font-family="Arial,sans-serif" font-weight="700">4. Zoning-rule / compteurs / logs</text><text x="500.0" y="445" text-anchor="middle" fill="#cbd5e1" font-size="12" font-family="Arial,sans-serif">Comparer policy attendue et règle installée</text><path d="M330 172 L210 172 L210 205" fill="none" stroke="#fb7185" stroke-width="2.4" class="flow" marker-end="url(#a2red)"/><text x="200" y="225" text-anchor="middle" fill="#fb7185" font-family="Arial,sans-serif" font-size="11">Non : corriger binding / VLAN / endpoint</text><path d="M670 258 L790 258 L790 290" fill="none" stroke="#fb7185" stroke-width="2.4" class="flow" marker-end="url(#a2red)"/><text x="790" y="310" text-anchor="middle" fill="#fb7185" font-family="Arial,sans-serif" font-size="11">Non : corriger BD / VRF / route</text><text x="500" y="480" text-anchor="middle" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="13">Toujours valider d’abord le forwarding avant d’attribuer le blocage au contrat.</text></svg></div>


## 8. Atelier guidé : sécuriser une application à trois couches

### 8.1 Besoin

On déploie une application avec trois groupes :
- `EPG-Web` : frontaux Web, sous-réseau `10.10.10.0/24` ;
- `EPG-App` : serveurs applicatifs, sous-réseau `10.10.20.0/24` ;
- `EPG-DB` : base de données, sous-réseau `10.10.30.0/24`.

Les trois BD sont associés à `VRF-Prod`. Le besoin est le suivant : Web peut atteindre App en HTTPS ; App peut atteindre DB sur le port SQL choisi par l’organisation ; Web ne doit pas accéder directement à DB ; les autres flux non explicitement demandés restent bloqués.

Les adresses et ports ci-dessus sont des exemples pédagogiques, pas une configuration prête à copier en production. Le port SQL doit être remplacé par le port réellement utilisé dans l’environnement.

### 8.2 Concevoir les objets

1. Créer ou sélectionner le tenant approprié.
2. Créer `VRF-Prod` et les BD nécessaires.
3. Configurer les sous-réseaux et passerelles conformément au plan IP.
4. Créer un Application Profile et les EPG `EPG-Web`, `EPG-App`, `EPG-DB`.
5. Associer chaque EPG au BD prévu et au domaine d’accès approprié.
6. Vérifier que les endpoints sont effectivement classés dans le bon EPG.

La création des objets n’est pas terminée tant que les relations ne sont pas cohérentes et que les endpoints ne sont pas visibles comme prévu. La simple présence d’un EPG dans l’interface ne prouve pas qu’un serveur y appartient.

### 8.3 Définir les contrats

Crée un contrat `C-Web-App-HTTPS` avec un subject et un filtre correspondant au TCP/443 attendu. Fais fournir le contrat par `EPG-App` et consommer par `EPG-Web`. Crée ensuite `C-App-DB-SQL` avec le port SQL réel, fourni par `EPG-DB` et consommé par `EPG-App`.

Ne crée pas de contrat Web-DB si le besoin interdit ce flux. L’absence de contrat dédié est un élément de la politique de refus par défaut dans le mode enforced. Si l’environnement utilise un mécanisme qui modifie cette hypothèse, documente-le et ajuste le plan de test.

### 8.4 Plan de test positif et négatif

| Test | Résultat attendu | Ce que le test valide |
|---|---|---|
| Web → App TCP/443 | Autorisé | Contrat HTTPS et chemin L3 |
| App → DB port SQL | Autorisé | Contrat SQL et chemin vers DB |
| Web → DB port SQL | Refusé | Absence d’autorisation directe |
| Web → App sur un port non prévu | Refusé, sauf autre contrat explicite | Granularité du filtre |
| App → DB vers une destination IP erronée | Échec | Contrôle de la destination et du réseau |
| Test depuis un endpoint mal classé | Résultat conforme à sa vraie politique, pas à son nom de serveur | Importance de la classification |

Les tests négatifs sont aussi importants que les tests positifs. Si tous les flux fonctionnent après ajout d’un contrat `any-any`, l’application peut sembler opérationnelle mais la segmentation demandée n’est plus démontrée.

### 8.5 Documenter l’état final

Consigne les noms des objets, les EPG provider/consumer, les filtres, les ports, la VRF, les BD, les sous-réseaux, les tests exécutés et leurs résultats. Note aussi les flux intentionnellement refusés. Cette documentation facilite les changements futurs et permet d’identifier si un nouveau flux correspond à une évolution légitime ou à un défaut de configuration.

## 9. Automatisation et gestion du changement

### 9.1 Pourquoi automatiser

Les API de l’APIC et les outils d’automatisation peuvent aider à créer, lire, comparer et valider des objets. L’automatisation ne rend pas une politique correcte par elle-même : elle peut reproduire très vite une erreur de conception. Les workflows doivent donc contenir des contrôles de préconditions, une validation du modèle et des tests post-déploiement.

### 9.2 Idempotence et dérive de configuration

Un workflow idempotent converge vers l’état souhaité sans dupliquer les objets à chaque exécution. Pour y parvenir, il doit lire l’état actuel, comparer les propriétés nécessaires, ne modifier que ce qui diffère et vérifier le résultat. La stratégie de nommage doit être stable et documentée.

La dérive apparaît lorsqu’une modification manuelle, une ancienne automatisation ou une opération de maintenance fait diverger l’état réel de l’état déclaré. Un inventaire périodique des relations critiques, contrats et bindings permet de détecter cette divergence. Ne stocke pas de secrets dans des scripts ou dépôts non protégés ; utilise les mécanismes de gestion d’identifiants approuvés dans l’environnement.

### 9.3 Pipeline de changement recommandé

1. **Prévalidation :** vérifier les objets ciblés, leurs dépendances et les droits de l’opérateur.
2. **Diff :** afficher ce qui sera créé, modifié ou supprimé.
3. **Validation sécurité :** comparer les flux autorisés avant/après et repérer les élargissements de portée.
4. **Déploiement contrôlé :** appliquer dans une fenêtre autorisée et avec un plan de retour arrière.
5. **Postvalidation :** vérifier résolution, endpoints, règles et tests de connectivité.
6. **Traçabilité :** conserver la version, les résultats, les erreurs et l’approbation.

Une suppression d’objet peut casser des relations qui ne sont pas évidentes à partir de son nom. Avant de supprimer un contrat, un BD ou un EPG, recherche les consommateurs et fournisseurs, les relations et les services qui en dépendent.

## 10. Conception, exploitation et sécurité

### 10.1 Convention de nommage

Utilise des noms qui expriment l’intention, la portée et l’environnement, sans être excessivement longs. Par exemple : `VRF-Prod`, `BD-Web-Prod`, `EPG-Web-Prod`, `C-Web-App-HTTPS`. Le nom doit rester cohérent avec les conventions de l’organisation. Évite les noms comme `test2`, `new-contract` ou `allow-all-final` qui ne décrivent pas le but réel.

### 10.2 Moindre privilège

Un contrat doit autoriser le minimum nécessaire en matière de source, destination, protocole et port. Les filtres trop larges facilitent les déploiements mais compliquent la gouvernance et peuvent ouvrir des chemins non voulus. Chaque exception devrait avoir un propriétaire, une justification, une date de revue et des tests associés.

### 10.3 Changements de politique en production

Avant un changement, capture les relations existantes et les résultats des tests. Évalue le blast radius : combien d’EPG utilisent le contrat, quels services partagent le BD, quels tenants ou VRF sont concernés et quelles routes externes peuvent être affectées. Prépare une procédure de retour arrière qui restaure le modèle précédent sans dépendre d’une reconstruction improvisée.

### 10.4 Supervision

Surveille l’état de la fabric, les liens, les endpoints, les routes, les événements de politique et les changements de configuration. Une alerte utile doit contenir le contexte nécessaire à l’investigation : heure, équipement ou objet, portée de l’impact, service concerné et première piste. Les compteurs de trafic et les journaux doivent être interprétés avec le volume normal et la fenêtre de test.

### 10.5 Limites de la segmentation réseau

ACI applique une politique réseau ; ce n’est pas un remplacement complet de la sécurité applicative, de la gestion des identités, du durcissement des hôtes ou de la protection des données. Une politique réseau peut limiter les chemins, mais elle ne corrige pas une vulnérabilité applicative ni une authentification faible. Les contrôles doivent se compléter.

## 11. Évaluation intermédiaire

### Questions

1. Pourquoi une route entre deux sous-réseaux ne prouve-t-elle pas que le flux inter-EPG est autorisé ?
2. Quelle différence entre BD, VRF et EPG ?
3. Pourquoi faut-il confirmer le classement de l’endpoint avant de modifier un contrat ?
4. Quel est le rôle des zoning-rules dans l’application des politiques ?
5. Quelles vérifications faut-il faire pour un flux vers un réseau externe via L3Out ?
6. Pourquoi un contrat `any-any` est-il une mauvaise première étape de dépannage ?
7. Quels éléments doivent être inclus dans un test de validation après modification d’un contrat ?
8. Pourquoi faut-il documenter les flux qui doivent être refusés ?

### Corrigé

1. La route répond à la reachability L3 ; la politique ACI peut toujours bloquer la communication entre EPG distincts.
2. Le BD décrit le segment L2 et ses options de forwarding, la VRF le domaine de routage L3, et l’EPG la classe de politique des endpoints.
3. La politique s’applique à la classe réelle de l’endpoint. Si le serveur est classé dans un autre EPG, le contrat attendu peut ne pas correspondre.
4. Les zoning-rules sont les règles installées sur les leaf qui appliquent les décisions de politique aux flux classifiés.
5. Vérifier peering, routes reçues/installées, route retour, classification des préfixes externes, contrat et tests applicatifs.
6. Il élargit l’accès, masque la cause racine et peut créer une exposition durable.
7. Source/destination, protocole/port, EPG, test positif, test négatif, compteurs ou logs et résultats attendus.
8. Les refus sont une exigence de sécurité à part entière ; ils prouvent que la segmentation fonctionne comme prévu.

## 12. Références et documentation

Les menus, noms d’objets, options et commandes peuvent varier selon la version d’ACI et les modèles de commutateurs. Pour une opération réelle, vérifie toujours la documentation correspondant à la release installée.

- [Cisco ACI Fundamentals 6.2(x) — Policy Model](https://www.cisco.com/c/en/us/td/docs/dcn/aci/apic/6x/aci-fundamentals/cisco-aci-fundamentals-62x/policy-model-62x.html) — tenants, VRF, BD, EPG, contrats, filtres et relations d’objets.
- [Cisco ACI Fundamentals 6.2(x) — Forwarding](https://www.cisco.com/c/en/us/td/docs/dcn/aci/apic/6x/aci-fundamentals/cisco-aci-fundamentals-62x/fundamentals-62x.html) — principes de forwarding et architecture fabric.
- [Cisco ACI Contract Guide](https://www.cisco.com/c/en/us/products/collateral/networking/cloud-networking/application-centric-infrastructure/contract-guide.html) — comportement et dépannage des contrats.
- [Cisco ACI Forwarding / VXLAN](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/2-x/L3_config/b_Cisco_APIC_Layer_3_Configuration_Guide/b_Cisco_APIC_Layer_3_Configuration_Guide_chapter_01.pdf) — principes d’encapsulation et forwarding.
- [Cisco Troubleshoot ACI Security Policies — Contracts](https://team-development.cisco.com/c/en/us/support/docs/cloud-systems-management/application-policy-infrastructure-controller-apic/218030-troubleshoot-aci-security-policies-con.html) — méthode de diagnostic des politiques de contrat.


## À retenir

- Une fabric ACI combine transport leaf-spine, overlay et politique centralement modélisée.
- Les relations d’objets ne sont pas toutes hiérarchiques ; les schémas doivent distinguer containment, association, contrat et flux de paquets.
- Un BD, une VRF et un EPG ont des rôles distincts et complémentaires.
- Un contrat doit être pensé à partir du flux applicatif réel, de son protocole, de son port et du rôle provider/consumer.
- Les zoning-rules appliquent les politiques résolues sur les leaf ; il faut les relier au trafic observé.
- Un incident se dépanne dans l’ordre : endpoint et accès, forwarding L2/L3, contrat/filtre, règle installée, puis hôte et application.
- Les flux refusés et les tests négatifs font partie de la validation de sécurité.
- Les changements de politique doivent être traçables, testés et réversibles.
