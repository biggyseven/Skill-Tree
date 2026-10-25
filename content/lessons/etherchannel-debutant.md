<style>
@keyframes ethFlowDash { to { stroke-dashoffset: -26; } }
.eth-flow { stroke-dasharray: 7 6; animation: ethFlowDash 1.8s linear infinite; }
@media (prefers-reduced-motion: reduce) { .eth-flow { animation: none !important; } }

.lesson-diagram { width: 100%; margin: 1rem 0 1.35rem; }
.lesson-diagram svg { display: block; width: 100%; height: auto; }
</style>

# Agrégation de liens (EtherChannel/LACP) — Niveau Débutant

**Niveau :** Débutant · **Domaine :** Réseaux Ethernet / couche 2 · **Prérequis :** notions de switch, port Ethernet, adresse MAC et VLAN.

L’objectif de ce cours est de comprendre comment plusieurs liens physiques Ethernet peuvent fonctionner ensemble comme un seul lien logique, comment LACP négocie cette agrégation et comment vérifier qu’elle fonctionne correctement. Les exemples de configuration utilisent une syntaxe Cisco IOS/IOS XE courante ; les commandes et limites exactes varient selon le constructeur, le modèle et la version.

## 1. Le problème : un seul câble ne suffit pas toujours

Imagine deux commutateurs qui doivent échanger les données de plusieurs dizaines d’ordinateurs. Un lien Ethernet unique peut devenir un point de panne : si le câble ou un port tombe en panne, la communication entre les deux commutateurs peut être interrompue. Le lien peut aussi devenir un goulot d’étranglement si le trafic cumulé augmente.

Une solution consiste à installer deux, quatre ou plusieurs liens physiques entre les mêmes équipements et à les regrouper dans une **agrégation de liens** (*link aggregation*). Les termes suivants sont souvent rencontrés :

- **LAG** (*Link Aggregation Group*) : terme générique désignant le groupe de liens agrégés.
- **EtherChannel** : nom utilisé par Cisco pour une agrégation de liens.
- **Port-channel** : interface logique représentant le groupe dans de nombreuses interfaces en ligne de commande Cisco.
- **LACP** (*Link Aggregation Control Protocol*) : protocole normalisé qui permet aux deux extrémités de négocier et contrôler l’agrégation.

Ces termes ne sont pas toujours interchangeables strictement : EtherChannel peut être configuré avec LACP, avec le protocole propriétaire Cisco PAgP, ou statiquement selon les équipements. Dans ce cours, nous utiliserons principalement **EtherChannel avec LACP**.

### Analogie

Un port-channel est comparable à une route avec plusieurs voies. Les voies sont les câbles physiques ; la route globale est l’interface logique. Si une voie est fermée, la circulation peut continuer sur les autres, mais la capacité totale diminue. Les voitures ne se répartissent pas nécessairement de manière parfaitement égale entre les voies : l’équipement utilise une règle de répartition.

## 2. Objectifs et limites d’une agrégation

### 2.1 Les objectifs principaux

**Augmenter la capacité agrégée.** Deux liens de 1 Gbit/s peuvent offrir jusqu’à environ 2 Gbit/s de capacité agrégée théorique pour plusieurs flux, sous réserve des limitations du matériel et des protocoles. Avec quatre liens de 1 Gbit/s, la capacité théorique du groupe peut approcher 4 Gbit/s dans les conditions favorables.

**Améliorer la résilience.** Si un membre tombe en panne, les membres restants peuvent continuer à transporter le trafic. Cette continuité suppose que le port-channel reste opérationnel, que le trafic restant puisse absorber la charge et que la panne soit détectée correctement.

**Simplifier la topologie logique.** Les protocoles comme Spanning Tree voient généralement le groupe comme un seul port logique, plutôt que comme plusieurs liens indépendants entre les mêmes commutateurs.

### 2.2 Ce que l’agrégation ne fait pas

- Elle ne transforme pas un port 1 Gbit/s en un port 10 Gbit/s.
- Elle ne garantit pas qu’une seule connexion atteindra la somme des débits de tous les liens.
- Elle ne remplace pas la redondance électrique, la redondance des équipements ou la diversité des chemins physiques.
- Elle ne permet pas systématiquement de connecter les membres à plusieurs commutateurs indépendants. Cela requiert une technologie de type stack ou multichassis, prise en charge et correctement configurée aux deux extrémités.
- Elle ne corrige pas à elle seule un problème de VLAN, de routage, de congestion ou de configuration incohérente.

## 3. Comprendre l’interface logique

Chaque membre est un port Ethernet réel, avec son câble, son port de commutateur et ses compteurs. Le port-channel est une interface logique créée au-dessus de ces membres. La configuration commune — par exemple le mode access/trunk et les VLAN — se gère souvent au niveau de l’interface logique, selon la plateforme. Les ports membres doivent présenter des caractéristiques compatibles.


<div class="lesson-diagram"><svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Deux liens physiques regroupés en un port-channel logique" viewBox="0 0 960 330" width="100%" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="328" rx="18" fill="#0b1220" stroke="#263449"/><text x="480" y="32" fill="#f1f5f9" font-size="21" font-weight="700" text-anchor="middle">Deux câbles physiques, un seul lien logique</text><rect x="45" y="93" width="205" height="150" rx="12" fill="#12263a" stroke="#38bdf8" stroke-width="2"/><text x="147" y="126" fill="#e2e8f0" text-anchor="middle" font-size="18" font-weight="700">Switch A</text><rect x="710" y="93" width="205" height="150" rx="12" fill="#12263a" stroke="#38bdf8" stroke-width="2"/><text x="812" y="126" fill="#e2e8f0" text-anchor="middle" font-size="18" font-weight="700">Switch B</text><rect x="72" y="150" width="150" height="28" rx="6" fill="#164e63" stroke="#22d3ee"/><text x="147" y="169" fill="#ecfeff" text-anchor="middle" font-size="13">Port-channel 1</text><rect x="738" y="150" width="150" height="28" rx="6" fill="#164e63" stroke="#22d3ee"/><text x="813" y="169" fill="#ecfeff" text-anchor="middle" font-size="13">Port-channel 1</text><path d="M250 145 C360 145 600 145 710 145" fill="none" stroke="#22d3ee" stroke-width="4"/><path d="M250 185 C360 185 600 185 710 185" fill="none" stroke="#a3e635" stroke-width="4"/><path d="M460 145 l16 0" stroke="#22d3ee" stroke-width="4" marker-end="url(#e1cyan)"/><path d="M490 185 l16 0" stroke="#a3e635" stroke-width="4" marker-end="url(#e1lime)"/><text x="480" y="120" fill="#7dd3fc" text-anchor="middle" font-size="14">Membre 1</text><text x="480" y="211" fill="#bef264" text-anchor="middle" font-size="14">Membre 2</text><text x="480" y="275" fill="#cbd5e1" text-anchor="middle" font-size="15">LACP vérifie la compatibilité des ports et construit l’agrégat</text><defs><marker id="e1cyan" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#22d3ee"/></marker><marker id="e1lime" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#a3e635"/></marker></defs></svg></div>


**À retenir sur le schéma :** les deux câbles restent deux liens physiques distincts, mais ils sont regroupés pour former un seul chemin logique. La flèche illustre le sens d’un flux représenté ; le trafic réel peut circuler dans les deux directions.

### 3.1 L’agrégat n’est pas un câble virtuel sans règles

Le port-channel possède un état global. Un membre peut être :

- **actif et agrégé** : il participe à l’agrégat et peut transporter une partie du trafic ;
- **hors service** : interface en panne, administrativement coupée ou non opérationnelle ;
- **non agrégé / individuel** : lien physique actif, mais qui n’a pas rejoint le groupe correctement ;
- **suspendu** : équipement qui neutralise le membre pour éviter une configuration risquée ou incompatible.

Les noms précis des états varient selon les systèmes. Il faut examiner l’état du port-channel et celui de chaque membre, pas seulement regarder si les voyants sont verts.

## 4. Les bases de LACP

LACP échange des messages de contrôle appelés **LACPDU** entre les équipements pour permettre la formation et la surveillance du groupe. Il annonce notamment l’identité du système, l’identité du port et des informations d’état. Les équipements déterminent alors quels ports compatibles peuvent être agrégés ensemble.

LACP est défini par les normes IEEE de l’agrégation de liens, historiquement IEEE 802.3ad et désormais IEEE 802.1AX. Un constructeur peut ajouter des paramètres propres à sa plateforme, mais le principe général est commun.

### 4.1 Les modes active et passive

- **Active** : le port initie la négociation en envoyant des LACPDU.
- **Passive** : le port n’initie pas la négociation ; il répond lorsqu’il reçoit les messages LACP d’un partenaire.

Les combinaisons courantes sont :

| Côté A | Côté B | Résultat attendu |
|---|---|---|
| Active | Active | Négociation possible |
| Active | Passive | Négociation possible |
| Passive | Active | Négociation possible |
| Passive | Passive | Pas d’initiation de négociation ; le groupe ne se forme généralement pas |

Pour un déploiement simple, **active des deux côtés** est souvent facile à comprendre et à diagnostiquer. Le choix dépend néanmoins des standards et des règles de configuration de l’organisation.


<div class="lesson-diagram"><svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Négociation LACP entre deux équipements" viewBox="0 0 960 330" width="100%" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="328" rx="18" fill="#0b1220" stroke="#263449"/><text x="480" y="32" fill="#f1f5f9" font-size="21" font-weight="700" text-anchor="middle">LACP : échange de contrôle des deux côtés</text><rect x="70" y="92" width="250" height="138" rx="12" fill="#12263a" stroke="#38bdf8" stroke-width="2"/><text x="195" y="125" fill="#e2e8f0" font-size="18" font-weight="700" text-anchor="middle">Switch A</text><text x="195" y="153" fill="#7dd3fc" font-size="15" text-anchor="middle">Mode active</text><text x="195" y="180" fill="#cbd5e1" font-size="13" text-anchor="middle">Envoie des LACPDU</text><rect x="640" y="92" width="250" height="138" rx="12" fill="#12263a" stroke="#a3e635" stroke-width="2"/><text x="765" y="125" fill="#e2e8f0" font-size="18" font-weight="700" text-anchor="middle">Switch B</text><text x="765" y="153" fill="#bef264" font-size="15" text-anchor="middle">Mode passive</text><text x="765" y="180" fill="#cbd5e1" font-size="13" text-anchor="middle">Répond aux LACPDU</text><path class="eth-flow" d="M320 130 C420 105 540 105 640 130" fill="none" stroke="#22d3ee" stroke-width="4" marker-end="url(#e2a)"/><path class="eth-flow" d="M640 190 C540 215 420 215 320 190" fill="none" stroke="#a3e635" stroke-width="4" marker-end="url(#e2b)"/><text x="480" y="91" fill="#7dd3fc" font-size="14" text-anchor="middle">LACPDU</text><text x="480" y="236" fill="#bef264" font-size="14" text-anchor="middle">LACPDU de réponse / état</text><rect x="280" y="265" width="400" height="36" rx="8" fill="#132d28" stroke="#34d399"/><text x="480" y="288" fill="#d1fae5" font-size="14" text-anchor="middle">Active + Passive = compatible</text><defs><marker id="e2a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#22d3ee"/></marker><marker id="e2b" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#a3e635"/></marker></defs></svg></div>


### 4.2 Pourquoi LACP est utile

Sans protocole de négociation, une configuration statique peut croire à tort que les ports sont bien connectés au bon équipement. LACP fournit une vérification dynamique du partenaire et de la compatibilité. Il réduit le risque de certains mauvais assemblages, mais ne remplace pas la vérification du câblage, la documentation et les contrôles de changement.

LACP ne prouve pas que toute la topologie physique est idéale : par exemple, relier des membres à deux commutateurs qui ne forment pas un système logique cohérent peut toujours être une erreur. LACP doit être configuré dans une architecture que les deux équipements prennent en charge.

### 4.3 LACP et agrégation statique

Une agrégation peut parfois être créée en mode statique, sans échanges LACP. Dans ce cas, la configuration manuelle doit être cohérente des deux côtés. Un mauvais câblage ou un groupe configuré différemment peut provoquer des perturbations difficiles à diagnostiquer.

Ne mélange pas les modes dans un même groupe : par exemple, ne configure pas un côté en LACP et l’autre en mode statique en supposant qu’ils vont négocier ensemble. Les deux extrémités doivent employer un mode compatible.

## 5. Répartition de charge : comment les flux utilisent-ils les membres ?

Un point important pour un débutant : l’agrégation **ne coupe pas chaque paquet en morceaux pour les envoyer simultanément sur tous les liens**. Les commutateurs choisissent généralement un membre à partir d’un algorithme de hachage (*hash*) utilisant certains champs des paquets, par exemple une combinaison d’adresses MAC, d’adresses IP ou de ports TCP/UDP, selon le matériel et la configuration.

Les paquets d’un même flux sont généralement conservés sur un même membre, afin de limiter le réordonnancement des paquets. D’autres flux peuvent être répartis sur d’autres membres. Les champs choisis pour le hachage et les options de configuration varient selon la plateforme.


<div class="lesson-diagram"><svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Répartition de plusieurs flux sur les membres d’un agrégat" viewBox="0 0 960 330" width="100%" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="328" rx="18" fill="#0b1220" stroke="#263449"/><text x="480" y="32" fill="#f1f5f9" font-size="21" font-weight="700" text-anchor="middle">Répartition par flux : le hachage choisit un membre</text><rect x="55" y="78" width="205" height="205" rx="12" fill="#12263a" stroke="#38bdf8" stroke-width="2"/><text x="158" y="108" fill="#e2e8f0" font-size="17" font-weight="700" text-anchor="middle">Flux entrants</text><rect x="80" y="127" width="155" height="30" rx="6" fill="#164e63" stroke="#22d3ee"/><text x="158" y="147" fill="#ecfeff" font-size="13" text-anchor="middle">Flux A</text><rect x="80" y="174" width="155" height="30" rx="6" fill="#3f2d12" stroke="#fbbf24"/><text x="158" y="194" fill="#fef3c7" font-size="13" text-anchor="middle">Flux B</text><rect x="80" y="221" width="155" height="30" rx="6" fill="#30224e" stroke="#c4b5fd"/><text x="158" y="241" fill="#ede9fe" font-size="13" text-anchor="middle">Flux C</text><rect x="700" y="96" width="205" height="66" rx="10" fill="#102e35" stroke="#22d3ee" stroke-width="2"/><text x="803" y="123" fill="#cffafe" font-size="15" font-weight="700" text-anchor="middle">Membre 1</text><text x="803" y="144" fill="#a5f3fc" font-size="12" text-anchor="middle">Lien physique A</text><rect x="700" y="205" width="205" height="66" rx="10" fill="#2b2818" stroke="#fbbf24" stroke-width="2"/><text x="803" y="232" fill="#fef3c7" font-size="15" font-weight="700" text-anchor="middle">Membre 2</text><text x="803" y="253" fill="#fde68a" font-size="12" text-anchor="middle">Lien physique B</text><path class="eth-flow" d="M260 142 C400 142 550 125 700 125" fill="none" stroke="#22d3ee" stroke-width="3" marker-end="url(#e3a)"/><path class="eth-flow" d="M260 189 C430 189 520 238 700 238" fill="none" stroke="#fbbf24" stroke-width="3" marker-end="url(#e3b)"/><path class="eth-flow" d="M260 236 C405 236 520 142 700 142" fill="none" stroke="#c4b5fd" stroke-width="3" marker-end="url(#e3c)"/><text x="480" y="304" fill="#cbd5e1" font-size="14" text-anchor="middle">Un même flux reste généralement sur le même membre pour préserver l’ordre</text><defs><marker id="e3a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#22d3ee"/></marker><marker id="e3b" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#fbbf24"/></marker><marker id="e3c" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#c4b5fd"/></marker></defs></svg></div>


### 5.1 Exemple simple

Supposons un port-channel composé de deux liens de 1 Gbit/s :

- Le flux A entre un poste et un serveur est envoyé sur le membre 1.
- Le flux B, entre deux autres adresses, est envoyé sur le membre 2.
- Le flux C peut se retrouver sur le membre 1 à cause du résultat du hachage.

Les membres ne sont donc pas forcément chargés à 50/50. Si un très gros flux est seul, il peut saturer un membre alors que l’autre est peu utilisé. On appelle parfois cela une **polarisation** ou une répartition déséquilibrée. Augmenter le nombre de liens n’élimine pas automatiquement ce phénomène.

### 5.2 Le débit d’un seul flux

Si une copie de fichier se limite à une seule connexion TCP, elle utilisera généralement un seul membre du groupe. Son débit sera alors limité par la capacité de ce membre, et non par la somme de tous les liens. Une application qui crée plusieurs flux peut mieux exploiter la capacité totale, mais le résultat dépend de l’algorithme de répartition, des endpoints et du reste du réseau.

### 5.3 Pourquoi on ne balance pas chaque paquet au hasard

Si les paquets d’une même conversation prennent des chemins de latence différente et arrivent dans le désordre, certains protocoles et systèmes peuvent réagir moins efficacement. C’est pourquoi beaucoup d’équipements préfèrent une répartition par flux qui maintient l’affinité des paquets.

## 6. Redondance et panne d’un membre

L’un des intérêts de l’agrégation est qu’une défaillance d’un câble ou d’un port membre ne doit pas nécessairement couper le lien logique. Les membres restants peuvent continuer à transporter les flux tant que le groupe demeure opérationnel.


<div class="lesson-diagram"><svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Basculement après la panne d’un membre" viewBox="0 0 960 330" width="100%" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="328" rx="18" fill="#0b1220" stroke="#263449"/><text x="480" y="32" fill="#f1f5f9" font-size="21" font-weight="700" text-anchor="middle">Panne d’un membre : le trafic se reporte sur le lien restant</text><rect x="55" y="105" width="210" height="130" rx="12" fill="#12263a" stroke="#38bdf8" stroke-width="2"/><text x="160" y="141" fill="#e2e8f0" font-size="18" font-weight="700" text-anchor="middle">Switch A</text><rect x="695" y="105" width="210" height="130" rx="12" fill="#12263a" stroke="#38bdf8" stroke-width="2"/><text x="800" y="141" fill="#e2e8f0" font-size="18" font-weight="700" text-anchor="middle">Switch B</text><path d="M265 156 C390 156 570 156 695 156" fill="none" stroke="#ef4444" stroke-width="4" stroke-dasharray="8 7"/><path d="M458 145 l22 22 M480 145 l-22 22" stroke="#f87171" stroke-width="5" stroke-linecap="round"/><text x="480" y="134" fill="#fca5a5" font-size="14" font-weight="700" text-anchor="middle">Membre 1 : DOWN</text><path class="eth-flow" d="M265 203 C390 203 570 203 695 203" fill="none" stroke="#34d399" stroke-width="5" marker-end="url(#e4a)"/><text x="480" y="230" fill="#a7f3d0" font-size="14" font-weight="700" text-anchor="middle">Membre 2 : actif</text><rect x="270" y="265" width="420" height="36" rx="8" fill="#2d1b20" stroke="#fb7185"/><text x="480" y="288" fill="#ffe4e6" font-size="14" text-anchor="middle">Capacité réduite : vérifier l’impact sur le débit restant</text><defs><marker id="e4a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#34d399"/></marker></defs></svg></div>


### 6.1 Capacité après panne

Prenons deux liens de 1 Gbit/s :

- fonctionnement normal : capacité agrégée théorique maximale de 2 Gbit/s ;
- un membre en panne : environ 1 Gbit/s de capacité de lien restante ;
- les flux peuvent être remappés sur les membres disponibles, mais un bref impact peut survenir pendant la détection ou la reprogrammation.

Avec quatre membres de 10 Gbit/s, une panne laisse trois liens, soit 30 Gbit/s de capacité de lien théorique restante, avant de considérer les en-têtes, le matériel, les flux et les autres contraintes. La capacité effective ne doit pas être confondue avec un débit applicatif garanti.

### 6.2 La panne doit être réellement indépendante

Deux câbles peuvent partager un même chemin physique, une même baie, une même carte ou une même alimentation. L’agrégation protège contre certaines pannes de membre, mais pas contre tous les risques communs. Dans un réseau critique, étudie aussi la diversité des conduits, les alimentations, les modules et la redondance des équipements.

### 6.3 Minimum de membres

Certaines plateformes permettent de définir un nombre minimal de liens agrégés pour que le port-channel soit opérationnel (`min-links`, par exemple). Si la configuration exige au moins deux membres, une panne qui laisse un seul lien peut faire tomber l’interface logique au lieu de continuer avec une capacité réduite. C’est parfois voulu pour éviter de fonctionner sous un seuil de capacité, mais il faut comprendre la conséquence avant d’activer ce réglage.

## 7. Où peut-on déployer une agrégation ?

### 7.1 Entre deux commutateurs

C’est le scénario classique : deux commutateurs disposent de plusieurs liens Ethernet parallèles et forment un port-channel. Les ports doivent pointer vers le même partenaire logique. Si les commutateurs sont indépendants, on ne peut pas simplement répartir au hasard un membre sur chacun : il faut une technologie de stack, MLAG, vPC, VSX, IRF ou équivalent prise en charge pour présenter le bon comportement logique.

### 7.2 Entre un serveur et un commutateur

Un serveur peut utiliser plusieurs interfaces réseau pour former un bond ou une team, avec le protocole de l’OS ou de l’hyperviseur. Le mode côté serveur doit être compatible avec le mode côté commutateur. Pour un agrégat LACP, le système serveur doit prendre en charge et activer LACP. D’autres modes de bonding existent, mais ils ne sont pas équivalents à LACP.


<div class="lesson-diagram"><svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Agrégation de liens entre un serveur et un commutateur" viewBox="0 0 960 330" width="100%" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="328" rx="18" fill="#0b1220" stroke="#263449"/><text x="480" y="32" fill="#f1f5f9" font-size="21" font-weight="700" text-anchor="middle">Agrégation serveur–switch : les deux côtés doivent être compatibles</text><rect x="60" y="100" width="260" height="150" rx="12" fill="#12263a" stroke="#a78bfa" stroke-width="2"/><text x="190" y="132" fill="#ede9fe" font-size="18" font-weight="700" text-anchor="middle">Serveur</text><rect x="100" y="153" width="180" height="28" rx="6" fill="#30224e" stroke="#c4b5fd"/><text x="190" y="172" fill="#ede9fe" font-size="13" text-anchor="middle">Bond / Team / LAG</text><rect x="640" y="100" width="260" height="150" rx="12" fill="#12263a" stroke="#38bdf8" stroke-width="2"/><text x="770" y="132" fill="#e2e8f0" font-size="18" font-weight="700" text-anchor="middle">Switch</text><rect x="680" y="153" width="180" height="28" rx="6" fill="#164e63" stroke="#22d3ee"/><text x="770" y="172" fill="#ecfeff" font-size="13" text-anchor="middle">Port-channel</text><path class="eth-flow" d="M320 160 C420 130 540 130 640 160" fill="none" stroke="#22d3ee" stroke-width="4" marker-end="url(#e5a)"/><path class="eth-flow" d="M320 198 C420 228 540 228 640 198" fill="none" stroke="#a3e635" stroke-width="4" marker-end="url(#e5b)"/><text x="480" y="113" fill="#7dd3fc" font-size="14" text-anchor="middle">NIC 1 ↔ port 1</text><text x="480" y="250" fill="#bef264" font-size="14" text-anchor="middle">NIC 2 ↔ port 2</text><text x="480" y="290" fill="#cbd5e1" font-size="14" text-anchor="middle">LACP doit être configuré des deux côtés si le mode LACP est choisi</text><defs><marker id="e5a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#22d3ee"/></marker><marker id="e5b" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#a3e635"/></marker></defs></svg></div>


### 7.3 Entre un commutateur et un routeur ou pare-feu

C’est possible lorsqu’ils prennent en charge la fonction et les modes requis. Il faut déterminer si le port-channel fonctionne en couche 2 (access ou trunk) ou en couche 3 (interface routée), et vérifier les particularités du système distant.

### 7.4 Un piège fréquent : deux switches qui ne se connaissent pas comme un seul système

Imaginons que Switch A dispose d’un lien vers Switch B et d’un autre vers Switch C. On ne doit pas supposer que ces deux liens peuvent former un seul LAG vers B et C simplement parce que tous les équipements parlent LACP. Les deux ports distants doivent appartenir à un même système logique capable de coordonner l’agrégation multichâssis, sinon le résultat ne sera pas celui attendu.

## 8. Contraintes de compatibilité à vérifier

Pour qu’un groupe soit stable, ses ports membres doivent avoir des paramètres compatibles. Les exigences exactes varient entre plateformes ; la liste suivante constitue une checklist de base.


<div class="lesson-diagram"><svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Paramètres à contrôler pour des membres compatibles" viewBox="0 0 960 330" width="100%" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="328" rx="18" fill="#0b1220" stroke="#263449"/><text x="480" y="32" fill="#f1f5f9" font-size="21" font-weight="700" text-anchor="middle">Avant d’agréger : comparer les deux extrémités</text><rect x="58" y="72" width="405" height="208" rx="12" fill="#102132" stroke="#38bdf8" stroke-width="2"/><rect x="497" y="72" width="405" height="208" rx="12" fill="#17271f" stroke="#34d399" stroke-width="2"/><text x="260" y="103" fill="#bae6fd" font-size="18" font-weight="700" text-anchor="middle">Paramètres à aligner</text><text x="700" y="103" fill="#bbf7d0" font-size="18" font-weight="700" text-anchor="middle">Vérification des deux côtés</text><g fill="#e2e8f0" font-size="15"><text x="86" y="140">• Même vitesse / duplex compatible</text><text x="86" y="172">• Même mode access ou trunk</text><text x="86" y="204">• VLAN natif et VLAN autorisés cohérents</text><text x="86" y="236">• Même protocole d’agrégation</text><text x="86" y="258">• Adresses / câblage vers le bon pair</text></g><g font-size="14"><rect x="530" y="122" width="340" height="34" rx="6" fill="#12392c" stroke="#34d399"/><text x="700" y="144" fill="#d1fae5" text-anchor="middle">Port 1 ↔ Port 1 : cohérent ?</text><rect x="530" y="166" width="340" height="34" rx="6" fill="#12392c" stroke="#34d399"/><text x="700" y="188" fill="#d1fae5" text-anchor="middle">Port 2 ↔ Port 2 : cohérent ?</text><rect x="530" y="210" width="340" height="34" rx="6" fill="#3b2715" stroke="#f59e0b"/><text x="700" y="232" fill="#fef3c7" text-anchor="middle">Différence détectée → corriger avant activation</text></g><text x="480" y="306" fill="#94a3b8" font-size="13" text-anchor="middle">Les détails exacts dépendent du constructeur et de la plateforme</text></svg></div>


### 8.1 Checklist technique

- **Vitesse et duplex :** les membres doivent utiliser des paramètres compatibles, généralement identiques dans les déploiements classiques.
- **Mode de port :** ne mélange pas des interfaces access et trunk dans le même groupe.
- **VLAN :** sur un trunk, la liste des VLAN autorisés doit être cohérente ; vérifie également le VLAN natif lorsqu’il est utilisé.
- **Protocole :** LACP des deux côtés, ou agrégation statique compatible des deux côtés ; ne mélange pas arbitrairement LACP et PAgP ou le mode statique.
- **Partenaire :** les membres doivent arriver au bon système distant ou à une paire multichâssis officiellement prise en charge.
- **Configuration de couche 3 :** dans un port-channel routé, l’adresse IP doit habituellement être appliquée à l’interface logique, et non individuellement aux ports membres.
- **Fonctions incompatibles :** certaines fonctions de port, sécurité ou supervision peuvent avoir des restrictions sur les interfaces membres. Consulte la documentation du modèle.
- **Nombre de membres :** vérifie la limite de la plateforme, ainsi que les membres actifs et éventuellement les membres en veille.

### 8.2 Pourquoi une configuration incohérente est dangereuse

Un agrégat mal configuré peut refuser des membres, les suspendre, avoir un port-channel down ou provoquer une connectivité partielle. Il ne faut pas contourner une protection automatique sans comprendre la cause : l’équipement peut empêcher une boucle de couche 2 ou un comportement incohérent.

## 9. Configuration d’un EtherChannel LACP sur Cisco IOS/IOS XE

> **Attention :** cet exemple est pédagogique. Adapte les noms d’interfaces, le numéro de groupe, les VLAN et les commandes à la plateforme. Effectue les changements sur une fenêtre de maintenance si le lien transporte du trafic de production, et prévois un moyen de retour arrière.

### 9.1 Scénario

Deux commutateurs, SW1 et SW2, sont reliés par deux câbles :

- SW1 `Gi1/0/1` vers SW2 `Gi1/0/1` ;
- SW1 `Gi1/0/2` vers SW2 `Gi1/0/2`.

Nous voulons former `Port-channel1` en trunk LACP, en autorisant les VLAN 10, 20 et 30. Les exemples ci-dessous montrent une configuration représentative, pas une recette universelle pour tous les modèles.

### 9.2 Configuration type sur SW1

```text
configure terminal
!
interface port-channel 1
 description LACP vers SW2
 switchport
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
!
interface range gigabitEthernet 1/0/1-2
 description Membres LACP vers SW2
 switchport
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 channel-group 1 mode active
 no shutdown
!
end
show etherchannel summary
show lacp neighbor
show interfaces port-channel 1
```

### 9.3 Configuration type sur SW2

```text
configure terminal
!
interface port-channel 1
 description LACP vers SW1
 switchport
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
!
interface range gigabitEthernet 1/0/1-2
 description Membres LACP vers SW1
 switchport
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 channel-group 1 mode active
 no shutdown
!
end
show etherchannel summary
show lacp neighbor
show interfaces port-channel 1
```

Les commandes d’ordre de configuration et certains paramètres peuvent différer selon IOS/IOS XE et selon que le modèle utilise une syntaxe de commutateur fixe ou modulaire. Suis la documentation du constructeur. En général, configure et vérifie les paramètres du port-channel et ceux des membres ; évite de laisser des différences de VLAN ou de mode entre les extrémités.

### 9.4 Variante : access au lieu de trunk

Si le port-channel transporte un seul VLAN non tagué, il peut être configuré en mode access. Les deux extrémités doivent alors utiliser la même logique de VLAN d’accès. Ne copie pas des commandes trunk dans un scénario access sans comprendre le rôle du lien.

### 9.5 Qu’est-ce qui se passe avec `channel-group 1 mode active` ?

La commande affecte le port physique au groupe 1 et met LACP en mode active sur ce membre. Le `Port-channel1` est l’interface logique qui représente le groupe. Les deux équipements doivent annoncer des paramètres compatibles et reconnaître le bon partenaire.

## 10. Vérifier le fonctionnement

La vérification ne se limite pas à un message « command accepted ». Confirme la formation du groupe, l’état des membres, la cohérence de la configuration et le transport réel du trafic.

Commandes Cisco souvent utiles :

```text
show etherchannel summary
show etherchannel 1 detail
show lacp neighbor
show interfaces port-channel 1
show interfaces gigabitEthernet 1/0/1
show interfaces gigabitEthernet 1/0/2
show running-config interface port-channel 1
show running-config interface gigabitEthernet 1/0/1
show spanning-tree interface port-channel 1
```

Toutes les commandes ne sont pas disponibles sous la même forme sur tous les modèles. D’autres constructeurs emploient des commandes différentes pour afficher la synthèse LAG, l’état LACP ou la table des voisins.

### 10.1 Comment lire `show etherchannel summary`

La sortie exacte dépend de la plateforme. Sur plusieurs systèmes IOS, la sortie présente le numéro de port-channel, le protocole et une liste de ports. Un indicateur `P` signifie couramment qu’un port est agrégé dans le groupe. `U` peut indiquer que le port-channel est en service ; `S` désigne couramment un groupe de couche 2. Un port marqué `I` ou `s` peut être individuel ou suspendu, selon le contexte et le modèle. **Lis toujours la légende de la sortie et la documentation de ta version** : les lettres ne sont pas universelles.

### 10.2 État attendu

Pour une agrégation saine, on souhaite normalement voir :

- le port-channel opérationnel ;
- les deux membres prévus, présents et agrégés ;
- le voisin LACP attendu ;
- les paramètres de trunk/VLAN conformes au plan ;
- aucune erreur physique persistante ni variation inattendue du compteur de paquets abandonnés ;
- la connectivité et les flux attendus fonctionnels.

## 11. Dépanner les problèmes les plus fréquents


<div class="lesson-diagram"><svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Arbre de diagnostic d’un EtherChannel inactif" viewBox="0 0 960 330" width="100%" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="328" rx="18" fill="#0b1220" stroke="#263449"/><text x="480" y="30" fill="#f1f5f9" font-size="21" font-weight="700" text-anchor="middle">Dépanner un EtherChannel qui ne monte pas</text><rect x="325" y="48" width="310" height="42" rx="8" fill="#17304a" stroke="#38bdf8" stroke-width="2"/><text x="480" y="74" fill="#e0f2fe" font-size="15" font-weight="700" text-anchor="middle">1. Le lien physique est-il UP ?</text><path d="M480 90 V111 H238 V128" fill="none" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#e7y)"/><path d="M480 90 V111 H722 V128" fill="none" stroke="#34d399" stroke-width="2.5" marker-end="url(#e7g)"/><text x="292" y="105" fill="#fde68a" font-size="12">Non</text><text x="668" y="105" fill="#a7f3d0" font-size="12">Oui</text><rect x="70" y="130" width="336" height="58" rx="8" fill="#332017" stroke="#fb923c"/><text x="238" y="153" fill="#ffedd5" font-size="14" font-weight="700" text-anchor="middle">Vérifier câble, optique,</text><text x="238" y="173" fill="#ffedd5" font-size="14" text-anchor="middle">transceiver, port et erreurs</text><rect x="555" y="130" width="336" height="58" rx="8" fill="#123029" stroke="#34d399"/><text x="723" y="153" fill="#d1fae5" font-size="14" font-weight="700" text-anchor="middle">2. Les LACP voisins sont-ils visibles ?</text><text x="723" y="173" fill="#a7f3d0" font-size="13" text-anchor="middle">show lacp neighbor (selon plateforme)</text><path d="M723 188 V208 H555 V224" fill="none" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#e7y)"/><path d="M723 188 V208 H820 V224" fill="none" stroke="#34d399" stroke-width="2.5" marker-end="url(#e7g)"/><text x="613" y="203" fill="#fde68a" font-size="12">Non</text><text x="790" y="203" fill="#a7f3d0" font-size="12">Oui</text><rect x="468" y="226" width="174" height="58" rx="8" fill="#332017" stroke="#fb923c"/><text x="555" y="249" fill="#ffedd5" font-size="13" text-anchor="middle">Modes active/passive,</text><text x="555" y="268" fill="#ffedd5" font-size="13" text-anchor="middle">pair / LACP activé</text><rect x="666" y="226" width="226" height="58" rx="8" fill="#142d3e" stroke="#38bdf8"/><text x="779" y="249" fill="#e0f2fe" font-size="13" text-anchor="middle">3. Vérifier membres,</text><text x="779" y="268" fill="#e0f2fe" font-size="13" text-anchor="middle">VLAN, vitesse et état Po</text><defs><marker id="e7y" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#fbbf24"/></marker><marker id="e7g" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#34d399"/></marker></defs></svg></div>


### Cas 1 — Le port-channel est down

**Vérifications :**

1. Les ports physiques sont-ils `up/up` ?
2. Le câblage relie-t-il réellement les membres aux ports prévus sur le bon commutateur distant ?
3. Les interfaces sont-elles administrativement actives ?
4. LACP est-il activé des deux côtés ?
5. Au moins un côté est-il en mode active ?
6. Les deux côtés utilisent-ils le même numéro/groupe logique, selon les exigences de leur plateforme ?
7. Une fonction locale ne bloque-t-elle pas le membre ?

**Hypothèse à tester :** si aucun voisin LACP n’apparaît, commence par le câblage, l’état des ports, la configuration LACP et le bon partenaire avant de modifier les VLAN.

### Cas 2 — Un membre est présent mais ne rejoint pas le groupe

Vérifie la vitesse, le duplex, le mode L2/L3, les VLAN, le VLAN natif, le nombre maximal de membres et toute différence de configuration. Sur certaines plateformes, un port incompatiblement configuré passe dans un état individuel ou suspendu.

Ne retire pas le membre du groupe au hasard. Compare les configurations des deux membres, puis compare les deux extrémités avec une checklist. Préserve les sorties de commande avant modification.

### Cas 3 — Un seul côté utilise LACP

Si SW1 est en mode `active` et SW2 est en mode statique, il ne faut pas s’attendre à ce que l’agrégation soit automatiquement négociée. Configure les deux côtés dans un mode compatible, selon la procédure de changement autorisée.

### Cas 4 — Passive des deux côtés

Deux ports en mode passive n’initient généralement pas la négociation. Passe l’un des côtés (ou les deux) en active, si cette modification correspond à la politique réseau, puis vérifie à nouveau les voisins et les membres.

### Cas 5 — Le port-channel est UP mais certains VLAN ne passent pas

L’agrégation et le transport VLAN sont deux choses différentes. Inspecte le mode access/trunk, la liste des VLAN autorisés, le VLAN natif, les VLAN créés sur les deux commutateurs, Spanning Tree, les ACL et le chemin de bout en bout. Une interface logique active ne garantit pas que le VLAN demandé soit autorisé.

### Cas 6 — La performance est inférieure à la capacité attendue

Une capacité agrégée de 2 × 1 Gbit/s ne garantit pas qu’une seule copie de fichier atteigne 2 Gbit/s. Identifie les flux utilisés, examine le type de hash, les compteurs des membres, les erreurs physiques et la capacité des appareils aux extrémités. Un lien peut être très utilisé pendant que l’autre reste presque inactif ; ce n’est pas automatiquement un défaut LACP.

### Cas 7 — La connexion coupe lorsqu’un membre échoue

Vérifie si le port-channel conserve son état, si le nombre de membres restants satisfait le seuil `min-links`, si la perte touche réellement un seul membre et si les équipements détectent correctement le défaut. Regarde les journaux et les compteurs. Un bref événement de reconvergence peut être normal, mais une coupure prolongée demande une investigation.

## 12. LACP, Spanning Tree et boucles de couche 2

Spanning Tree (STP/RSTP/MSTP selon le réseau) prévient les boucles de couche 2. Avec une agrégation correctement créée, le groupe est généralement présenté à STP comme un lien logique unique. Cela permet d’utiliser plusieurs liens sans que STP ne traite chaque câble comme une branche indépendante entre les mêmes deux switches.

Si les ports sont laissés comme des liens séparés sans agrégation, STP peut bloquer certains chemins redondants. Cela peut être normal, mais ce n’est pas équivalent à utiliser un EtherChannel : les membres bloqués ne participent pas nécessairement comme attendu à la capacité du groupe.

**Ne désactive pas STP pour « faire marcher » un EtherChannel.** Vérifie la configuration du LAG, le bon partenaire, les états STP et les consignes d’architecture. Sur une paire de commutateurs mal câblée, tenter de forcer plusieurs liens indépendants en forwarding peut causer une boucle, une tempête de broadcast ou une interruption massive.

## 13. Sécurité et bonnes pratiques de changement

Une agrégation est une modification de topologie. Elle peut impacter la connectivité, les VLAN, les politiques de sécurité et l’accès distant à l’équipement.

Avant le changement :

1. Confirme le propriétaire du lien, son rôle et les services qui l’utilisent.
2. Documente les câbles et ports des deux extrémités.
3. Sauvegarde les configurations et enregistre l’état initial.
4. Vérifie les versions, la compatibilité des équipements et la documentation constructeur.
5. Prépare un plan de retour arrière qui restaure une topologie cohérente des deux côtés.
6. Confirme la fenêtre de changement et la méthode d’accès de secours.

Après le changement :

1. Vérifie l’état du port-channel et tous les membres.
2. Vérifie les voisins LACP et les paramètres VLAN.
3. Teste la connectivité représentative des VLAN ou services transportés.
4. Surveille les erreurs, les drops, l’utilisation des membres et les journaux.
5. Si possible, effectue un test de résilience contrôlé sur un membre, seulement dans une fenêtre autorisée et avec un retour arrière prêt.
6. Documente les résultats et la configuration finale.

Évite les essais de panne non autorisés en production. Un test de désactivation d’un port peut être perturbant même si le port-channel est conçu pour être redondant.

## 14. Atelier guidé : deux switches et deux liens

### Énoncé

SW1 et SW2 sont reliés par deux liens Ethernet Gigabit. Le lien doit transporter les VLAN 10 et 20. Tu dois configurer l’agrégation LACP et confirmer que les deux membres sont actifs.

### Étape A — Préparation

- Définis les ports physiques de chaque côté et confirme le câblage.
- Vérifie qu’aucun des ports n’appartient déjà à un autre port-channel.
- Sauvegarde les configurations courantes.
- Confirme que VLAN 10 et VLAN 20 existent là où ils doivent être transportés.

### Étape B — Configuration

Sur les deux commutateurs, crée le port-channel, configure le trunk logique, et place les ports membres dans le même groupe LACP. Pour ce scénario pédagogique, `mode active` est utilisé de chaque côté. Adapte les commandes à la plateforme réelle.

### Étape C — Contrôle

Exécute les commandes disponibles pour examiner la synthèse de l’EtherChannel, les voisins LACP, l’état des interfaces logiques et physiques, ainsi que le trunk et les VLAN. Ne passe pas directement au test de panne si les membres ne sont pas tous agrégés.

### Étape D — Validation

- Un équipement du VLAN 10 peut-il joindre sa destination prévue ?
- Un équipement du VLAN 20 peut-il joindre sa destination prévue ?
- Le port-channel reste-t-il stable ?
- Les compteurs montrent-ils un trafic cohérent ?
- Les deux membres sont-ils correctement agrégés ?

### Étape E — Test de résilience contrôlé

Dans un laboratoire, désactive un seul membre et vérifie que l’agrégat continue de fonctionner par l’autre. Confirme la baisse de capacité attendue et les journaux. Réactive le membre, puis vérifie qu’il rejoint à nouveau le groupe. Ne considère pas l’exercice terminé avant d’avoir vérifié l’état final et la stabilité.

## 15. Exercice de dimensionnement

Un port-channel comprend trois liens de 1 Gbit/s. Réponds aux questions suivantes :

1. Quelle est la capacité de lien théorique maximale si les trois membres sont disponibles ?
2. Quelle capacité nominale de liens reste si un membre tombe en panne ?
3. Un seul flux TCP est-il assuré d’atteindre 3 Gbit/s ?
4. Que faut-il surveiller pour savoir si la charge est bien répartie ?

**Corrigé :**

1. Jusqu’à 3 Gbit/s de capacité agrégée théorique.
2. Environ 2 Gbit/s de capacité de lien nominale restante.
3. Non. Un flux utilise généralement un membre choisi par hachage ; son débit est limité par le lien et les autres facteurs de bout en bout.
4. Les compteurs et l’utilisation de chaque membre, les champs de hachage, le nombre de flux, les erreurs, les drops et les performances des équipements aux extrémités.

## 16. Quiz final

**1. Que représente le port-channel ?**

A. Un câble supplémentaire virtuel sans ports physiques.  
B. Une interface logique représentant plusieurs liens physiques agrégés.  
C. Un protocole de routage IP.

**2. Quel mode LACP initie la négociation ?**

A. Active.  
B. Passive.  
C. Access.

**3. Deux côtés en passive forment-ils généralement un groupe LACP ?**

A. Oui, car les deux attendent.  
B. Non, car aucun côté n’initie l’échange.

**4. Deux liens de 1 Gbit/s garantissent-ils 2 Gbit/s à une seule connexion ?**

A. Oui.  
B. Non, les flux sont généralement distribués par hachage entre les membres.

**5. Quel élément faut-il vérifier si un membre refuse de s’agréger ?**

A. Seulement la couleur des voyants.  
B. Vitesse, mode, VLAN, état LACP, câblage et compatibilité de la plateforme.  
C. Le nom du VLAN uniquement.

**6. Peut-on connecter sans condition les membres d’un LAG à deux switches indépendants ?**

A. Oui, tant que LACP est actif.  
B. Non : il faut une architecture multichâssis prise en charge si les liens aboutissent à plusieurs équipements.

**Réponses :** 1-B, 2-A, 3-B, 4-B, 5-B, 6-B.

## 17. Glossaire

- **Agrégation de liens / LAG :** groupe de ports Ethernet qui fonctionne comme une interface logique.
- **EtherChannel :** appellation Cisco pour cette fonction d’agrégation.
- **Port-channel :** interface logique représentant le groupe sur de nombreuses plateformes Cisco.
- **LACP :** protocole de contrôle qui négocie et surveille les membres d’un agrégat.
- **LACPDU :** unité de données de contrôle envoyée par LACP.
- **Active / Passive :** modes LACP ; active initie les échanges, passive répond.
- **Membre :** port physique appartenant au groupe.
- **Hash / hachage :** fonction qui utilise les caractéristiques d’un flux pour sélectionner un membre.
- **STP :** protocole qui évite les boucles de couche 2.
- **Trunk :** port transportant plusieurs VLAN avec des identifiants de VLAN.
- **VLAN natif :** VLAN utilisé pour le trafic non tagué sur un trunk 802.1Q, selon la configuration.
- **MLAG / vPC / VSX / stack :** mécanismes de constructeurs permettant, selon leur conception, de présenter une agrégation vers plusieurs châssis comme un seul partenaire logique.
- **Min-links :** seuil minimal éventuel de membres requis pour que le port-channel reste opérationnel.

## 18. Checklist rapide à conserver

**Avant de configurer :**

- [ ] Je connais le rôle des liens et les VLAN transportés.
- [ ] Je connais le câblage exact des deux extrémités.
- [ ] Les plateformes prennent en charge le mode d’agrégation souhaité.
- [ ] Le port-channel et le protocole choisis sont compatibles aux deux extrémités.
- [ ] Les ports ont vitesse, mode et paramètres cohérents.
- [ ] Je dispose d’une sauvegarde et d’un plan de retour arrière.

**Après la configuration :**

- [ ] Le port-channel est opérationnel.
- [ ] Tous les membres attendus sont agrégés.
- [ ] Le voisin LACP affiché correspond au bon équipement.
- [ ] Le trunk/access et les VLAN correspondent au plan.
- [ ] Les tests de connectivité fonctionnent.
- [ ] Les erreurs, drops et journaux sont contrôlés.
- [ ] Le changement est documenté.

## 19. Sources et documentation

Les commandes, limites de membres, états et options varient entre versions et modèles. Avant une intervention, consulte le guide correspondant exactement à l’équipement utilisé.

- [Cisco — EtherChannel Configuration Guide](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/etherchannel/etherchannel-configuration-guide/etherchannels.html) — principes, contraintes de compatibilité et modes LACP.
- [Cisco — EtherChannel](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/etherchannel/etherchannel-configuration-guide/m_ethernetchannel.html) — procédures de configuration et de vérification.
- [IEEE 802.1AX — Link Aggregation](https://standards.ieee.org/ieee/149/6768/) — référence normative sur l’agrégation de liens.
- Pour le dépannage, les commandes et les restrictions propres au matériel, utiliser les sections de surveillance et de diagnostic du [guide EtherChannel Cisco IOS XE](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/etherchannel/etherchannel-configuration-guide/etherchannels.html), puis sélectionner le guide correspondant au modèle installé.


**Objectif de sortie :** à la fin de ce cours, tu dois pouvoir expliquer la différence entre liens physiques et port-channel, décrire le rôle de LACP, comprendre la répartition des flux, effectuer une configuration de laboratoire simple, vérifier l’état de l’agrégat et dépanner les incompatibilités les plus courantes sans intervenir à l’aveugle en production.
