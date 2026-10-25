# Agrégation de liens (EtherChannel / LACP) — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Prérequis :** Ethernet, VLAN, interfaces trunk/access, adressage IP de base et commandes de consultation réseau.  
**Objectif :** concevoir, configurer, vérifier et dépanner un agrégat de liens sur plusieurs plateformes, en comprenant les limites de débit et les états LACP.

> **Important.** Les exemples sont des modèles de laboratoire fondés sur des syntaxes publiées par les constructeurs. Les commandes et options exactes dépendent du matériel, de la version logicielle et du modèle de commutateur. Avant une intervention en production, compare-les à la documentation de ta version et prévois un accès hors bande : une erreur de configuration d’un lien d’agrégation peut couper l’administration distante.

## 1. Mise en situation : pourquoi agréger des liens ?

Imagine un serveur de fichiers connecté à un commutateur par un câble Ethernet de 1 Gb/s. À mesure que les utilisateurs se multiplient, le lien devient un goulot d’étranglement. Installer deux câbles ne double pas automatiquement la capacité : sans configuration adaptée, ils peuvent créer une boucle de couche 2 ou un chemin redondant bloqué par STP. L’agrégation de liens traite les deux interfaces physiques comme un lien logique, à condition que les deux extrémités soient configurées de façon compatible.

Un groupe d’agrégation est appelé **LAG** (Link Aggregation Group). Les noms courants sont :

- **EtherChannel** ou **Port-Channel** sur Cisco ;
- **Aggregated Ethernet** (`ae0`, `ae1`…) sur Juniper ;
- **LAG** sur Aruba AOS-CX ;
- **bond** sous Linux, avec le mode `802.3ad` pour la négociation LACP.

La norme à connaître est IEEE 802.1AX, qui décrit l’agrégation de liens. LACP permet aux deux équipements d’échanger des informations pour former et maintenir l’agrégat. Les termes ne sont pas tous synonymes : *LAG* décrit le groupe logique ; *LACP* est un protocole de contrôle ; *EtherChannel* est la terminologie Cisco, qui peut fonctionner avec LACP, PAgP ou un mode statique selon la plateforme.


<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 370" role="img" aria-label="Deux liens physiques agrégés en un lien logique LAG entre un serveur et un commutateur" width="100%">
<defs><marker id="ec1cyan" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#38bdf8"/></marker><marker id="ec1green" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#34d399"/></marker></defs><style>@keyframes ecFlow{to{stroke-dashoffset:-30}}.ec-flow{stroke-dasharray:9 7;animation:ecFlow 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.ec-flow{animation:none}}</style>
<rect x="1" y="1" width="958" height="368" rx="18" fill="#090f1b" stroke="#26364b"/>
<text x="480" y="32" text-anchor="middle" fill="#f8fafc" font-size="21" font-weight="700">De plusieurs interfaces à un lien logique</text>
<rect x="55" y="112" width="220" height="152" rx="14" fill="#132236" stroke="#38bdf8" stroke-width="2"/><text x="165" y="140" text-anchor="middle" fill="#e0f2fe" font-size="18" font-weight="700">Serveur</text><rect x="87" y="161" width="156" height="31" rx="6" fill="#1e3a5f" stroke="#38bdf8"/><text x="165" y="181" text-anchor="middle" fill="#f0f9ff" font-size="14">NIC 1 · 1 Gb/s</text><rect x="87" y="204" width="156" height="31" rx="6" fill="#1e3a5f" stroke="#38bdf8"/><text x="165" y="224" text-anchor="middle" fill="#f0f9ff" font-size="14">NIC 2 · 1 Gb/s</text>
<rect x="685" y="112" width="220" height="152" rx="14" fill="#132236" stroke="#34d399" stroke-width="2"/><text x="795" y="140" text-anchor="middle" fill="#d1fae5" font-size="18" font-weight="700">Commutateur</text><rect x="715" y="161" width="160" height="31" rx="6" fill="#064e3b" stroke="#34d399"/><text x="795" y="181" text-anchor="middle" fill="#ecfdf5" font-size="14">Port membre 1</text><rect x="715" y="204" width="160" height="31" rx="6" fill="#064e3b" stroke="#34d399"/><text x="795" y="224" text-anchor="middle" fill="#ecfdf5" font-size="14">Port membre 2</text>
<path d="M243 176 C380 176 590 176 715 176" stroke="#38bdf8" stroke-width="3" fill="none" marker-end="url(#ec1cyan)" class="ec-flow"/><path d="M243 219 C380 219 590 219 715 219" stroke="#34d399" stroke-width="3" fill="none" marker-end="url(#ec1green)" class="ec-flow"/>
<rect x="340" y="104" width="280" height="45" rx="10" fill="#172554" stroke="#818cf8"/><text x="480" y="132" text-anchor="middle" fill="#e0e7ff" font-size="17" font-weight="700">LAG / Port-Channel / ae0</text>
<path d="M480 150 L480 165" stroke="#818cf8" stroke-width="2" stroke-dasharray="4 4"/><text x="480" y="294" text-anchor="middle" fill="#cbd5e1" font-size="15">Deux liens physiques, une interface logique vue par les couches supérieures</text><text x="480" y="320" text-anchor="middle" fill="#fbbf24" font-size="14">2 × 1 Gb/s = 2 Gb/s agrégés théoriques, pas 2 Gb/s par flux unique</text><text x="480" y="344" text-anchor="middle" fill="#94a3b8" font-size="12">Débit utile dépend du hachage, des flux, des équipements et des protocoles</text></svg></div>
### Ce que l’agrégation apporte

1. **Capacité agrégée plus grande :** plusieurs flux peuvent être répartis sur plusieurs membres.
2. **Résilience à la panne d’un lien :** si un membre tombe, les membres restants peuvent continuer de transférer le trafic.
3. **Gestion logique :** VLAN, STP et plusieurs fonctions sont configurés ou vus au niveau de l’interface logique selon la plateforme.
4. **Exploitation plus simple :** une interface logique remplace une multitude de liens parallèles gérés indépendamment.

### Ce que l’agrégation ne garantit pas

- Elle ne permet généralement pas à un flux TCP unique d’additionner à volonté la capacité de tous les membres.
- Elle ne protège pas d’une panne du commutateur distant, du châssis local, d’une alimentation commune ou d’un conduit physique commun.
- Elle ne rend pas identiques des interfaces incompatibles.
- Elle n’empêche pas à elle seule une saturation des files d’attente, un défaut de routage, un problème de VLAN ou une panne de serveur.
- Elle ne remplace ni la redondance de bout en bout ni une stratégie de sauvegarde.

## 2. Le vocabulaire à maîtriser

| Terme | Signification pratique |
|---|---|
| LAG | Groupe logique de ports physiques. |
| Port membre | Interface Ethernet physique rattachée au LAG. |
| LACPDU | Trame de contrôle LACP échangée entre voisins directement connectés. |
| Actor / Partner | Le côté local est l’Actor ; le voisin est le Partner dans l’échange LACP. |
| System ID | Identité LACP du système, composée d’une priorité et d’une adresse MAC système. |
| Key | Valeur permettant d’identifier les ports qui peuvent faire partie du même agrégateur sur un système. |
| Port priority | Priorité utilisée dans certaines décisions de sélection des ports. |
| Collecting | Le membre peut accepter le trafic reçu et le remettre au traitement normal du LAG. |
| Distributing | Le membre peut être choisi pour émettre le trafic de l’agrégat. |
| Active / Passive | Modes LACP : active initie l’échange, passive répond à un échange initié par le voisin. |
| Static / mode on | Agrégat forcé sans négociation LACP ; les deux extrémités doivent être configurées manuellement de façon cohérente. |
| Min-links | Nombre minimum de membres opérationnels exigé pour considérer le LAG comme actif sur les plateformes qui proposent cette fonction. |
| Hash / load-balancing | Algorithme qui associe les flux aux membres physiques. |
| MLAG / MC-LAG / VSX / vPC | Familles de fonctions permettant, selon les constructeurs et architectures, de présenter un LAG connecté à deux équipements logiques coordonnés. Les mécanismes ne sont pas interchangeables. |

## 3. Comment LACP forme l’agrégat

Les interfaces configurées pour LACP échangent des LACPDU qui annoncent l’identité du système, l’identité et la priorité du port, la clé, ainsi que des états. Les équipements utilisent ces informations pour déterminer quels ports peuvent appartenir au même agrégateur et si chaque port est autorisé à collecter et distribuer le trafic.

Le déroulé logique :

1. Le lien physique monte : couche optique/cuivre, vitesse et négociation Ethernet doivent fonctionner.
2. LACP découvre le partenaire et reçoit ses informations.
3. Les deux extrémités évaluent la compatibilité et la sélection des ports.
4. Les ports éligibles sont synchronisés et entrent dans des états d’agrégation utilisables.
5. Le plan de données distribue les flux parmi les membres sélectionnés.
6. En cas de changement — perte de signal, absence de LACPDU, changement de partenaire ou de configuration — un ou plusieurs membres peuvent être retirés du forwarding.


<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 400" role="img" aria-label="Négociation LACP entre deux équipements, échange bidirectionnel de LACPDU puis liens synchronisés" width="100%">
<defs><marker id="ec2blue" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#38bdf8"/></marker><marker id="ec2green" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#34d399"/></marker><marker id="ec2amber" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#fbbf24"/></marker></defs><style>@keyframes ecFlow{to{stroke-dashoffset:-30}}.ec-flow{stroke-dasharray:9 7;animation:ecFlow 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.ec-flow{animation:none}}</style>
<rect x="1" y="1" width="958" height="398" rx="18" fill="#090f1b" stroke="#26364b"/><text x="480" y="32" text-anchor="middle" fill="#f8fafc" font-size="21" font-weight="700">LACP : négociation avant le transfert normal</text>
<rect x="55" y="70" width="245" height="90" rx="13" fill="#132236" stroke="#38bdf8" stroke-width="2"/><text x="177" y="101" text-anchor="middle" fill="#e0f2fe" font-size="18" font-weight="700">Équipement A</text><text x="177" y="128" text-anchor="middle" fill="#bae6fd" font-size="15">LACP active</text>
<rect x="660" y="70" width="245" height="90" rx="13" fill="#132236" stroke="#34d399" stroke-width="2"/><text x="782" y="101" text-anchor="middle" fill="#d1fae5" font-size="18" font-weight="700">Équipement B</text><text x="782" y="128" text-anchor="middle" fill="#a7f3d0" font-size="15">LACP passive</text>
<path d="M300 91 C410 55 550 55 660 91" stroke="#38bdf8" stroke-width="3" fill="none" marker-end="url(#ec2blue)" class="ec-flow"/><text x="480" y="62" text-anchor="middle" fill="#7dd3fc" font-size="13">LACPDU (Actor / Partner)</text>
<path d="M660 136 C550 172 410 172 300 136" stroke="#34d399" stroke-width="3" fill="none" marker-end="url(#ec2green)" class="ec-flow"/><text x="480" y="184" text-anchor="middle" fill="#a7f3d0" font-size="13">Réponse LACPDU</text>
<rect x="83" y="220" width="794" height="63" rx="11" fill="#172554" stroke="#818cf8"/><text x="480" y="246" text-anchor="middle" fill="#e0e7ff" font-size="17" font-weight="700">Vérification des paramètres et de l’identité du partenaire</text><text x="480" y="268" text-anchor="middle" fill="#c7d2fe" font-size="13">System ID · port key · état · compatibilité · sélection de l’agrégateur</text>
<path d="M480 284 L480 310" stroke="#fbbf24" stroke-width="3" marker-end="url(#ec2amber)"/>
<rect x="180" y="316" width="600" height="57" rx="11" fill="#064e3b" stroke="#34d399" stroke-width="2"/><text x="480" y="340" text-anchor="middle" fill="#ecfdf5" font-size="17" font-weight="700">Collecting / Distributing</text><text x="480" y="360" text-anchor="middle" fill="#a7f3d0" font-size="13">Le membre est sélectionné pour recevoir et transmettre le trafic</text></svg></div>
### Active et passive : le piège classique

| Côté A | Côté B | Résultat attendu |
|---|---|---|
| active | active | La négociation peut démarrer des deux côtés. |
| active | passive | La négociation peut démarrer côté actif, le passif répond. |
| passive | passive | Aucun côté n’initie les échanges ; le LAG ne se forme normalement pas par LACP. |
| static/on | LACP active/passive | Incompatibilité de méthode : le fonctionnement ne doit pas être supposé. |

Les modes active et passive ne désignent pas un lien de secours et un lien principal : ce sont des rôles d’initiation du protocole. Le trafic de données n’est pas « envoyé seulement par le port actif » au sens de LACP. De même, « passive » n’est pas synonyme de « standby ».

### LACP lent et rapide

LACP peut envoyer les LACPDU à des cadences différentes. Les options nommées *fast* et *slow* ne signifient pas la même chose que les modes active/passive. Elles influencent la fréquence des échanges et, selon l’implémentation, le délai de détection d’un voisin devenu silencieux. Une détection rapide n’accélère pas nécessairement la réparation d’une panne optique ou d’un service applicatif. Vérifie les timers effectifs de chaque plateforme et ne promets pas une durée de convergence universelle.

### LACP n’est pas une preuve complète de santé applicative

Un LAG peut être `up` alors que les utilisateurs ne peuvent pas accéder au serveur. LACP ne teste pas la disponibilité d’une application, la résolution DNS, le routage de bout en bout ni les permissions d’un service. Il valide le fonctionnement du groupe de ports au niveau du lien.

## 4. Répartition du trafic : hash, flux et limites de débit

Les équipements choisissent généralement un membre à partir d’un hash de champs de trame ou de paquet : adresse MAC source/destination, adresses IP, ports TCP/UDP ou combinaison de champs. Les options disponibles dépendent de la plateforme, de la version et parfois du type d’interface. Le choix est fait par flux ou par paquet selon l’implémentation, mais les algorithmes conçus pour conserver l’ordre des paquets utilisent généralement des caractéristiques stables du flux.


<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" role="img" aria-label="Deux flux répartis par hachage sur des membres différents, un flux unique reste sur un seul membre" width="100%">
<defs><marker id="ec3a" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#38bdf8"/></marker><marker id="ec3b" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#34d399"/></marker><marker id="ec3c" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#fbbf24"/></marker></defs><style>@keyframes ecFlow{to{stroke-dashoffset:-30}}.ec-flow{stroke-dasharray:9 7;animation:ecFlow 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.ec-flow{animation:none}}</style>
<rect x="1" y="1" width="958" height="388" rx="18" fill="#090f1b" stroke="#26364b"/><text x="480" y="32" text-anchor="middle" fill="#f8fafc" font-size="21" font-weight="700">Répartition : le hachage choisit un membre par flux</text>
<rect x="42" y="82" width="225" height="245" rx="14" fill="#132236" stroke="#475569"/><text x="154" y="110" text-anchor="middle" fill="#f8fafc" font-size="18" font-weight="700">Flux entrants</text><rect x="69" y="132" width="170" height="43" rx="8" fill="#1e3a5f" stroke="#38bdf8"/><text x="154" y="159" text-anchor="middle" fill="#e0f2fe" font-size="15">Flux A · client 1</text><rect x="69" y="194" width="170" height="43" rx="8" fill="#064e3b" stroke="#34d399"/><text x="154" y="221" text-anchor="middle" fill="#ecfdf5" font-size="15">Flux B · client 2</text><rect x="69" y="256" width="170" height="43" rx="8" fill="#78350f" stroke="#fbbf24"/><text x="154" y="283" text-anchor="middle" fill="#fef3c7" font-size="15">Flux C · même client</text>
<rect x="350" y="137" width="260" height="145" rx="14" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="480" y="168" text-anchor="middle" fill="#e0e7ff" font-size="18" font-weight="700">Fonction de hachage</text><text x="480" y="198" text-anchor="middle" fill="#c7d2fe" font-size="14">MAC / IP / ports / protocole</text><text x="480" y="223" text-anchor="middle" fill="#c7d2fe" font-size="14">selon plateforme et configuration</text><text x="480" y="252" text-anchor="middle" fill="#fbbf24" font-size="13">Même tuple → généralement même membre</text>
<rect x="691" y="83" width="225" height="244" rx="14" fill="#132236" stroke="#475569"/><text x="803" y="111" text-anchor="middle" fill="#f8fafc" font-size="18" font-weight="700">Membres LAG</text><rect x="720" y="132" width="167" height="43" rx="8" fill="#1e3a5f" stroke="#38bdf8"/><text x="803" y="159" text-anchor="middle" fill="#e0f2fe" font-size="15">Lien 1</text><rect x="720" y="194" width="167" height="43" rx="8" fill="#064e3b" stroke="#34d399"/><text x="803" y="221" text-anchor="middle" fill="#ecfdf5" font-size="15">Lien 2</text><rect x="720" y="256" width="167" height="43" rx="8" fill="#334155" stroke="#94a3b8"/><text x="803" y="283" text-anchor="middle" fill="#f8fafc" font-size="15">Lien N</text>
<path d="M239 153 L350 173" stroke="#38bdf8" stroke-width="3" fill="none" marker-end="url(#ec3a)" class="ec-flow"/><path d="M239 215 L350 207" stroke="#34d399" stroke-width="3" fill="none" marker-end="url(#ec3b)" class="ec-flow"/><path d="M239 277 L350 242" stroke="#fbbf24" stroke-width="3" fill="none" marker-end="url(#ec3c)" class="ec-flow"/><path d="M610 177 L720 153" stroke="#38bdf8" stroke-width="3" fill="none" marker-end="url(#ec3a)" class="ec-flow"/><path d="M610 214 L720 215" stroke="#34d399" stroke-width="3" fill="none" marker-end="url(#ec3b)" class="ec-flow"/><path d="M610 245 L720 277" stroke="#fbbf24" stroke-width="3" fill="none" marker-end="url(#ec3c)" class="ec-flow"/><text x="480" y="359" text-anchor="middle" fill="#fbbf24" font-size="15" font-weight="700">3 liens de 1 Gb/s ne garantissent pas 3 Gb/s pour une seule connexion TCP</text><text x="480" y="378" text-anchor="middle" fill="#94a3b8" font-size="12">La capacité agrégée se révèle surtout lorsque plusieurs flux sont distribuables</text></svg></div>
### Pourquoi trois liens de 1 Gb/s ne font pas un flux de 3 Gb/s

Avec trois membres à 1 Gb/s, la capacité nominale agrégée maximale à sens donné est de 3 Gb/s si les trois membres transportent effectivement des flux. Mais une seule conversation peut être affectée à un seul membre. Par exemple, une copie de fichier utilisant une seule connexion TCP peut plafonner près de la capacité utile d’un membre, tandis que plusieurs clients peuvent se répartir sur les trois. Les chiffres réels dépendent de l’encapsulation, des protocoles, des équipements et de la charge.

Le hachage ne distribue pas forcément les octets uniformément. Trois flux de forte taille peuvent par hasard tomber sur un seul membre, tandis que plusieurs flux très modestes peuvent être répartis. Un hash fondé uniquement sur les adresses MAC risque de ne pas distinguer assez de flux lorsque plusieurs communications partagent les mêmes extrémités de couche 2. Un hash utilisant les champs IP/transport peut être plus fin si les deux équipements le prennent en charge et si les paquets sont visibles sans ambiguïté.

**Attention à l’asymétrie :** les deux sens ne sont pas nécessairement envoyés sur le même lien physique. Ce n’est pas forcément un problème, mais des outils de capture attachés à un seul membre peuvent ne pas voir l’ensemble du trafic. Les compteurs au niveau LAG et au niveau membre sont donc complémentaires.

### Mesurer correctement

- Mesure un flux unique puis plusieurs flux simultanés ; les résultats ne répondent pas à la même question.
- Observe les compteurs de chaque membre pendant la mesure ; un taux élevé sur un seul membre peut être cohérent avec le hash.
- Vérifie le sens de mesure, la capacité réellement négociée et les limitations du testeur.
- Utilise un outil de test qui génère plusieurs flux si tu cherches à évaluer la capacité agrégée, par exemple `iperf3` avec plusieurs flux parallèles dans un environnement autorisé.
- Ne confonds pas débit de ligne (bit/s), débit utile applicatif, paquets par seconde et latence.
- Tiens compte des buffers et de la congestion : un lien très sollicité peut provoquer de la latence avant d’atteindre la limite de débit.

## 5. Contraintes de compatibilité et conception

Les conditions exactes varient, mais il faut contrôler au minimum :

- **Vitesse / duplex :** les membres devraient avoir des paramètres compatibles. Un LAG peut refuser un membre ou produire un état non souhaité si sa vitesse diffère.
- **Média et caractéristiques du port :** optiques, câbles, capacité, FEC ou paramètres particuliers doivent correspondre aux recommandations matériel.
- **MTU :** une différence entre membres ou entre interfaces logiques peut créer des symptômes difficiles à reproduire.
- **Couche 2 :** le mode access/trunk, le VLAN d’accès, le VLAN natif et la liste des VLAN autorisés doivent être cohérents.
- **Couche 3 :** pour un agrégat routé, adresse IP, MTU, protocole de routage et paramètres doivent être au niveau logique approprié, pas distribués incohéremment sur les membres.
- **LACP :** mode, clé, identité système, priorités, paramètres de sélection et limite de membres actifs.
- **STP :** un agrégat Layer 2 est généralement présenté comme un seul port logique à STP ; si les liens ne forment pas vraiment le même agrégat, les protections contre les boucles peuvent avoir un comportement inattendu.
- **Capacités matérielles :** nombre maximal de LAG, de membres actifs, de membres en veille, et restrictions de modules/ASIC.
- **Topologie :** plusieurs câbles branchés sur le même switch ne donnent pas de résilience contre la panne du switch. Pour relier un hôte à deux switches, il faut une architecture multichâssis compatible, par exemple stack, vPC, MC-LAG ou VSX, en respectant le modèle de chaque constructeur.


<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 380" role="img" aria-label="Comparaison de deux interfaces membres avec configuration concordante et configuration divergente de VLAN" width="100%">
<defs><marker id="ec4good" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#34d399"/></marker><marker id="ec4bad" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#fb7185"/></marker></defs><style>@keyframes ecFlow{to{stroke-dashoffset:-30}}.ec-flow{stroke-dasharray:9 7;animation:ecFlow 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.ec-flow{animation:none}}</style>
<rect x="1" y="1" width="958" height="378" rx="18" fill="#090f1b" stroke="#26364b"/><text x="480" y="32" text-anchor="middle" fill="#f8fafc" font-size="21" font-weight="700">Compatibilité des membres : ce qui se ressemble doit réellement correspondre</text>
<rect x="40" y="70" width="420" height="265" rx="14" fill="#052e2b" stroke="#34d399" stroke-width="2"/><text x="250" y="100" text-anchor="middle" fill="#d1fae5" font-size="18" font-weight="700">Configuration cohérente</text><rect x="77" y="126" width="144" height="50" rx="8" fill="#064e3b" stroke="#34d399"/><text x="149" y="147" text-anchor="middle" fill="#ecfdf5" font-size="14">Port 1</text><text x="149" y="165" text-anchor="middle" fill="#a7f3d0" font-size="12">Trunk · VLAN 10,20</text><rect x="279" y="126" width="144" height="50" rx="8" fill="#064e3b" stroke="#34d399"/><text x="351" y="147" text-anchor="middle" fill="#ecfdf5" font-size="14">Port 2</text><text x="351" y="165" text-anchor="middle" fill="#a7f3d0" font-size="12">Trunk · VLAN 10,20</text><path d="M221 151 L279 151" stroke="#34d399" stroke-width="3" marker-end="url(#ec4good)" class="ec-flow"/><rect x="100" y="213" width="300" height="73" rx="10" fill="#064e3b" stroke="#34d399"/><text x="250" y="241" text-anchor="middle" fill="#ecfdf5" font-size="16" font-weight="700">LAG opérationnel</text><text x="250" y="263" text-anchor="middle" fill="#a7f3d0" font-size="13">Membres sélectionnés, trafic transféré</text>
<rect x="500" y="70" width="420" height="265" rx="14" fill="#3f1722" stroke="#fb7185" stroke-width="2"/><text x="710" y="100" text-anchor="middle" fill="#ffe4e6" font-size="18" font-weight="700">Configuration divergente</text><rect x="537" y="126" width="144" height="50" rx="8" fill="#881337" stroke="#fb7185"/><text x="609" y="147" text-anchor="middle" fill="#fff1f2" font-size="14">Port 1</text><text x="609" y="165" text-anchor="middle" fill="#fecdd3" font-size="12">Trunk · VLAN 10,20</text><rect x="739" y="126" width="144" height="50" rx="8" fill="#881337" stroke="#fb7185"/><text x="811" y="147" text-anchor="middle" fill="#fff1f2" font-size="14">Port 2</text><text x="811" y="165" text-anchor="middle" fill="#fecdd3" font-size="12">Trunk · VLAN 10,30</text><path d="M681 151 L739 151" stroke="#fb7185" stroke-width="3" marker-end="url(#ec4bad)" class="ec-flow"/><rect x="560" y="213" width="300" height="73" rx="10" fill="#881337" stroke="#fb7185"/><text x="710" y="241" text-anchor="middle" fill="#fff1f2" font-size="16" font-weight="700">Négociation / membre en échec</text><text x="710" y="263" text-anchor="middle" fill="#fecdd3" font-size="13">LAG partiel, suspendu ou trafic incohérent</text><text x="480" y="359" text-anchor="middle" fill="#cbd5e1" font-size="14">Comparer vitesse, duplex, VLAN, native VLAN, mode access/trunk, MTU et paramètres LACP</text></svg></div>
### Agrégat Layer 2 ou Layer 3 ?

**Layer 2 :** le LAG est un lien de commutation qui transporte une ou plusieurs VLAN. L’adresse IP de l’équipement est portée ailleurs, par exemple sur une SVI ou une interface VLAN. Les VLAN autorisés, le VLAN natif et STP sont des points de contrôle essentiels.

**Layer 3 :** les membres forment une interface logique routée ; l’adresse IP et le protocole de routage sont généralement configurés sur cette interface logique. Le modèle précis change selon le système d’exploitation réseau. Un lien routé agrégé peut simplifier les uplinks entre commutateurs de distribution et cœur.

Ne mélange pas les deux procédures. Sur Cisco, un Port-Channel L2 utilise `switchport`, tandis qu’un Port-Channel L3 utilise généralement `no switchport`. Sur Junos, une interface `ae` peut porter une configuration de commutation ou une configuration routée. Sous Linux, le bond est une interface logicielle à laquelle on attache la configuration IP/bridge/VLAN selon le scénario.

## 6. Configuration multiconstructeur — exemple de laboratoire

### Topologie commune

- Équipement A : ports physiques 1 et 2 vers l’équipement B.
- VLAN 10 et VLAN 20 traversent le lien en mode trunk.
- Deux liens Ethernet compatibles, chacun à 1 Gb/s.
- LAG logique nommé Port-Channel 10, `ae0`, `lag 20` ou `bond0`, selon la plateforme.
- LACP active sur l’équipement A et active/passive sur B.

Avant de saisir une configuration, relève la version du système, identifie les interfaces exactes, vérifie qu’elles ne servent pas déjà à un autre agrégat, sauvegarde la configuration et assure-toi d’avoir une console ou un accès hors bande. Remplace les noms d’interfaces et les VLAN d’exemple par ceux de ton laboratoire.

### 6.1 Cisco IOS XE — EtherChannel Layer 2 trunk avec LACP

Exemple indicatif sur une syntaxe Cisco IOS XE courante :

```text
configure terminal
!
interface range GigabitEthernet1/0/1-2
 description Membres LACP vers SW-B
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 channel-group 10 mode active
 no shutdown
!
interface Port-channel10
 description LAG LACP vers SW-B
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 no shutdown
end
!
show etherchannel summary
show lacp neighbor
show interfaces port-channel 10
show interfaces trunk
```

Points importants :

- Les interfaces membres doivent posséder des paramètres compatibles. Selon la plateforme, certaines commandes peuvent être héritées du Port-Channel ou doivent être configurées sur les membres pour être cohérentes.
- Évite de changer une interface déjà en service sans plan de migration : l’ajout au groupe peut provoquer une reconfiguration ou une interruption.
- La sortie `show etherchannel summary` permet d’identifier le protocole, le Port-Channel et l’état des membres ; la lettre d’état exacte est à interpréter selon la version.
- `mode active` démarre la négociation LACP. `mode passive` attend une initiation par le voisin. `mode on` est statique et ne fournit pas la validation LACP.
- Les limitations de membres actifs et les commandes disponibles changent avec le matériel et la version. Vérifie la documentation de la gamme exacte.

### 6.2 Juniper Junos — Aggregated Ethernet `ae0`

Sur les systèmes Junos où l’agrégation Ethernet doit être déclarée, configure le nombre d’interfaces agrégées, rattache les ports physiques à `ae0`, puis configure l’interface logique. Syntaxe illustrative :

```text
set chassis aggregated-devices ethernet device-count 1
set interfaces ge-0/0/0 ether-options 802.3ad ae0
set interfaces ge-0/0/1 ether-options 802.3ad ae0
set interfaces ae0 aggregated-ether-options lacp active
set interfaces ae0 unit 0 family ethernet-switching interface-mode trunk
set interfaces ae0 unit 0 family ethernet-switching vlan members VLAN10
set interfaces ae0 unit 0 family ethernet-switching vlan members VLAN20
```

Valide la syntaxe adaptée à ta plateforme Juniper, notamment si elle utilise le style de configuration Ethernet-switching ELS ou un modèle plus ancien. Certains systèmes prennent en charge des commandes de VLAN différentes. Vérifications typiques :

```text
show lacp interfaces
show interfaces ae0 extensive
show configuration interfaces ae0
show ethernet-switching interfaces
```

Points à retenir : `ae0` est le lien logique. Les interfaces physiques sont des membres de cet agrégat ; la configuration Layer 2 ou Layer 3 doit être placée au bon niveau. Pour une architecture MC-LAG, le `system-id`, l’`admin-key` et la configuration des deux châssis doivent être cohérents, mais ce scénario dépasse le LAG simple à un seul équipement distant.

### 6.3 Aruba AOS-CX — LAG 20

Exemple indicatif pour AOS-CX :

```text
configure terminal
interface lag 20
    no shutdown
    no routing
    lacp mode active
    vlan trunk native 1
    vlan trunk allowed 10,20
exit
interface 1/1/1
    no shutdown
    lag 20
exit
interface 1/1/2
    no shutdown
    lag 20
exit
write memory
```

Les détails exacts du `vlan trunk native`, de la liste VLAN et de la façon d’ajouter des membres dépendent de la gamme AOS-CX et de la version. Certaines versions présentent la configuration des membres et du LAG avec des nuances. Vérifie la CLI guide spécifique au switch. Commandes de vérification possibles :

```text
show lacp aggregates
show lacp interfaces
show interface lag 20
show running-config interface lag 20
```

**Attention :** ne transpose pas mécaniquement les commandes AOS-CX vers ArubaOS-Switch (ProVision) : syntaxe et capacités peuvent différer.

### 6.4 Linux — bonding en mode `802.3ad`

Le bonding Linux peut regrouper plusieurs interfaces Ethernet. Le mode `802.3ad` utilise LACP et nécessite que le commutateur en face configure les ports dans le même agrégat. Voici une séquence de laboratoire non persistante, à exécuter en console locale ou hors bande, car elle peut interrompre ta connexion si les interfaces transportent l’accès distant.

```bash
# Exemple à adapter aux interfaces réellement présentes
sudo modprobe bonding
sudo ip link add bond0 type bond mode 802.3ad
sudo ip link set enp1s0 down
sudo ip link set enp2s0 down
sudo ip link set enp1s0 master bond0
sudo ip link set enp2s0 master bond0
sudo ip link set bond0 up
sudo ip link set enp1s0 up
sudo ip link set enp2s0 up

# Contrôle de l'état LACP/bonding
cat /proc/net/bonding/bond0
ip -d link show bond0
ip -s link show bond0
```

Pour un hôte de laboratoire, configure ensuite l’adresse IP, le bridge, les VLAN et/ou le gestionnaire réseau au niveau qui convient à l’architecture. Ne configure pas indépendamment la même adresse IP sur chaque interface membre. La création par `ip link` n’est pas persistante après redémarrage ; Netplan, NetworkManager, systemd-networkd ou les outils de la distribution peuvent être utilisés pour rendre la configuration persistante. Leur syntaxe dépend de la distribution et de sa version.

Le fichier `/proc/net/bonding/bond0` est particulièrement utile pour afficher le mode, l’état MII, le partenaire LACP, le nombre de membres actifs et des informations de chaque esclave. La documentation du noyau souligne que le mode 802.3ad impose une configuration correspondante côté switch, et que l’algorithme de sélection des flux affecte la distribution réelle.

## 7. Règles de configuration transversales

Quel que soit le constructeur, applique ces règles :

1. **Créer l’agrégat logique et les membres dans un ordre documenté.** L’ordre exact dépend du système ; suis le guide plateforme.
2. **Configurer VLAN et mode d’interface au niveau approprié.** Ne laisse pas des membres avec des profils contradictoires.
3. **Utiliser LACP à moins d’avoir une raison opérationnelle documentée pour le statique.** LACP détecte une partie des erreurs de câblage et de compatibilité qu’un groupe forcé ne détecte pas.
4. **Éviter passive/passive.** Au moins un côté doit initier la négociation.
5. **Ne jamais agréger deux chemins vers deux switches indépendants** sauf si stack, vPC, MLAG, MC-LAG, VSX ou technologie équivalente est configurée et supportée de bout en bout.
6. **Documenter les ports et les câbles.** Étiquette les deux extrémités et conserve le schéma physique.
7. **Définir la capacité minimale acceptable.** Le paramètre `min-links` (quand disponible) peut empêcher le lien logique de rester up avec une seule liaison alors que le service exige deux ou trois membres.
8. **Vérifier le comportement de retour après panne.** Lorsqu’un membre revient, surveille la stabilité, le redistribution du trafic et les journaux.
9. **Contrôler les deux extrémités.** « UP » localement n’indique pas toujours que le groupe complet est sain.
10. **Ne pas modifier le hash pour masquer un autre problème.** Mesure avant et après chaque changement.

## 8. Dimensionnement et disponibilité

### Capacité brute

Pour `n` membres de capacité `C`, la capacité brute nominale dans une direction est approximativement :

`Capacité agrégée = nombre de membres actifs × capacité d’un membre`

Exemple : 4 × 10 Gb/s donnent 40 Gb/s nominaux pour des flux qui se répartissent bien. Cela ne signifie pas qu’une seule connexion obtiendra 40 Gb/s, ni que l’application verra 40 Gb/s utiles. Ethernet est full duplex : la capacité dans le sens A→B et dans le sens B→A se calcule séparément.

### Calcul de capacité après panne N-1

Avec 4 liens de 10 Gb/s, la perte d’un lien laisse 3 × 10 = 30 Gb/s nominaux. Si l’usage de pointe normal est de 27 Gb/s, après la panne la charge théorique de la capacité restante devient 27/30 = 90 %. C’est une faible marge pour les pics, l’effet du hash et les protocoles. La conception doit conserver assez de marge en condition dégradée.

| Nombre de membres actifs | Capacité nominale par direction si chaque lien vaut 10 Gb/s | Après perte d’un membre |
|---:|---:|---:|
| 2 | 20 Gb/s | 10 Gb/s |
| 3 | 30 Gb/s | 20 Gb/s |
| 4 | 40 Gb/s | 30 Gb/s |
| 8 | 80 Gb/s | 70 Gb/s |

Ces valeurs sont des maximums nominaux ; elles supposent que les flux peuvent utiliser les membres disponibles et que les équipements amont/aval ne constituent pas d’autres goulots d’étranglement.

### Min-links : décision de conception

Imaginons un service qui a besoin d’au moins 20 Gb/s de capacité nominale. Un LAG à quatre membres de 10 Gb/s peut fonctionner avec un membre restant si aucune limite n’est configurée, mais le service sera peut-être fortement dégradé. `min-links 2` peut indiquer que le groupe ne doit être considéré comme opérationnel que si au moins deux membres sont en état. Ce comportement varie selon le constructeur et ne remplace pas les tests applicatifs ; il peut aussi provoquer une interruption plus franche si le seuil n’est plus atteint.

La décision doit être liée à un niveau de service : rester partiellement disponible à capacité réduite, ou retirer complètement l’interface pour déclencher une autre stratégie de bascule ? Consigne les conséquences et teste-les.


<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" role="img" aria-label="Tolérance à la panne avec trois liens membres, perte d'un lien et capacité réduite" width="100%">
<defs><marker id="ec5green" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#34d399"/></marker><marker id="ec5amber" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#fbbf24"/></marker></defs><style>@keyframes ecFlow{to{stroke-dashoffset:-30}}.ec-flow{stroke-dasharray:9 7;animation:ecFlow 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.ec-flow{animation:none}}</style>
<rect x="1" y="1" width="958" height="358" rx="18" fill="#090f1b" stroke="#26364b"/><text x="480" y="32" text-anchor="middle" fill="#f8fafc" font-size="21" font-weight="700">Résilience : perte d’un membre sans perte de tout le LAG</text>
<rect x="45" y="95" width="160" height="150" rx="13" fill="#132236" stroke="#38bdf8" stroke-width="2"/><text x="125" y="125" text-anchor="middle" fill="#e0f2fe" font-size="18" font-weight="700">Switch A</text><text x="125" y="153" text-anchor="middle" fill="#bae6fd" font-size="14">Port-Channel 10</text><text x="125" y="177" text-anchor="middle" fill="#cbd5e1" font-size="13">3 × 1 Gb/s</text><rect x="755" y="95" width="160" height="150" rx="13" fill="#132236" stroke="#34d399" stroke-width="2"/><text x="835" y="125" text-anchor="middle" fill="#d1fae5" font-size="18" font-weight="700">Switch B</text><text x="835" y="153" text-anchor="middle" fill="#a7f3d0" font-size="14">Port-Channel 10</text><text x="835" y="177" text-anchor="middle" fill="#cbd5e1" font-size="13">3 × 1 Gb/s</text>
<path d="M205 129 L755 129" stroke="#34d399" stroke-width="4" marker-end="url(#ec5green)" class="ec-flow"/><path d="M205 168 L755 168" stroke="#34d399" stroke-width="4" marker-end="url(#ec5green)" class="ec-flow"/><path d="M205 207 L755 207" stroke="#fb7185" stroke-width="4" stroke-dasharray="7 7"/><path d="M465 190 L495 220 M495 190 L465 220" stroke="#fb7185" stroke-width="5" stroke-linecap="round"/><text x="480" y="99" text-anchor="middle" fill="#a7f3d0" font-size="14">Lien 1</text><text x="480" y="158" text-anchor="middle" fill="#a7f3d0" font-size="14">Lien 2</text><text x="480" y="246" text-anchor="middle" fill="#fda4af" font-size="14">Lien 3 en panne</text>
<rect x="235" y="274" width="490" height="57" rx="11" fill="#172554" stroke="#818cf8"/><text x="480" y="297" text-anchor="middle" fill="#e0e7ff" font-size="16" font-weight="700">2 membres restent opérationnels</text><text x="480" y="318" text-anchor="middle" fill="#c7d2fe" font-size="14">Capacité nominale théorique : 3 Gb/s → 2 Gb/s</text></svg></div>
## 9. STP, VLAN et sécurité opérationnelle

Un LAG de couche 2 est normalement vu comme une interface logique par Spanning Tree Protocol. STP ne traite pas chaque membre comme un lien de topologie indépendant lorsque ceux-ci appartiennent réellement au même agrégat. Une configuration incohérente, un membre connecté au mauvais équipement ou un mauvais mode statique peut néanmoins produire une topologie qui n’est pas celle attendue.

### Liste de vérification Layer 2

- Le trunk porte-t-il les VLAN attendus aux deux extrémités ?
- Le VLAN natif est-il concordant ? Une différence peut causer des trames non taguées classées dans le mauvais VLAN.
- Le port-channel est-il bien dans l’état STP attendu et sans changements de topologie anormaux ?
- Les VLAN existent-ils sur les deux commutateurs ?
- Les ACL, port-security, DHCP snooping, DAI ou autres fonctions de protection sont-elles applicables au niveau logique, membre ou les deux selon la plateforme ?
- Une fonction de miroir/SPAN observe-t-elle le LAG ou seulement un membre physique ? La capture peut être incomplète si le trafic n’est pas distribué sur le port surveillé.

### Trunks minimaux

Pour des liens d’infrastructure, n’autorise que les VLAN nécessaires plutôt que tous les VLAN par défaut, si ton design et les outils d’exploitation le permettent. Documente explicitement le VLAN natif et ne suppose pas que la valeur par défaut est la même partout. Les commandes et les options de contrôle de VLAN varient entre les versions et les gammes.

## 10. Dépannage systématique

Un dépannage efficace sépare la couche physique, le contrôle LACP, la configuration, puis le plan de données. Ne change pas simultanément le mode LACP, les VLAN, le hash et le câblage : tu perdrais la capacité d’identifier la cause.


<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 450" role="img" aria-label="Arbre de diagnostic d'un EtherChannel qui ne fonctionne pas : physique, LACP, compatibilité, VLAN, hashing" width="100%">
<defs><marker id="ec6blue" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#38bdf8"/></marker><marker id="ec6amber" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#fbbf24"/></marker></defs><style>@keyframes ecFlow{to{stroke-dashoffset:-30}}.ec-flow{stroke-dasharray:9 7;animation:ecFlow 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.ec-flow{animation:none}}</style>
<rect x="1" y="1" width="958" height="448" rx="18" fill="#090f1b" stroke="#26364b"/><text x="480" y="32" text-anchor="middle" fill="#f8fafc" font-size="21" font-weight="700">Diagnostic : suivre une séquence qui isole les causes</text>
<rect x="325" y="56" width="310" height="48" rx="10" fill="#172554" stroke="#818cf8"/><text x="480" y="85" text-anchor="middle" fill="#e0e7ff" font-size="16" font-weight="700">1. LAG up et membres présents ?</text><path d="M480 104 L480 130" stroke="#38bdf8" stroke-width="3" marker-end="url(#ec6blue)" class="ec-flow"/>
<rect x="325" y="134" width="310" height="48" rx="10" fill="#132236" stroke="#38bdf8"/><text x="480" y="163" text-anchor="middle" fill="#e0f2fe" font-size="15">2. Liens physiques / erreurs / optiques</text><path d="M480 182 L480 208" stroke="#38bdf8" stroke-width="3" marker-end="url(#ec6blue)" class="ec-flow"/>
<rect x="325" y="212" width="310" height="48" rx="10" fill="#132236" stroke="#38bdf8"/><text x="480" y="241" text-anchor="middle" fill="#e0f2fe" font-size="15">3. Voisin LACP / actor-partner / key</text><path d="M480 260 L480 286" stroke="#38bdf8" stroke-width="3" marker-end="url(#ec6blue)" class="ec-flow"/>
<rect x="325" y="290" width="310" height="48" rx="10" fill="#132236" stroke="#38bdf8"/><text x="480" y="319" text-anchor="middle" fill="#e0f2fe" font-size="15">4. Paramètres L2/L3 cohérents ?</text><path d="M480 338 L480 364" stroke="#38bdf8" stroke-width="3" marker-end="url(#ec6blue)" class="ec-flow"/>
<rect x="325" y="368" width="310" height="49" rx="10" fill="#064e3b" stroke="#34d399"/><text x="480" y="389" text-anchor="middle" fill="#ecfdf5" font-size="15" font-weight="700">5. Vérifier VLAN, MTU, STP, IP et hashing</text><text x="480" y="407" text-anchor="middle" fill="#a7f3d0" font-size="12">Valider chaque hypothèse avec compteurs et trafic</text>
<rect x="45" y="211" width="220" height="106" rx="11" fill="#3f1722" stroke="#fb7185"/><text x="155" y="238" text-anchor="middle" fill="#ffe4e6" font-size="15" font-weight="700">Si échec à une étape</text><text x="155" y="263" text-anchor="middle" fill="#fecdd3" font-size="13">Consigner preuve, heure,</text><text x="155" y="283" text-anchor="middle" fill="#fecdd3" font-size="13">impact et changement observé</text><path d="M325 236 L265 236" stroke="#fbbf24" stroke-width="3" marker-end="url(#ec6amber)" class="ec-flow"/><text x="295" y="224" text-anchor="middle" fill="#fbbf24" font-size="12">NON</text><text x="496" y="125" text-anchor="start" fill="#94a3b8" font-size="12">OUI ↓</text></svg></div>
### Étape A — Vérifier le physique

1. Confirmer que les interfaces sont administrativement activées et ont un lien.
2. Contrôler vitesse, duplex, erreurs CRC, pertes de signal, puissance optique, FEC et compteurs de drops lorsqu’ils sont disponibles.
3. Vérifier la correspondance de câblage A1↔B1, A2↔B2. Identifier les membres connectés à un autre switch que celui attendu.
4. Comparer les compteurs avant/après un test contrôlé, plutôt que lire un compteur cumulatif isolément.

Si le lien physique est down, LACP ne peut pas le rendre opérationnel. Résous d’abord le câble, l’optique, le transceiver, la compatibilité vitesse/FEC ou le port.

### Étape B — Vérifier la négociation

1. Confirmer le mode LACP sur chaque extrémité.
2. Vérifier que les voisins affichent le bon System ID et les bons ports partenaires.
3. Rechercher passive/passive, clé incohérente, nombre de membres inattendu ou ports suspendus/standalone.
4. Vérifier Collecting/Distributing ou l’équivalent exposé par le système.
5. Examiner les compteurs LACP, les logs système et les changements de voisinage.

### Étape C — Vérifier les paramètres de forwarding

1. Comparer la configuration logique et les paramètres des membres.
2. Sur Layer 2, comparer access/trunk, VLAN autorisés, VLAN natif, STP et MTU.
3. Sur Layer 3, vérifier adresse sur l’interface logique, routage, adjacency, MTU et routes retour.
4. Vérifier les ACL, QoS, policers et éventuelles différences de configuration matériel.
5. Contrôler si les paquets sont visibles dans les deux directions au niveau correct.

### Étape D — Comprendre une performance « trop faible »

Si le LAG est operational mais les performances sont décevantes :

- comparer débit d’un seul flux et plusieurs flux ;
- observer le trafic par membre pour détecter la polarisation ;
- vérifier les congestions, drops, pauses Ethernet et erreurs ;
- examiner le hash disponible et les champs pris en compte ;
- contrôler si l’autre extrémité utilise un algorithme similaire mais indépendant ;
- valider la capacité des uplinks, du serveur et des équipements de test ;
- s’assurer qu’aucun membre n’est actif à une vitesse inférieure à celle prévue.

### Symptômes courants et pistes de cause

| Symptôme | Causes possibles | Vérification prioritaire |
|---|---|---|
| Aucun LAG ne se forme | Passive/passive, mauvais mode, mauvais câblage, LACP absent d’un côté | Voisins LACP, mode configuré, état physique |
| Un seul membre est actif | Mauvaise compatibilité, port suspendu, limite de membres, clé/ID ou vitesse | État détaillé LACP, configuration et logs |
| Le LAG est up mais des VLAN ne passent pas | Liste VLAN, native VLAN, VLAN absent, STP ou ACL | Trunk/interface logique, table VLAN, compteurs |
| Débit faible sur un flux | Hash par flux, limite à la vitesse d’un membre, goulet applicatif | Test mono-flux puis multi-flux, compteurs par membre |
| Un membre cumule beaucoup plus de trafic | Peu de flux, mauvais hash ou valeurs de flux similaires | Distribution par membre, fonction de hash prise en charge |
| Coupure lors du retrait d’un lien | Mauvaise configuration, min-links trop élevé, résilience non testée ou trafic concentré | État avant/après, événements, seuil min-links, tests applicatifs |
| Deux liens connectés à deux commutateurs mais STP bloque ou LAG ne monte pas | Pas de stack/MLAG/vPC/VSX ou technologie équivalente, design incompatible | Architecture multichâssis et état de pair |
| Capture Wireshark ne voit qu’une partie du flux | SPAN sur un membre, asymétrie, hash, direction de copie | Point de capture, SPAN au niveau LAG, capture des deux côtés |

## 11. Procédure de changement avec retour arrière

### Avant le changement

- Identifier le service, les équipements, les ports, les VLAN et les équipes concernées.
- Sauvegarder la configuration des deux extrémités et capturer les sorties d’état initiales.
- Vérifier la documentation de la version et les limites de matériel.
- Préparer les commandes exactes, la séquence de déploiement et une procédure de rollback.
- Confirmer un accès console/hors bande. Éviter de dépendre uniquement du lien qui va être modifié.
- Planifier une fenêtre, avertir les utilisateurs et définir un critère d’abandon.

### Pendant le changement

1. Appliquer la configuration à une extrémité en respectant le guide de la plateforme.
2. Configurer l’extrémité opposée et surveiller la négociation.
3. Contrôler l’état global, l’état des membres, les VLAN et la table MAC ou les adjacences IP.
4. Tester le plan de données : ping ciblé si pertinent, application réelle, débit mono/multi-flux si nécessaire.
5. Retirer un membre à la fois pour tester la tolérance à la panne, uniquement après la validation initiale et si la fenêtre le permet.
6. Revenir à l’état initial si un critère d’échec est rencontré.

### Après le changement

- Vérifier qu’il n’y a pas de nouveaux logs d’erreur, de CRC ou de drops.
- Confirmer l’état LACP des membres et l’équilibre global du trafic avec le niveau de détail attendu.
- Vérifier les services applicatifs, pas seulement le statut du Port-Channel/LAG.
- Documenter la configuration effective, la topologie physique et le test de perte d’un membre.
- Mettre à jour la source de vérité, le plan de câblage et le runbook.

## 12. Atelier pratique guidé

### Scénario

Une entreprise connecte un serveur de virtualisation à un switch par deux interfaces 10 Gb/s. Les deux liens montent physiquement, mais seul un membre est visible comme actif. Après avoir corrigé la configuration, le LAG est up, mais un test de transfert depuis une seule VM plafonne aux alentours de 9 Gb/s. Plusieurs VM simultanées atteignent un débit global plus élevé.

### Exercice 1 — Diagnostic du seul membre actif

Hypothèses possibles : les interfaces sont configurées dans des groupes différents ; une interface possède un paramètre incompatible ; le serveur et le switch n’ont pas le même mode d’agrégation ; les deux interfaces ne sont pas membres du même partenaire logique ; une limitation de membres actifs est configurée. Les vérifications commencent par l’état détaillé LACP, le voisin et la configuration effective. Ne force pas `mode on` comme raccourci : cela retire la validation du protocole et peut masquer une incompatibilité.

### Exercice 2 — Le débit mono-flux plafonne

Ce résultat peut être normal. L’algorithme de distribution envoie une conversation donnée sur un seul membre afin de préserver l’ordre des paquets. Lance plusieurs flux en laboratoire et surveille les compteurs par membre. Si la charge totale se répartit, le LAG peut fonctionner comme prévu. Si un grand nombre de flux restent sur le même membre, vérifie les champs de hash et les facteurs limitant le test.

### Exercice 3 — Un VLAN est inaccessible

Compare les VLAN autorisés sur les deux interfaces logiques. Vérifie que le VLAN existe, que la gateway est accessible, que STP ne bloque pas le port logique, que le VLAN natif ne diffère pas et qu’aucune ACL ne bloque le trafic. Une interface LAG `up` ne prouve pas que chaque VLAN est correctement transporté.

### Exercice 4 — Test de résilience

Dans une fenêtre de test, enregistre les compteurs et la session applicative, puis désactive volontairement un membre. Le résultat attendu est une diminution de la capacité disponible et un rééquilibrage des flux qui peuvent changer de membre, pas forcément une hausse instantanée du débit sur chaque connexion. Note le délai observable, la perte de paquets, les journaux, l’état du membre et le retour à l’état normal. Réactive le lien et confirme la stabilité.

## 13. Exemple de checklist opérationnelle

### Conception

- [ ] Les besoins de capacité et de résilience sont définis.
- [ ] Le type d’agrégat (Layer 2/Layer 3) est décidé.
- [ ] Le support LACP et la limite de membres sont vérifiés sur les deux plateformes.
- [ ] Le scénario multichâssis, le cas échéant, est officiellement supporté.
- [ ] La capacité N-1 conserve une marge suffisante.

### Configuration

- [ ] Même groupe logique aux deux extrémités.
- [ ] Au moins un côté initie LACP.
- [ ] Vitesse, MTU, VLAN et paramètres d’interface sont cohérents.
- [ ] L’adresse IP est au niveau logique approprié pour un agrégat routé.
- [ ] Le nombre de membres actifs et min-links sont adaptés.

### Vérification et exploitation

- [ ] Tous les membres attendus sont sélectionnés et en forwarding.
- [ ] Les System ID et partenaires correspondent au câblage.
- [ ] Les VLAN ou adjacences Layer 3 fonctionnent.
- [ ] Les tests d’application sont réussis.
- [ ] Les tests mono-flux et multi-flux sont interprétés correctement.
- [ ] Une panne membre a été testée et documentée.
- [ ] Le plan de câblage, le runbook et la configuration sauvegardée sont à jour.

## 14. Quiz de validation

**1.** Quelle différence entre LAG et LACP ?  
**Réponse :** Le LAG est le groupe logique de liens ; LACP est le protocole de contrôle qui négocie et maintient l’agrégation dynamique.

**2.** Pourquoi passive/passive ne forme-t-il normalement pas un agrégat LACP ?  
**Réponse :** Aucun côté n’initie les LACPDU ; les deux attendent une initiation du partenaire.

**3.** Qu’obtient-on théoriquement avec quatre liens de 10 Gb/s ?  
**Réponse :** Jusqu’à 40 Gb/s de capacité agrégée nominale par direction avec une bonne répartition, mais pas une garantie de 40 Gb/s pour un seul flux.

**4.** Le LAG est up : peut-on conclure que le VLAN 20 passe ?  
**Réponse :** Non. Il faut vérifier VLAN autorisés, existence du VLAN, STP, MTU, ACL et connectivité de bout en bout.

**5.** Deux membres sont connectés à deux switches autonomes : est-ce automatiquement un LAG valide ?  
**Réponse :** Non. Il faut un mécanisme multichâssis supporté et configuré (par exemple stack, vPC, MC-LAG ou VSX selon le constructeur) ou relier le LAG à un seul système logique.

**6.** Quel est l’intérêt de `min-links` ?  
**Réponse :** Exiger un nombre minimum de membres opérationnels pour que l’agrégat soit considéré actif. La décision doit se baser sur les objectifs de disponibilité, et le comportement exact dépend de la plateforme.

**7.** Pourquoi une copie unique plafonne-t-elle à la capacité d’un membre ?  
**Réponse :** Le hash affecte généralement un flux à un membre pour préserver l’ordre des paquets. Les flux parallèles peuvent utiliser différents membres.

**8.** LACP active/passive indique-t-il un lien principal et un lien de secours ?  
**Réponse :** Non. Ces modes déterminent qui initie les échanges de contrôle ; ils ne désignent pas l’état actif/secours des câbles.

## 15. Glossaire rapide

- **Actor/Partner :** extrémités d’un échange LACP.
- **Aggregation key :** valeur participant à la sélection des ports qui appartiennent au même agrégateur.
- **Bond :** interface d’agrégation logicielle Linux.
- **Collecting/Distributing :** états de transfert d’un port membre LACP.
- **EtherChannel :** terme Cisco désignant une agrégation de liens.
- **Hashing :** choix de membre basé sur des champs de la communication.
- **LAG :** groupe de liens logiques constitué de plusieurs liens physiques.
- **LACP :** Link Aggregation Control Protocol.
- **LACPDU :** unité de données de contrôle LACP.
- **MLAG/MC-LAG :** mécanismes permettant une agrégation vers plusieurs équipements coordonnés ; les implémentations sont spécifiques aux constructeurs.
- **Min-links :** seuil minimal de membres actifs.
- **Port-Channel :** interface logique d’agrégation dans Cisco IOS/IOS XE.
- **STP :** Spanning Tree Protocol.
- **VLAN natif :** VLAN utilisé pour les trames non taguées sur certains trunks 802.1Q.

## 16. Références techniques officielles

- IEEE, **802.1AX — Link Aggregation** : https://1.ieee802.org/tsn/802-1ax-rev/ (cadre normalisé d’agrégation de liens).
- Cisco, **EtherChannel Configuration Guide — Cisco IOS XE** : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/etherchannel/etherchannel-configuration-guide/etherchannels.html
- Juniper, **Configuring Aggregated Ethernet LACP** : https://www.juniper.net/documentation/us/en/software/junos/fusion-enterprise/topics/task/interfaces-configuring-aggregated-ethernet-lacp-l2.html
- Aruba, **AOS-CX Link Aggregation Guide** : https://www.arubanetworks.com/techdocs/AOS-CX/10.06/PDF/6200/Link%20Aggregation.pdf
- Linux Kernel, **Ethernet Bonding Driver documentation** : https://docs.kernel.org/networking/bonding.html

Ces références sont des points de départ. Pour un déploiement réel, utilise les documents qui correspondent au modèle et à la version logicielle installée.


**À retenir :** LACP améliore la gestion de l’agrégation et permet d’identifier certaines incompatibilités, mais il ne remplace pas la conception réseau. Pour configurer un LAG correctement, aligne les deux extrémités, vérifie les états du protocole, mesure la distribution réelle des flux et teste explicitement le fonctionnement en condition dégradée.
