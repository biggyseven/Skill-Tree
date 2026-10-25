# Wi-Fi 802.11 — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Prérequis :** notions de base sur SSID, point d’accès, client, adresse IP, Ethernet, DHCP et sécurité Wi-Fi.  
**Objectif :** analyser le comportement réel d’un réseau Wi-Fi, distinguer les problèmes radio des problèmes d’authentification et de services IP, choisir des paramètres radio raisonnés et résoudre les incidents à partir de preuves plutôt que de suppositions.

> **Périmètre.** Ce cours porte sur la famille IEEE 802.11 et les pratiques de conception, de sécurisation et de dépannage. Les valeurs réglementaires des bandes et des canaux varient selon le pays, l’équipement et la version du firmware. Avant toute configuration de production, vérifier la réglementation locale, la fiche technique et le guide de l’équipement.

## 1. Relier les bases aux situations réelles

Un réseau Wi-Fi est un réseau local dont la liaison entre la station et le point d’accès est radio. La couche physique (PHY) définit notamment la modulation, les canaux et les mécanismes de transmission. La couche MAC organise l’accès au médium, l’adressage de couche 2, les accusés de réception, les retransmissions et la gestion de l’association. Au-delà de cette liaison, des fonctions classiques restent nécessaires : segmentation en VLAN, attribution IP, routage, DNS, contrôle d’accès et sécurité applicative.

Il faut distinguer plusieurs noms qui se ressemblent :

- **SSID** : nom logique présenté à l’utilisateur, par exemple `Bureau-Staff`.
- **BSSID** : identifiant généralement fondé sur une adresse MAC pour une cellule radio / BSS donnée. Deux points d’accès qui diffusent le même SSID peuvent annoncer des BSSID différents.
- **STA (station)** : client Wi-Fi, comme un téléphone, un ordinateur ou un capteur.
- **AP (Access Point)** : point d’accès qui fournit l’accès radio au réseau de distribution.
- **BSS** : Basic Service Set, ensemble radio centré sur un AP dans une infrastructure classique.
- **ESS** : ensemble de BSS qui présentent un service WLAN coordonné, souvent avec le même SSID et des possibilités d’itinérance.
- **Canal** : portion de spectre utilisée par une transmission. La largeur effective du canal et le domaine réglementaire conditionnent la sélection disponible.
- **RSSI** : indicateur de puissance reçue. Il est souvent rapporté en dBm, mais sa mesure et sa calibration dépendent du matériel.
- **SNR** : rapport signal/bruit, exprimé en dB. Un signal fort peut rester de mauvaise qualité si le bruit ou les interférences sont également forts.
- **Airtime (temps d’antenne)** : temps pendant lequel le médium est occupé par les trames et les mécanismes associés. Il est souvent une ressource plus utile à diagnostiquer que le débit PHY annoncé.

### 1.1 Le vrai chemin d’une connexion

<div class="wifi-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 340" width="100%" role="img" aria-label="Étapes de connexion d’une station Wi-Fi à un point d’accès">
<defs><marker id="w1arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#55d6be"/></marker><style>@keyframes w1flow{to{stroke-dashoffset:-24}}.w1flow{stroke-dasharray:8 7;animation:w1flow 1.8s linear infinite}@media(prefers-reduced-motion:reduce){.w1flow{animation:none}}</style></defs>
<rect x="18" y="18" width="864" height="304" rx="18" fill="#0b1220" stroke="#27364b"/>
<text x="450" y="48" fill="#f1f5f9" font-size="20" font-weight="700" text-anchor="middle">Association : du réseau détecté à l’accès IP</text>
<rect x="44" y="90" width="165" height="78" rx="12" fill="#122b44" stroke="#60a5fa" stroke-width="2"/><text x="126" y="120" fill="#dbeafe" text-anchor="middle" font-size="15" font-weight="700">Station cliente</text><text x="126" y="143" fill="#93c5fd" text-anchor="middle" font-size="12">scan actif / passif</text>
<rect x="261" y="90" width="165" height="78" rx="12" fill="#12352f" stroke="#55d6be" stroke-width="2"/><text x="343" y="120" fill="#d1fae5" text-anchor="middle" font-size="15" font-weight="700">Point d’accès</text><text x="343" y="143" fill="#99f6e4" text-anchor="middle" font-size="12">BSSID / SSID</text>
<rect x="478" y="90" width="165" height="78" rx="12" fill="#31244a" stroke="#c4b5fd" stroke-width="2"/><text x="560" y="120" fill="#ede9fe" text-anchor="middle" font-size="15" font-weight="700">Sécurité du WLAN</text><text x="560" y="143" fill="#c4b5fd" text-anchor="middle" font-size="12">802.1X / PSK / clés</text>
<rect x="695" y="90" width="165" height="78" rx="12" fill="#3b2d19" stroke="#fbbf24" stroke-width="2"/><text x="777" y="120" fill="#fef3c7" text-anchor="middle" font-size="15" font-weight="700">Accès réseau</text><text x="777" y="143" fill="#fcd34d" text-anchor="middle" font-size="12">VLAN / DHCP / IP</text>
<path class="w1flow" d="M209 129 H255" fill="none" stroke="#55d6be" stroke-width="3" marker-end="url(#w1arrow)"/><path class="w1flow" d="M426 129 H472" fill="none" stroke="#55d6be" stroke-width="3" marker-end="url(#w1arrow)"/><path class="w1flow" d="M643 129 H689" fill="none" stroke="#55d6be" stroke-width="3" marker-end="url(#w1arrow)"/>
<text x="450" y="211" fill="#cbd5e1" font-size="13" text-anchor="middle">1. Découvrir · 2. Authentification 802.11 · 3. Association · 4. 802.1X/PSK et établissement des clés</text>
<path d="M777 170 V235 H126 V175" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="5 6" marker-end="url(#w1arrow)"/><text x="450" y="259" fill="#94a3b8" font-size="12" text-anchor="middle">En entreprise, EAP/802.1X intervient après l’association; viennent ensuite IP, passerelle, DNS et applications</text>
<text x="450" y="294" fill="#fbbf24" font-size="12" text-anchor="middle">Une association Wi-Fi réussie ne garantit pas que DHCP, DNS ou Internet fonctionnent.</text>
</svg></div>

La réussite des premières étapes n’atteste pas de la santé du parcours complet. Un client peut voir le SSID mais ne pas s’associer ; s’associer mais échouer lors de la négociation de sécurité ; être connecté au WLAN sans recevoir d’adresse IP ; obtenir une adresse mais ne pas résoudre les noms DNS ; ou accéder aux services internes sans avoir de sortie Internet. Le diagnostic doit donc identifier le **premier point où le comportement attendu ne se produit plus**.

### 1.2 Ce que le Wi-Fi ne garantit pas

Le débit physique affiché par un client (par exemple 866 Mbit/s) n’est pas le débit applicatif garanti. Le protocole partage un canal avec les clients, les AP voisins et parfois des sources d’interférence non Wi-Fi. Les trames de contrôle, les en-têtes, les attentes, les confirmations, les retransmissions et le partage du médium consomment une partie de la capacité. Le résultat dépend aussi du nombre de flux, du serveur distant, du chemin filaire, du VPN, du DNS, du chiffrement et des capacités du client.

Une bonne analyse distingue donc :

1. le débit PHY négocié;
2. la qualité radio et la stabilité de la liaison;
3. le temps d’antenne consommé;
4. le débit utile mesuré par application;
5. l’expérience utilisateur (latence, gigue, pertes, coupures).


## 2. La couche MAC : comment plusieurs appareils partagent le canal

### 2.1 CSMA/CA, écoute du canal et backoff

Le Wi-Fi ne peut pas supposer qu’une station détectera toujours une collision pendant qu’elle émet. Le mécanisme historique d’accès distribué s’appuie donc sur l’évitement des collisions (*Carrier Sense Multiple Access with Collision Avoidance*, CSMA/CA). Une station vérifie si le canal semble libre, attend une durée inter-trame adaptée, puis utilise un compteur de backoff aléatoire. Si le canal devient occupé, le compteur est généralement gelé et reprend lorsqu’il redevient disponible, suivant les règles du mécanisme MAC utilisé.

Après une transmission unicast, un accusé de réception (ACK) peut confirmer la réception correcte de la trame. Si l’émetteur ne reçoit pas l’ACK attendu, il peut réessayer et adapter sa fenêtre de contention. Les retransmissions contribuent à la fiabilité, mais leur coût est une consommation d’air supplémentaire et une augmentation de latence.

<div class="wifi-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 350" width="100%" role="img" aria-label="Accès au médium Wi-Fi par CSMA/CA avec attente, backoff, données et ACK">
<defs><marker id="w2arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#55d6be"/></marker><style>@keyframes w2flow{to{stroke-dashoffset:-24}}.w2flow{stroke-dasharray:8 7;animation:w2flow 1.8s linear infinite}@media(prefers-reduced-motion:reduce){.w2flow{animation:none}}</style></defs>
<rect x="18" y="18" width="864" height="314" rx="18" fill="#0b1220" stroke="#27364b"/><text x="450" y="48" fill="#f1f5f9" font-size="20" font-weight="700" text-anchor="middle">CSMA/CA : l’émetteur évite les collisions</text>
<text x="52" y="91" fill="#cbd5e1" font-size="13">Canal</text><path d="M52 111 H842" stroke="#475569" stroke-width="2"/>
<rect x="80" y="92" width="130" height="38" rx="6" fill="#153b38" stroke="#55d6be"/><text x="145" y="116" fill="#ccfbf1" font-size="13" text-anchor="middle">Canal libre</text>
<rect x="216" y="92" width="130" height="38" rx="6" fill="#31244a" stroke="#c4b5fd"/><text x="281" y="116" fill="#ede9fe" font-size="13" text-anchor="middle">DIFS / AIFS</text>
<rect x="352" y="92" width="145" height="38" rx="6" fill="#3b2d19" stroke="#fbbf24"/><text x="424" y="116" fill="#fef3c7" font-size="13" text-anchor="middle">Backoff aléatoire</text>
<rect x="503" y="92" width="170" height="38" rx="6" fill="#122b44" stroke="#60a5fa"/><text x="588" y="116" fill="#dbeafe" font-size="13" text-anchor="middle">Trame DATA</text>
<rect x="679" y="92" width="125" height="38" rx="6" fill="#153b38" stroke="#55d6be"/><text x="741" y="116" fill="#ccfbf1" font-size="13" text-anchor="middle">SIFS + ACK</text>
<path class="w2flow" d="M80 145 H800" fill="none" stroke="#55d6be" stroke-width="2.5" marker-end="url(#w2arrow)"/>
<text x="450" y="183" fill="#cbd5e1" font-size="13" text-anchor="middle">Si le canal devient occupé, le compte à rebours est gelé puis reprend lorsque le canal est de nouveau disponible.</text>
<rect x="70" y="213" width="355" height="80" rx="10" fill="#101d2e" stroke="#60a5fa"/><text x="247" y="238" fill="#dbeafe" font-size="14" font-weight="700" text-anchor="middle">Réussite</text><text x="247" y="260" fill="#cbd5e1" font-size="12" text-anchor="middle">DATA reçue + ACK : transmission confirmée</text><text x="247" y="278" fill="#94a3b8" font-size="11" text-anchor="middle">ACK absent ≠ preuve unique d’interférence</text>
<rect x="475" y="213" width="355" height="80" rx="10" fill="#301d25" stroke="#fb7185"/><text x="652" y="238" fill="#ffe4e6" font-size="14" font-weight="700" text-anchor="middle">Échec / nouvel essai</text><text x="652" y="260" fill="#fecdd3" font-size="12" text-anchor="middle">Backoff élargi, retry, puis abandon si limite atteinte</text><text x="652" y="278" fill="#fda4af" font-size="11" text-anchor="middle">Augmente le temps d’antenne et réduit le débit utile</text>
</svg></div>

**Exemple.** Dans une salle de formation, 35 appareils partagent le même canal 5 GHz. Même si chaque appareil ne transfère que de petits volumes, ils doivent attendre leur tour. Si certains clients ont un débit PHY beaucoup plus faible, ils peuvent garder le canal occupé plus longtemps pour transférer les mêmes quantités de données. Ce phénomène explique pourquoi l’ajout de clients lents ou éloignés peut dégrader l’expérience des autres utilisateurs.

### 2.2 DIFS/AIFS, SIFS et différenciation de trafic

Les espaces inter-trames contrôlent l’ordre d’accès au médium. Les mécanismes EDCA associés à la qualité de service 802.11e emploient des catégories d’accès avec des paramètres de contention différents. La voix peut bénéficier d’une catégorie d’accès plus prioritaire que le trafic de fond, mais cela ne crée pas de capacité radio supplémentaire. Une priorité mal conçue peut faire attendre plus longtemps d’autres classes et ne peut pas corriger une couverture insuffisante ou une interférence sévère.

- **SIFS** : intervalle court utilisé pour des réponses immédiates comme ACK, CTS ou certaines transmissions de réponse.
- **DIFS** : durée d’attente employée par l’accès distribué classique avant de lancer le backoff.
- **AIFS** : durée inter-trame arbitraire, utilisée avec EDCA et dépendante de la catégorie d’accès.
- **CW / contention window** : plage dans laquelle est choisi le backoff aléatoire.

Les détails exacts varient selon la génération 802.11, les mécanismes MAC activés et l’implémentation. L’essentiel en dépannage est de comprendre qu’une saturation et de multiples retransmissions rendent les files d’attente plus longues et l’accès au canal moins prévisible.

### 2.3 Nœud caché et RTS/CTS

Deux clients peuvent chacun entendre un AP mais ne pas s’entendre mutuellement. Si les deux transmettent vers cet AP en pensant que le canal est libre, les transmissions peuvent se heurter au niveau du récepteur. Ce problème est appelé **nœud caché**. RTS/CTS peut réduire certaines collisions en réservant le médium avant l’envoi de données, mais ajoute des trames de contrôle. Ce mécanisme n’est pas une solution universelle : il peut aider dans des situations spécifiques tout en diminuant le débit disponible si activé sans diagnostic.

Le problème dit de **nœud exposé** est l’inverse conceptuel : une station retarde sa transmission parce qu’elle entend une activité proche, même si sa transmission vers un autre récepteur aurait pu être sans conflit. Les mécanismes modernes de réutilisation spatiale peuvent améliorer certains scénarios, mais leur effet dépend de la topologie radio et des capacités des appareils.

### 2.4 802.11ax : efficacité dans les réseaux denses

Wi-Fi 6 correspond à IEEE 802.11ax. Parmi ses mécanismes figurent :

- **OFDMA** : partage d’une ressource de fréquence en unités de ressources afin de desservir plusieurs stations dans une transmission planifiée, notamment utile pour des échanges de petite taille et multi-utilisateurs;
- **MU-MIMO** : utilisation de plusieurs flux spatiaux afin de communiquer avec plusieurs clients dans des conditions matérielles et radio appropriées;
- **BSS Coloring** : étiquette permettant aux appareils compatibles d’identifier certaines transmissions d’un BSS différent et d’évaluer des possibilités de réutilisation spatiale;
- **TWT (Target Wake Time)** : mécanisme de planification des réveils qui peut réduire la consommation d’énergie et la contention pour certains appareils.

Ces fonctions ne sont utiles que si les clients, les AP, le contrôleur et les paramètres prennent en charge le scénario. Elles ne suppriment pas les limites de propagation, le bruit ou la concurrence entre appareils anciens et récents. Voir les ressources de Cisco sur [Wi-Fi 6](https://blogs.cisco.com/networking/wi-fi-6-powers-real-world-enterprise-applications) et [BSS Coloring](https://www.cisco.com/c/en/us/td/docs/wireless/controller/9800/26-1/configuration-guide/wl-26-1-cg/bss-coloring/bss-coloring-overview.html).


## 3. Bandes, canaux et largeur de canal

### 3.1 2,4 GHz, 5 GHz et 6 GHz

<div class="wifi-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 390" width="100%" role="img" aria-label="Comparaison conceptuelle des bandes 2,4 GHz, 5 GHz et 6 GHz et des largeurs de canal">
<defs><marker id="w3arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#55d6be"/></marker><style>@keyframes w3flow{to{stroke-dashoffset:-24}}.w3flow{stroke-dasharray:8 7;animation:w3flow 1.8s linear infinite}@media(prefers-reduced-motion:reduce){.w3flow{animation:none}}</style></defs>
<rect x="18" y="18" width="864" height="354" rx="18" fill="#0b1220" stroke="#27364b"/><text x="450" y="48" fill="#f1f5f9" font-size="20" font-weight="700" text-anchor="middle">Bandes radio : compromis entre portée, largeur et congestion</text>
<text x="58" y="96" fill="#dbeafe" font-size="15" font-weight="700">2,4 GHz</text><rect x="190" y="77" width="635" height="32" rx="6" fill="#122b44" stroke="#60a5fa"/><rect x="215" y="77" width="115" height="32" rx="4" fill="#1d4ed8"/><rect x="375" y="77" width="115" height="32" rx="4" fill="#1d4ed8"/><rect x="535" y="77" width="115" height="32" rx="4" fill="#1d4ed8"/><text x="272" y="98" fill="#eff6ff" font-size="12" text-anchor="middle">1</text><text x="432" y="98" fill="#eff6ff" font-size="12" text-anchor="middle">6</text><text x="592" y="98" fill="#eff6ff" font-size="12" text-anchor="middle">11</text><text x="730" y="98" fill="#bfdbfe" font-size="11" text-anchor="middle">Exemple courant, selon région</text>
<text x="58" y="154" fill="#d1fae5" font-size="15" font-weight="700">5 GHz</text><rect x="190" y="135" width="635" height="32" rx="6" fill="#12352f" stroke="#55d6be"/><rect x="210" y="135" width="110" height="32" rx="4" fill="#0f766e"/><rect x="330" y="135" width="110" height="32" rx="4" fill="#0f766e"/><rect x="450" y="135" width="110" height="32" rx="4" fill="#0f766e"/><rect x="570" y="135" width="110" height="32" rx="4" fill="#0f766e"/><rect x="690" y="135" width="110" height="32" rx="4" fill="#0f766e"/><text x="505" y="156" fill="#ccfbf1" font-size="12" text-anchor="middle">Canaux et DFS selon domaine réglementaire</text>
<text x="58" y="212" fill="#ede9fe" font-size="15" font-weight="700">6 GHz</text><rect x="190" y="193" width="635" height="32" rx="6" fill="#31244a" stroke="#c4b5fd"/><path class="w3flow" d="M210 209 H800" stroke="#c4b5fd" stroke-width="3" fill="none" marker-end="url(#w3arrow)"/><text x="508" y="214" fill="#f5f3ff" font-size="12" text-anchor="middle">Plus de spectre dans les pays qui l’autorisent</text>
<text x="450" y="260" fill="#cbd5e1" font-size="13" text-anchor="middle">Une largeur plus importante n’est pas automatiquement meilleure : elle consomme davantage de spectre contigu.</text>
<rect x="72" y="282" width="230" height="58" rx="9" fill="#122b44" stroke="#60a5fa"/><text x="187" y="306" fill="#dbeafe" font-size="13" font-weight="700" text-anchor="middle">20 MHz</text><text x="187" y="325" fill="#93c5fd" font-size="11" text-anchor="middle">Plus de réutilisation possible</text>
<rect x="335" y="282" width="230" height="58" rx="9" fill="#12352f" stroke="#55d6be"/><text x="450" y="306" fill="#d1fae5" font-size="13" font-weight="700" text-anchor="middle">40 / 80 MHz</text><text x="450" y="325" fill="#99f6e4" font-size="11" text-anchor="middle">Compromis selon densité</text>
<rect x="598" y="282" width="230" height="58" rx="9" fill="#3b2d19" stroke="#fbbf24"/><text x="713" y="306" fill="#fef3c7" font-size="13" font-weight="700" text-anchor="middle">160 / 320 MHz</text><text x="713" y="325" fill="#fcd34d" font-size="11" text-anchor="middle">Besoin de spectre et clients compatibles</text>
</svg></div>

Les bandes n’offrent pas le même compromis :

| Bande | Caractéristiques générales | Points d’attention |
|---|---|---|
| 2,4 GHz | Propagation souvent favorable à travers certains obstacles; compatibilité avec de nombreux appareils IoT | Spectre limité, davantage de réseaux voisins et d’interférences possibles; les canaux se chevauchent facilement si la planification est mauvaise |
| 5 GHz | Davantage de possibilités de canaux que 2,4 GHz dans de nombreuses régions; support étendu dans les réseaux d’entreprise | Portée utile dépendante de la puissance, des obstacles et du canal; certains canaux sont soumis à DFS |
| 6 GHz | Spectre additionnel disponible là où le régulateur l’autorise; utile pour des clients récents et des canaux plus larges | Compatibilité client/AP, conditions réglementaires, puissances autorisées, exigences de sécurité et atténuation radio à considérer |

**Ne configure pas une fréquence ou un canal seulement parce qu’il apparaît dans un tableau trouvé en ligne.** Les canaux utilisables, la puissance, le DFS, l’utilisation en intérieur/extérieur et la disponibilité de la bande 6 GHz varient d’un domaine réglementaire à l’autre. Le contrôleur peut adapter la liste en fonction du pays configuré et du modèle d’AP.

### 3.2 Canaux qui se chevauchent

En 2,4 GHz, les canaux sont très rapprochés. Dans de nombreux déploiements qui utilisent les canaux de 20 MHz, le plan classique emploie les canaux 1, 6 et 11; le choix définitif dépend cependant du domaine réglementaire et du plan RF local. Configurer des canaux partiellement chevauchants peut augmenter les interférences adjacentes et compliquer l’accès au médium. Choisir trois canaux « différents » dans l’interface ne signifie pas qu’ils sont suffisamment séparés spectralement.

Sur 5 GHz et 6 GHz, un plan de fréquences propose souvent davantage de canaux et permet une meilleure réutilisation, mais il doit prendre en compte les largeurs autorisées, la disponibilité DFS, la puissance et les clients réellement pris en charge. Les points d’accès adjacents n’ont pas systématiquement intérêt à utiliser le canal le plus large disponible.

### 3.3 20, 40, 80, 160 et 320 MHz : le compromis

Élargir un canal augmente les ressources de fréquence mobilisées par une transmission et peut accroître le débit maximal PHY lorsque signal, modulation et capacités du matériel le permettent. Mais plus le canal est large, moins il est possible de réutiliser des canaux indépendants dans un spectre donné. En environnement dense, des canaux de 20 ou 40 MHz peuvent offrir plus de canaux réutilisables et de meilleures performances globales que 80 ou 160 MHz.

La largeur de **320 MHz** est associée à certaines capacités Wi-Fi 7 / 802.11be dans des bandes où cela est autorisé et pris en charge; elle n’est pas un réglage générique à imposer aux réseaux existants. Wi-Fi 7 introduit notamment Multi-Link Operation (MLO), qui permet à des équipements compatibles de gérer des liens multiples selon les modes supportés. Ces fonctions ne garantissent pas des gains identiques sur tous les clients et tous les types de trafic.

**Méthode de choix :** commencer par le besoin applicatif et la densité, inspecter l’environnement RF, vérifier les capacités des clients, faire un test pilote, puis comparer débit utile, latence et retransmissions avant/après. Éviter de changer simultanément la largeur, la puissance, le canal et les paramètres de roaming, car cela rend l’effet de chaque modification difficile à isoler.

### 3.4 DFS et changements de canal

Dans certains canaux 5 GHz, l’équipement doit détecter certains signaux radar et quitter un canal lorsque les règles l’exigent. C’est le mécanisme DFS (*Dynamic Frequency Selection*). Le temps de vérification et les changements de canal peuvent expliquer une interruption brève ou un changement d’état radio. Le client peut alors rescanner et réassocier, selon les circonstances. Avant de désactiver ou d’éviter des canaux DFS, vérifier la réglementation, l’environnement et les recommandations du constructeur; un problème ne doit pas être attribué au DFS sans journaux ou mesures concordants.

### 3.5 Puissance de transmission et asymétrie de liaison

Augmenter la puissance de l’AP ne garantit pas une meilleure connexion. Le client transmet souvent à une puissance plus faible que l’AP; il peut donc recevoir le signal du point d’accès tout en étant incapable de lui renvoyer ses propres trames avec une qualité suffisante. Cette situation peut créer une cellule apparente plus large mais pas une liaison bidirectionnelle fiable. Un plan radio doit être étudié à la fois pour la réception par le client et pour celle des trames émises par le client au niveau de l’AP.

L’emplacement des AP, le type d’antenne, l’orientation, les matériaux, la hauteur, les personnes et les obstacles influencent la propagation. Une planification professionnelle combine l’étude de site, le prédictif quand il est adapté, puis des mesures après installation. Un RSSI brut doit être interprété avec le SNR, la qualité des trames, le débit de données et le comportement applicatif.


## 4. Évaluer la qualité radio et la capacité

### 4.1 RSSI et SNR ne racontent pas la même chose

RSSI exprime la puissance reçue estimée. Les valeurs sont souvent affichées en dBm; une valeur plus proche de zéro signifie généralement un signal plus fort. Comme la calibration varie selon les appareils, comparer des valeurs absolues de constructeurs différents demande de la prudence.

Le SNR compare la puissance du signal au bruit. Un signal à −55 dBm dans un environnement peu bruyant peut fonctionner nettement mieux qu’un signal à −48 dBm dominé par des interférences ou un bruit élevé. Il ne faut pas utiliser une valeur seuil unique comme garantie universelle : les besoins varient selon les débits de modulation, les applications, le nombre de flux et le contexte. À titre de méthode, comparer les mesures au moment de l’incident avec une zone de référence saine et avec les objectifs définis pour l’application.

### 4.2 Interférence co-canal, inter-canal et non-Wi-Fi

- **Co-canal (CCI)** : des BSS différents utilisent le même canal et doivent partager le médium; la conséquence peut être une augmentation de l’attente et une réduction du temps disponible.
- **Canaux adjacents (ACI)** : transmissions sur des fréquences partiellement chevauchantes peuvent perturber la réception et accroître les erreurs.
- **Interférence non-Wi-Fi** : d’autres sources radioélectriques peuvent occuper ou perturber le spectre sans être décodées comme des trames 802.11.
- **Bruit de fond** : l’énergie ambiante mesurée peut limiter la réception même en présence d’un RSSI correct.

Un scanner de canaux ou la liste des SSID ne suffit pas toujours à identifier une source non-Wi-Fi. Pour les cas complexes, utiliser un outil d’analyse de spectre adapté et corréler les mesures avec l’heure, la zone et le symptôme.

### 4.3 Airtime et débit utile

La capacité d’un canal radio partagé n’est pas simplement la somme des débits annoncés de tous les clients. Les stations consomment de l’air pour transmettre les données et les trames de gestion/contrôle; le canal peut être inactif pendant des attentes, et les retransmissions consomment davantage de temps. Les clients à faible débit prennent parfois beaucoup plus d’air pour des données identiques. En environnement dense, la charge, les retries, l’occupation du canal et la distribution des clients sont donc des indicateurs de capacité essentiels.

Exemple simplifié : un flux utile de 10 Mo transféré à un débit effectif de 10 Mbit/s consomme environ 8 secondes de transmission utile; à 2 Mbit/s, le même volume prend environ 40 secondes, sans même tenir compte des en-têtes, confirmations, contention et retransmissions. Plusieurs clients lents peuvent ainsi occuper une part disproportionnée du temps d’antenne. Ce calcul illustre le phénomène, mais ne remplace pas les mesures de l’équipement.

### 4.4 MCS, spatial streams et agrégation

Le débit PHY dépend entre autres de la modulation et du codage (MCS), de la largeur de canal, du nombre de flux spatiaux, des capacités du client/AP et des conditions radio. Un appareil 2x2 ne reçoit pas automatiquement un débit 4x4 simplement parce que l’AP possède quatre chaînes radio. Des techniques comme l’agrégation de trames (A-MPDU et A-MSDU) réduisent certains coûts fixes pour des flux appropriés. Les détails de négociation peuvent être observés dans les statistiques du contrôleur, les journaux du client ou une capture compatible.

Une baisse du débit PHY peut être une réaction normale à une variation de signal; elle devient un problème si elle s’accompagne de retries, d’une latence excessive ou d’un débit utile insuffisant. À l’inverse, un débit PHY élevé n’empêche pas la congestion du canal ou la lenteur d’un service distant.


## 5. Association, authentification et sécurité

### 5.1 Trames 802.11 : gestion, contrôle et données

L’analyse des échanges Wi-Fi utilise souvent trois grandes catégories de trames :

- **Gestion** : beacon, probe request/response, authentication, association/reassociation, désassociation et dé-authentification.
- **Contrôle** : ACK, RTS, CTS et autres trames de contrôle qui facilitent l’accès ou confirment des échanges.
- **Données** : transport des données de l’utilisateur, avec des en-têtes dont l’interprétation dépend du type de trame et du sens entre station, AP et distribution system.

Une capture effectuée en mode normal peut ne présenter que le trafic vu par l’interface connectée, avec un encapsulage de couche liaison qui n’est pas un en-tête radio brut. Pour observer les trames de gestion et les échanges d’autres stations, il faut souvent un adaptateur/driver compatible et le mode monitor. Le support varie selon le système et le matériel; voir la [FAQ officielle Wireshark sur la capture 802.11](https://www.wireshark.org/download/docs/faq.html).

### 5.2 WPA2-Personal, WPA2-Enterprise et WPA3

**WPA2-Personal** utilise une clé partagée (PSK) ou un mécanisme dérivé du mot de passe pour rejoindre le WLAN. Le partage d’un même secret entre tous les utilisateurs rend la rotation, la révocation individuelle et l’audit plus difficiles dans un environnement professionnel.

**WPA2-Enterprise** s’appuie généralement sur 802.1X/EAP et un serveur d’authentification comme RADIUS. La méthode EAP choisie, la validation des certificats par le client et la configuration des serveurs doivent être cohérentes. L’utilisateur ne doit pas accepter aveuglément un certificat de serveur inconnu : une validation incorrecte peut exposer les identifiants à un serveur frauduleux.

**WPA3-Personal** emploie SAE (Simultaneous Authentication of Equals) pour améliorer la protection de l’authentification fondée sur un mot de passe par rapport au modèle PSK traditionnel, sous réserve des capacités et du mode de fonctionnement négociés. **WPA3-Enterprise** apporte les mécanismes de sécurité attendus dans les déploiements entreprise selon le profil utilisé. Les détails dépendent de la certification, du profil, des options de transition et des capacités des terminaux.

**OWE / Enhanced Open** peut chiffrer le lien radio d’un réseau ouvert compatible sans fournir l’authentification forte d’un réseau d’entreprise. Il faut distinguer confidentialité du lien, authentification de l’identité et autorisation d’accès : ce sont des propriétés différentes.

La bande 6 GHz, lorsque disponible, impose des exigences de sécurité propres aux règles et certifications applicables; on ne doit pas la considérer comme un prolongement transparent de n’importe quel WLAN ancien. Vérifier le support du client, le mode WPA attendu, le profil de sécurité et le domaine réglementaire dans la documentation des équipements concernés.

### 5.3 802.1X, EAP, RADIUS et autorisation

<div class="wifi-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" width="100%" role="img" aria-label="Flux d’authentification Wi-Fi entreprise par 802.1X EAP et serveur RADIUS">
<defs><marker id="w4arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#55d6be"/></marker><marker id="w4gold" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#fbbf24"/></marker><style>@keyframes w4flow{to{stroke-dashoffset:-24}}.w4flow{stroke-dasharray:8 7;animation:w4flow 1.8s linear infinite}@media(prefers-reduced-motion:reduce){.w4flow{animation:none}}</style></defs>
<rect x="18" y="18" width="864" height="324" rx="18" fill="#0b1220" stroke="#27364b"/><text x="450" y="48" fill="#f1f5f9" font-size="20" font-weight="700" text-anchor="middle">WLAN d’entreprise : rôles EAP / authenticator / RADIUS</text>
<rect x="48" y="95" width="190" height="85" rx="12" fill="#122b44" stroke="#60a5fa" stroke-width="2"/><text x="143" y="124" fill="#dbeafe" font-size="15" font-weight="700" text-anchor="middle">Client / supplicant</text><text x="143" y="147" fill="#93c5fd" font-size="12" text-anchor="middle">identité + méthode EAP</text>
<rect x="355" y="95" width="190" height="85" rx="12" fill="#12352f" stroke="#55d6be" stroke-width="2"/><text x="450" y="124" fill="#d1fae5" font-size="15" font-weight="700" text-anchor="middle">Point d’accès</text><text x="450" y="147" fill="#99f6e4" font-size="12" text-anchor="middle">authenticator 802.1X</text>
<rect x="662" y="95" width="190" height="85" rx="12" fill="#31244a" stroke="#c4b5fd" stroke-width="2"/><text x="757" y="124" fill="#ede9fe" font-size="15" font-weight="700" text-anchor="middle">Serveur RADIUS</text><text x="757" y="147" fill="#c4b5fd" font-size="12" text-anchor="middle">politiques / identité</text>
<path class="w4flow" d="M238 120 H349" fill="none" stroke="#55d6be" stroke-width="3" marker-end="url(#w4arrow)"/><path class="w4flow" d="M349 157 H244" fill="none" stroke="#55d6be" stroke-width="2.5" marker-end="url(#w4arrow)"/><text x="293" y="108" fill="#99f6e4" font-size="11" text-anchor="middle">EAPOL →</text><text x="293" y="174" fill="#99f6e4" font-size="11" text-anchor="middle">← EAPOL</text>
<path class="w4flow" d="M545 145 H656" fill="none" stroke="#c4b5fd" stroke-width="3" marker-end="url(#w4arrow)"/><text x="600" y="133" fill="#c4b5fd" font-size="11" text-anchor="middle">RADIUS / EAP</text>
<path class="w4flow" d="M656 166 H545" fill="none" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#w4gold)"/><text x="600" y="194" fill="#fcd34d" font-size="11" text-anchor="middle">Accept / Reject</text>
<rect x="82" y="229" width="736" height="76" rx="11" fill="#101d2e" stroke="#475569"/><text x="450" y="252" fill="#f1f5f9" font-size="14" font-weight="700" text-anchor="middle">Après réussite de l’authentification</text><text x="450" y="274" fill="#cbd5e1" font-size="12" text-anchor="middle">Établissement des clés, autorisation / VLAN selon politique, puis DHCP et accès IP</text><text x="450" y="291" fill="#fbbf24" font-size="11" text-anchor="middle">Le succès RADIUS ne prouve pas que le VLAN, DHCP, DNS ou routage sont corrects.</text>
</svg></div>

Dans un WLAN d’entreprise, le client (*supplicant*) et le point d’accès (*authenticator*) échangent des messages EAP encapsulés en EAPOL sur le segment radio; l’AP ou le contrôleur échange généralement avec le serveur RADIUS sur le réseau de distribution. Selon l’architecture, RADIUS peut retourner une acceptation, un refus ou des attributs de politique, par exemple un VLAN dynamique. Le client établit ensuite les clés nécessaires au chiffrement du trafic après le déroulement approprié du protocole.

Lorsque la connexion échoue, lire les journaux par étapes :

1. le client détecte-t-il le SSID et les paramètres de sécurité?
2. commence-t-il l’authentification?
3. le serveur RADIUS reçoit-il la demande?
4. le serveur retourne-t-il Accept ou Reject, et pourquoi?
5. les échanges de clés réussissent-ils?
6. l’équipement applique-t-il la bonne politique/VLAN?
7. le client reçoit-il une configuration IP correcte?

Un `Access-Accept` ne valide pas DHCP, DNS, routage ou l’application. De même, un `Access-Reject` n’est pas automatiquement synonyme de mauvais mot de passe : certificat expiré, méthode EAP incompatible, identité inattendue, politique d’accès ou disponibilité RADIUS doivent être examinés.

### 5.4 PMF / 802.11w et hygiène de sécurité

Protected Management Frames (PMF), introduit par 802.11w et intégré aux profils de sécurité modernes, protège certaines trames de gestion robustes contre la falsification après établissement de la sécurité appropriée. Son statut obligatoire ou facultatif dépend du profil utilisé. Les fonctions de protection de trames ne remplacent pas une authentification forte et une segmentation adéquate.

Mesures de base en entreprise : séparer les réseaux employés, invités et IoT; appliquer le moindre privilège aux VLAN/ACL; utiliser une authentification individuelle lorsqu’elle est appropriée; valider les certificats EAP; éliminer les mots de passe partagés non maîtrisés; journaliser les échecs d’authentification; maintenir firmware et contrôleurs; réviser périodiquement les comptes, certificats et secrets. Un portail captif ne doit pas être confondu avec le chiffrement radio ou un contrôle d’accès réseau complet.


## 6. Itinérance entre points d’accès

### 6.1 Pourquoi un terminal « colle » à un AP éloigné

Dans la plupart des réseaux Wi-Fi, le client décide à quel moment chercher un autre AP et quand se réassocier. L’infrastructure peut lui fournir de l’information ou des recommandations, mais elle ne peut pas obliger tous les terminaux à se comporter de la même façon. Les appareils appliquent des algorithmes différents, et des facteurs comme la batterie, le pilote, la puissance reçue, la qualité des transmissions et la politique système influencent la décision.

Un SSID identique ne suffit pas à garantir un roaming fluide. Les AP doivent proposer une sécurité compatible, des paramètres cohérents, une connectivité réseau et des politiques de mobilité adaptées. Si le changement d’AP conduit à un autre VLAN sans mécanisme prévu, l’adresse IP ou les sessions peuvent être perturbées. Si la couverture se chevauche trop peu, le client peut perdre la liaison avant de trouver un candidat convenable; si les cellules se chevauchent excessivement avec une puissance trop élevée, il peut rester associé trop longtemps au mauvais AP ou les canaux peuvent être très occupés.

### 6.2 802.11k, 802.11v et 802.11r

<div class="wifi-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 365" width="100%" role="img" aria-label="Itinérance Wi-Fi d’un client entre deux points d’accès avec aides 802.11k v et r">
<defs><marker id="w5arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#55d6be"/></marker><style>@keyframes w5flow{to{stroke-dashoffset:-24}}.w5flow{stroke-dasharray:8 7;animation:w5flow 1.8s linear infinite}@media(prefers-reduced-motion:reduce){.w5flow{animation:none}}</style></defs>
<rect x="18" y="18" width="864" height="329" rx="18" fill="#0b1220" stroke="#27364b"/><text x="450" y="48" fill="#f1f5f9" font-size="20" font-weight="700" text-anchor="middle">Roaming : le client décide, l’infrastructure peut l’aider</text>
<rect x="55" y="108" width="190" height="90" rx="12" fill="#122b44" stroke="#60a5fa" stroke-width="2"/><text x="150" y="139" fill="#dbeafe" font-size="15" font-weight="700" text-anchor="middle">AP-1 / BSSID A</text><text x="150" y="161" fill="#93c5fd" font-size="12" text-anchor="middle">Association actuelle</text>
<rect x="655" y="108" width="190" height="90" rx="12" fill="#12352f" stroke="#55d6be" stroke-width="2"/><text x="750" y="139" fill="#d1fae5" font-size="15" font-weight="700" text-anchor="middle">AP-2 / BSSID B</text><text x="750" y="161" fill="#99f6e4" font-size="12" text-anchor="middle">Cible possible</text>
<rect x="356" y="105" width="188" height="96" rx="12" fill="#31244a" stroke="#c4b5fd" stroke-width="2"/><text x="450" y="133" fill="#ede9fe" font-size="15" font-weight="700" text-anchor="middle">Client mobile</text><text x="450" y="155" fill="#c4b5fd" font-size="12" text-anchor="middle">RSSI / SNR / charge</text><text x="450" y="174" fill="#c4b5fd" font-size="12" text-anchor="middle">décision de roam</text>
<path class="w5flow" d="M245 150 H350" fill="none" stroke="#60a5fa" stroke-width="3" marker-end="url(#w5arrow)"/><path class="w5flow" d="M550 150 H649" fill="none" stroke="#55d6be" stroke-width="3" marker-end="url(#w5arrow)"/>
<text x="450" y="230" fill="#cbd5e1" font-size="13" text-anchor="middle">802.11k : rapport de voisins · 802.11v : recommandation de transition · 802.11r : transition sécurisée rapide</text>
<rect x="70" y="253" width="232" height="60" rx="9" fill="#101d2e" stroke="#60a5fa"/><text x="186" y="276" fill="#dbeafe" font-size="13" font-weight="700" text-anchor="middle">Préparation</text><text x="186" y="295" fill="#93c5fd" font-size="11" text-anchor="middle">mesurer et proposer des voisins</text>
<rect x="334" y="253" width="232" height="60" rx="9" fill="#101d2e" stroke="#c4b5fd"/><text x="450" y="276" fill="#ede9fe" font-size="13" font-weight="700" text-anchor="middle">Transition</text><text x="450" y="295" fill="#c4b5fd" font-size="11" text-anchor="middle">réassociation / échange de clés</text>
<rect x="598" y="253" width="232" height="60" rx="9" fill="#101d2e" stroke="#55d6be"/><text x="714" y="276" fill="#d1fae5" font-size="13" font-weight="700" text-anchor="middle">Validation</text><text x="714" y="295" fill="#99f6e4" font-size="11" text-anchor="middle">IP, latence et application stables</text>
</svg></div>

- **802.11k — Radio Resource Measurement** : fournit notamment un rapport de voisins afin d’aider le client à identifier plus rapidement des AP candidats. Il réduit potentiellement le travail de scan, sans choisir le nouveau point d’accès à la place du client.
- **802.11v — BSS Transition Management** : permet à l’infrastructure d’envoyer des recommandations de transition et offre d’autres mécanismes de gestion. Une recommandation ne signifie pas que tous les clients l’accepteront.
- **802.11r — Fast BSS Transition** : accélère certains échanges de transition de sécurité afin de réduire la latence du roaming dans les environnements compatibles.

Il faut tester la compatibilité des équipements réels. Des options 802.11r mal adaptées à un parc mixte ou à certains objets anciens peuvent empêcher des clients de se connecter. Les stratégies de déploiement progressif et les tests par modèle de terminal sont plus sûrs qu’une activation aveugle. Cisco explique les différences et les conditions d’activation dans son guide [802.11r/k/v Fast Roams](https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/221671-understand-802-11r-11k-11v-fast-roams-on.html).

### 6.3 Mesurer le roaming comme une application

Pour une application temps réel, vérifier la durée pendant laquelle les paquets ne passent plus, la variation de latence, les pertes et le comportement de la session applicative. Il est utile de corréler les horodatages client/AP/contrôleur, l’identité du client, l’ancien et le nouveau BSSID, le canal, l’état de sécurité et les journaux DHCP si le changement d’architecture réseau l’exige.

Ne conclure pas à une « mauvaise itinérance » à partir d’un seul RSSI. La transition peut échouer à cause d’une authentification complète trop lente, d’une politique VLAN incohérente, d’une couverture faible, d’un client qui retarde le roam, d’une surcharge radio ou d’un problème de chemin filaire.


## 7. Concevoir et exploiter un WLAN fiable

### 7.1 SSID, radios et segmentation

Créer un SSID séparé pour chaque équipe n’est pas systématiquement une bonne pratique. Chaque SSID implique des éléments de gestion, des annonces et des interactions supplémentaires; un nombre excessif de SSID peut réduire l’efficacité dans des environnements denses. Préférer le nombre de WLAN nécessaire aux politiques de sécurité et aux besoins opérationnels, puis réaliser la segmentation avec des VLAN, ACL, rôles ou mécanismes de politique pris en charge.

Un schéma courant distingue :

- `Staff` : authentification d’entreprise, accès aux outils métier selon les rôles;
- `Guest` : accès Internet filtré, isolation des clients et durée de session adaptée;
- `IoT` : inventaire contrôlé des terminaux, accès limité aux seuls services nécessaires;
- `Management` : plan de gestion des AP/contrôleurs, non accessible depuis le WLAN utilisateur ordinaire.

Les noms sont des exemples. Il faut vérifier que les SSID ne partagent pas accidentellement une politique trop permissive, un secret identique ou un accès direct aux plans de gestion.

### 7.2 Topologie : AP, LAN, contrôleur et services IP

<div class="wifi-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 370" width="100%" role="img" aria-label="Architecture WLAN avec client, point d’accès, réseau de distribution, contrôleur, VLAN et services IP">
<defs><marker id="w7arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#55d6be"/></marker><style>@keyframes w7flow{to{stroke-dashoffset:-24}}.w7flow{stroke-dasharray:8 7;animation:w7flow 1.8s linear infinite}@media(prefers-reduced-motion:reduce){.w7flow{animation:none}}</style></defs>
<rect x="18" y="18" width="864" height="334" rx="18" fill="#0b1220" stroke="#27364b"/><text x="450" y="48" fill="#f1f5f9" font-size="20" font-weight="700" text-anchor="middle">Du client Wi-Fi à l’application : parcours logique</text>
<rect x="45" y="108" width="145" height="70" rx="10" fill="#122b44" stroke="#60a5fa"/><text x="117" y="135" fill="#dbeafe" font-size="14" font-weight="700" text-anchor="middle">Client Wi-Fi</text><text x="117" y="155" fill="#93c5fd" font-size="11" text-anchor="middle">802.11 radio</text>
<rect x="245" y="108" width="145" height="70" rx="10" fill="#12352f" stroke="#55d6be"/><text x="317" y="135" fill="#d1fae5" font-size="14" font-weight="700" text-anchor="middle">Point d’accès</text><text x="317" y="155" fill="#99f6e4" font-size="11" text-anchor="middle">pont / tunnel selon mode</text>
<rect x="445" y="108" width="145" height="70" rx="10" fill="#31244a" stroke="#c4b5fd"/><text x="517" y="135" fill="#ede9fe" font-size="14" font-weight="700" text-anchor="middle">LAN / VLAN</text><text x="517" y="155" fill="#c4b5fd" font-size="11" text-anchor="middle">tagging / ACL</text>
<rect x="645" y="108" width="210" height="70" rx="10" fill="#3b2d19" stroke="#fbbf24"/><text x="750" y="135" fill="#fef3c7" font-size="14" font-weight="700" text-anchor="middle">Services réseau</text><text x="750" y="155" fill="#fcd34d" font-size="11" text-anchor="middle">DHCP · DNS · gateway · apps</text>
<path class="w7flow" d="M190 143 H239 M390 143 H439 M590 143 H639" fill="none" stroke="#55d6be" stroke-width="3" marker-end="url(#w7arrow)"/>
<rect x="275" y="218" width="350" height="65" rx="10" fill="#101d2e" stroke="#475569"/><text x="450" y="242" fill="#f1f5f9" font-size="14" font-weight="700" text-anchor="middle">Contrôleur WLAN (si architecture centralisée)</text><text x="450" y="261" fill="#cbd5e1" font-size="12" text-anchor="middle">gestion, politiques, mobilité et tunnel selon le modèle</text>
<path class="w7flow" d="M317 178 V199 H330 V212 M517 178 V199 H570 V212" fill="none" stroke="#c4b5fd" stroke-width="2.5" marker-end="url(#w7arrow)"/>
<text x="450" y="314" fill="#94a3b8" font-size="12" text-anchor="middle">Le contrôle WLAN et le chemin des données ne sont pas forcément le même trajet.</text><text x="450" y="333" fill="#fbbf24" font-size="11" text-anchor="middle">Le fonctionnement exact dépend du constructeur, du mode AP et du design de mobilité.</text>
</svg></div>

Le chemin exact varie selon l’architecture : certains AP pontent localement les trames dans le VLAN associé; d’autres encapsulent le trafic utilisateur vers un contrôleur ou une passerelle selon les modes de fonctionnement. Le plan de contrôle, la gestion et le trafic de données peuvent donc suivre des chemins distincts. Lorsqu’un WLAN se connecte mais que les applications échouent, vérifier le mode de transfert réel au lieu de supposer que tout passe par le contrôleur.

Sur le réseau filaire, contrôler les ports des AP, la négociation Ethernet, l’alimentation PoE, les VLAN autorisés, le VLAN natif lorsque pertinent, les ACL, le MTU pour les tunnels concernés, la reachability du contrôleur, la synchronisation de l’heure et les services de résolution. Un AP qui redémarre sous charge peut souffrir d’une alimentation insuffisante ou d’un défaut logiciel, pas forcément d’un problème RF.

### 7.3 Capacité : dimensionner par l’usage

Éviter de dimensionner uniquement à partir d’un nombre théorique maximum de clients par AP. Un appareil IoT qui envoie quelques petits messages n’impose pas le même besoin qu’un terminal de visioconférence ou un poste qui télécharge de gros fichiers. Le dimensionnement doit prendre en compte :

- simultanéité réelle des usages, pas seulement le nombre de comptes;
- exigences de débit, latence, gigue et disponibilité;
- bandes et générations prises en charge par les terminaux;
- obstacles et couverture requise dans toute la zone;
- temps d’antenne, charge de chaque radio et diversité de débits;
- port uplink de l’AP, budget PoE et capacité du commutateur;
- tolérance à la perte d’un AP ou d’un lien amont.

Après déploiement, comparer la conception aux mesures sur site. Une salle peut présenter une couverture correcte mais une capacité insuffisante lorsque tous les utilisateurs se connectent à la fois. Il faut alors examiner la réutilisation des canaux, les largeurs, la répartition des clients, les capacités des AP et le câblage, pas simplement augmenter la puissance.

### 7.4 QoS voix/vidéo

La QoS Wi-Fi s’appuie sur EDCA et des marquages de priorité, mais le marquage doit rester cohérent de l’application jusqu’au réseau filaire. Une application qui marque tout en priorité maximale finit par rendre la politique inutile. Valider la correspondance entre DSCP, catégories d’accès, politique contrôleur, commutateurs et éventuelles passerelles; observer aussi les pertes, la gigue, le temps d’antenne et les retransmissions. La priorité ne répare pas une couverture dégradée ou une radio saturée.


## 8. Méthode opérationnelle de dépannage

<div class="wifi-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" width="100%" role="img" aria-label="Arbre de diagnostic Wi-Fi séparant radio, authentification, DHCP et application">
<defs><marker id="w6arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#55d6be"/></marker><style>@keyframes w6flow{to{stroke-dashoffset:-24}}.w6flow{stroke-dasharray:8 7;animation:w6flow 1.8s linear infinite}@media(prefers-reduced-motion:reduce){.w6flow{animation:none}}</style></defs>
<rect x="18" y="18" width="864" height="384" rx="18" fill="#0b1220" stroke="#27364b"/><text x="450" y="48" fill="#f1f5f9" font-size="20" font-weight="700" text-anchor="middle">Dépannage par couches : localiser le premier échec</text>
<rect x="310" y="70" width="280" height="54" rx="10" fill="#31244a" stroke="#c4b5fd" stroke-width="2"/><text x="450" y="92" fill="#ede9fe" font-size="14" font-weight="700" text-anchor="middle">Symptôme reproduit ?</text><text x="450" y="109" fill="#c4b5fd" font-size="11" text-anchor="middle">client, heure, SSID, zone, application</text>
<path class="w6flow" d="M450 124 V151 H150 V172 M450 151 V172 M450 151 H750 V172" fill="none" stroke="#55d6be" stroke-width="2.5" marker-end="url(#w6arrow)"/>
<rect x="55" y="174" width="190" height="70" rx="10" fill="#122b44" stroke="#60a5fa"/><text x="150" y="199" fill="#dbeafe" font-size="14" font-weight="700" text-anchor="middle">Radio / 802.11</text><text x="150" y="218" fill="#93c5fd" font-size="11" text-anchor="middle">RSSI, SNR, retries, canal</text><text x="150" y="233" fill="#93c5fd" font-size="11" text-anchor="middle">association / roaming</text>
<rect x="355" y="174" width="190" height="70" rx="10" fill="#31244a" stroke="#c4b5fd"/><text x="450" y="199" fill="#ede9fe" font-size="14" font-weight="700" text-anchor="middle">Sécurité / identité</text><text x="450" y="218" fill="#c4b5fd" font-size="11" text-anchor="middle">PSK, EAP, RADIUS, clés</text><text x="450" y="233" fill="#c4b5fd" font-size="11" text-anchor="middle">policy / VLAN</text>
<rect x="655" y="174" width="190" height="70" rx="10" fill="#12352f" stroke="#55d6be"/><text x="750" y="199" fill="#d1fae5" font-size="14" font-weight="700" text-anchor="middle">Services IP</text><text x="750" y="218" fill="#99f6e4" font-size="11" text-anchor="middle">DHCP, passerelle, DNS</text><text x="750" y="233" fill="#99f6e4" font-size="11" text-anchor="middle">routage / pare-feu</text>
<path class="w6flow" d="M150 244 V276 H450 V300 M450 244 V300 M750 244 V276 H450" fill="none" stroke="#55d6be" stroke-width="2.5" marker-end="url(#w6arrow)"/>
<rect x="250" y="302" width="400" height="57" rx="10" fill="#3b2d19" stroke="#fbbf24"/><text x="450" y="325" fill="#fef3c7" font-size="14" font-weight="700" text-anchor="middle">Tester de bout en bout et corréler les preuves</text><text x="450" y="344" fill="#fcd34d" font-size="11" text-anchor="middle">un résultat positif à une couche ne valide pas la suivante</text>
<text x="450" y="383" fill="#94a3b8" font-size="12" text-anchor="middle">Comparer un client affecté et un client sain dans les mêmes conditions.</text>
</svg></div>

### 8.1 Commencer par décrire précisément le symptôme

Recueillir au minimum : utilisateur et appareil, système/driver, SSID, heure de début, emplacement, BSSID si disponible, bande/canal, symptôme exact, portée (un appareil ou beaucoup), services affectés et changements récents. Distinguer « je ne vois pas le réseau », « je ne peux pas m’associer », « connecté sans IP », « IP obtenue mais DNS en échec », « signal bon mais débit lent » et « connexion coupée lors du déplacement ». Ces symptômes pointent vers des couches différentes.

### 8.2 Construire des preuves comparables

Comparer un client affecté et un client sain dans les mêmes conditions. Contrôler les journaux du client, AP, contrôleur, RADIUS, DHCP et pare-feu selon le point d’échec. Conserver les horodatages en tenant compte des décalages d’horloge; synchroniser les équipements avec NTP lorsque possible. Avant de changer plusieurs paramètres, relever l’état initial et noter une hypothèse testable.

**Règle opérationnelle : une modification à la fois.** Si l’on change simultanément canal, puissance, sécurité et largeur, l’amélioration ou la dégradation ne peut pas être attribuée à un facteur précis. Pour un service critique, prévoir une fenêtre de changement, des critères de retour arrière et un moyen indépendant de joindre l’équipement.

### 8.3 Cas A — Le client ne voit pas le SSID

1. Vérifier que le WLAN est diffusé et actif dans le profil applicable.
2. Confirmer la compatibilité de bande, canal, largeur, sécurité et génération radio du terminal.
3. Examiner la couverture et les journaux de détection de l’AP.
4. Vérifier si le réseau est volontairement masqué et si le client doit le configurer manuellement — masquer le SSID n’est pas une mesure de sécurité suffisante.
5. Comparer un autre terminal et une autre position.
6. Si la bande utilise DFS ou fait l’objet d’un changement de canal, corréler les événements RF et système.

### 8.4 Cas B — SSID visible, association impossible

Vérifier les trames de gestion et le code de statut de réponse dans les journaux ou une capture autorisée. Contrôler les limites de clients, les politiques d’accès, les paramètres de sécurité compatibles, la liste de contrôle d’accès, la disponibilité d’AP et les éventuels mécanismes de rejet. Dans un réseau entreprise, vérifier les échanges EAP/RADIUS et les certificats. Un mot de passe qui semble correct n’élimine pas l’hypothèse d’une méthode EAP ou d’un profil incompatible.

### 8.5 Cas C — Connecté, mais pas d’adresse IP

Vérifier si le client est autorisé dans le bon VLAN ou rôle. Examiner l’échange DHCP (DISCOVER, OFFER, REQUEST, ACK dans le cas courant) et les journaux du serveur ou du relais. Contrôler les scopes épuisés, les options, la reachability du serveur DHCP, le trunk entre AP/commutateur et le mapping SSID-VLAN. Si une IP automatique de repli apparaît, elle est un indice, non une preuve suffisante : confirmer le résultat dans les journaux DHCP.

### 8.6 Cas D — IP attribuée, mais accès applicatif impossible

Procéder par étapes : tester la passerelle locale, vérifier la table ARP/ND et la route, interroger DNS, puis tester la destination par IP si cela est pertinent et autorisé. Si l’accès par IP fonctionne mais pas par nom, examiner DNS, suffixes de recherche et politique. Si seul un service échoue, vérifier certificat TLS, proxy, VPN, pare-feu, MTU et service distant. Ne pas désactiver le pare-feu au hasard : créer un test contrôlé, borné dans le temps, puis restaurer la politique.

### 8.7 Cas E — Le Wi-Fi est lent alors que le signal semble bon

1. Mesurer la latence et le débit vers une cible locale filaire saine avant de tester Internet.
2. Observer l’occupation du canal, le nombre de clients, les retries et les débits de données.
3. Comparer le client en 2,4 et 5/6 GHz si le matériel, la réglementation et la politique le permettent.
4. Vérifier la largeur du canal et l’utilisation des canaux adjacents.
5. Comparer un client récent et un client ancien, et tester près de l’AP puis dans la zone problématique.
6. Examiner le port uplink, l’agrégation Ethernet, l’alimentation, le contrôleur, le routage et la connexion Internet.
7. Isoler une éventuelle limitation du serveur, du VPN, du DNS ou de l’application.

### 8.8 Cas F — Coupures pendant le déplacement

Relever la chronologie, la variation de BSSID, la durée de coupure, les messages de roaming, la couverture du trajet et la cohérence de sécurité/VLAN. Tester 802.11k/v/r sur un petit groupe pilote après avoir vérifié le support du terminal et les contraintes de compatibilité. Ne pas régler un seuil de déconnexion très agressif sans mesure : cela peut provoquer des bascules répétées plutôt qu’un itinérance stable.


## 9. Outils de diagnostic

### 9.1 Sous Windows

Dans un terminal, ces commandes peuvent fournir un premier aperçu; leur sortie exacte varie selon la version de Windows et le pilote.

```powershell
netsh wlan show interfaces
netsh wlan show drivers
netsh wlan show networks mode=bssid
ipconfig /all
ipconfig /renew
nslookup example.com
ping <adresse-de-la-passerelle>
```

Interprétation : `show interfaces` expose notamment l’état, le SSID, le BSSID, le type radio, le canal et des indicateurs de signal; `show drivers` aide à identifier les capacités annoncées par le pilote; `show networks mode=bssid` liste les BSSID visibles selon ce que le client a détecté. Le pourcentage de signal affiché par Windows n’est pas une mesure SNR standardisée entre tous les adaptateurs.

### 9.2 Sous Linux

Selon la distribution, le pilote et les droits disponibles :

```bash
nmcli device status
nmcli device wifi list
nmcli -f IN-USE,SSID,BSSID,CHAN,RATE,SIGNAL,SECURITY device wifi list
iw dev
iw dev wlan0 link
ip address show
ip route
resolvectl status
```

Remplacer `wlan0` par le nom réel de l’interface (souvent de type `wlp...`). `iw` et `nmcli` ne fournissent pas exactement les mêmes informations sur toutes les cartes. Il faut éviter de lancer des commandes de changement de canal ou de mode sur un réseau de production sans comprendre leurs effets.

### 9.3 Wireshark et mode monitor

Pour capturer les trames 802.11 brutes, l’adaptateur, le chipset, le pilote et le système doivent prendre en charge le mode monitor. En fonction de la plateforme, activer ce mode peut déconnecter l’interface du réseau normal. Une capture ne voit généralement que l’activité du canal sur lequel la radio est réglée, et le résultat dépend de l’antenne, du placement, du filtre, de l’horodatage et des pertes de capture. On peut donc manquer un échange même s’il a eu lieu sur un autre canal ou hors de portée du capteur.

Filtres d’affichage utiles lorsqu’ils s’appliquent aux champs présents dans le type de capture :

```text
wlan.fc.type == 0              # trames de gestion
wlan.fc.type == 1              # trames de contrôle
wlan.fc.type == 2              # trames de données
wlan.fc.type_subtype == 0x08   # beacon, selon décodage de trame
wlan.fc.type_subtype == 0x04   # probe request, selon décodage
wlan.fc.type_subtype == 0x0b   # authentication, selon décodage
wlan.fc.type_subtype == 0x00   # association request, selon décodage
```

La syntaxe et les champs disponibles dépendent de la version de Wireshark et du type d’encapsulation capturé; utiliser l’autocomplétion et la référence des champs de la version installée. Voir le [guide Wireshark](https://www.wireshark.org/docs/wsug_html/) et la [FAQ sur les captures WLAN](https://www.wireshark.org/download/docs/faq.html). Ne capturer que les réseaux et données pour lesquels on dispose d’une autorisation explicite, protéger les fichiers PCAP et supprimer/masquer les données sensibles avant partage.

### 9.4 Journaux et télémétrie des contrôleurs

Utiliser les journaux et métriques correspondant au constructeur : état d’association, raison de déconnexion, RSSI/SNR, canal, retries, vitesse négociée, temps d’antenne, charge radio, événements DFS, historique de roaming, erreurs de sécurité, état du tunnel, utilisation uplink et capacité du scope DHCP. Préférer des comparaisons par fenêtre horaire et par zone plutôt qu’un seul instantané global.

Un tableau de bord agrégé peut masquer un problème localisé. Une moyenne de signal élevée ne prouve pas que le client affecté dispose d’une liaison fiable; une moyenne de charge raisonnable peut cacher un canal saturé dans une salle particulière.


## 10. Études de cas guidées

### Cas 1 — Téléchargement lent dans une salle de cours

**Symptôme :** le signal indiqué sur les ordinateurs est élevé, mais le téléchargement et les appels vidéo sont irréguliers entre 10 h et midi. Les tests sont corrects tôt le matin.

**Hypothèses à comparer :** contention de temps d’antenne, clients à faible débit, canaux co-canal, uplink surchargé, DHCP/DNS ou lien Internet. La variation temporelle suggère la charge, mais elle ne prouve pas à elle seule que la radio est en cause.

**Procédure :**
1. Tester la latence vers une cible locale filaire et vers une destination externe.
2. Comparer 9 h et 11 h : occupation du canal, clients actifs par radio, retries et distribution des débits PHY.
3. Inspecter les canaux utilisés par les AP voisins et l’effet des largeurs de canal.
4. Vérifier l’uplink Ethernet et les compteurs du commutateur.
5. Réaliser une modification pilote contrôlée (par exemple, ajustement de largeur ou de canal si les mesures la justifient).
6. Répéter les mêmes tests aux mêmes heures et comparer le débit utile, la latence et les retries.

**Correction attendue :** ne pas commencer par augmenter la puissance d’émission. La preuve doit montrer si la limitation est RF, uplink ou applicative.

### Cas 2 — Un utilisateur ne peut plus rejoindre le WLAN entreprise

**Symptôme :** l’appareil voit le SSID, puis affiche une erreur d’identification. D’autres collègues continuent de fonctionner.

**Procédure :** confirmer heure, modèle d’appareil et méthode de sécurité; vérifier date/heure et certificats du client; corréler journaux du client, AP/contrôleur et RADIUS; inspecter le code de refus ou le timeout; contrôler si le certificat serveur attendu est validé et si une politique de groupe a changé. Ne demander jamais d’envoyer un mot de passe en clair dans un ticket.

**Interprétations :** un RADIUS `Reject` avec raison explicite oriente vers une politique ou une identité; un timeout sans demande reçue peut indiquer un chemin réseau, un DNS de dépendance, un pare-feu ou un serveur indisponible. Une association réussie suivie d’un blocage pointe plus probablement vers la négociation de clés ou une étape ultérieure.

### Cas 3 — Coupure brève lors d’un appel vocal en mouvement

**Symptôme :** l’appel se dégrade à chaque passage d’un couloir vers une salle de réunion.

**Procédure :** effectuer plusieurs passages avec un appareil témoin; enregistrer l’heure et les BSSID successifs; cartographier RSSI et SNR; examiner si le client garde le premier AP trop longtemps; mesurer durée de transition et latence applicative; vérifier les paramètres de sécurité et l’affectation réseau des deux AP; évaluer 802.11k/v/r sur un pilote compatible.

**Point important :** la présence de 802.11r ne garantit pas à elle seule un roaming fluide. La couverture, la décision du client, la continuité du réseau de distribution et le comportement de l’application doivent tous être vérifiés.


## 11. Ateliers pratiques et exercices

### Atelier A — Cartographier une connexion

**Objectif :** établir si le défaut se situe au niveau de l’association, de la sécurité ou des services IP.

1. Connecter un terminal à un SSID de laboratoire autorisé.
2. Noter SSID, BSSID, bande, canal et qualité du signal.
3. Vérifier l’adresse IP, le masque, la passerelle et les serveurs DNS.
4. Tester la passerelle puis une adresse connue sur le LAN de laboratoire.
5. Tester la résolution DNS séparément.
6. Consigner chaque résultat dans une chronologie.

**Résultat attendu :** une suite de tests qui sépare les étapes radio et IP au lieu d’un verdict vague « Wi-Fi fonctionne/ne fonctionne pas ».

### Atelier B — Observer la contention

**Objectif :** comprendre l’effet d’une charge radio sans perturber un réseau tiers.

Dans un laboratoire contrôlé, relever l’occupation du canal et les statistiques de retransmission avec peu de clients, puis avec un trafic autorisé généré par plusieurs clients. Comparer débit utile, latence, retries et utilisation du canal. Répéter avec un canal planifié différemment seulement si le matériel permet un changement sûr. Documenter les conditions du test, le canal, la largeur et les appareils.

### Atelier C — Tester une transition de BSSID

**Objectif :** identifier l’événement qui interrompt l’application.

Utiliser deux AP de laboratoire avec le même SSID et une politique cohérente. Marcher sur un trajet prédéfini avec un terminal témoin; relever les BSSID, le temps de transition et une sonde applicative. Si l’équipement le permet, comparer un scénario avec les optimisations de roaming activées et un scénario témoin. Valider avant le test les capacités du terminal et prévoir un retour arrière.

### Questions de validation

1. Pourquoi une association réussie ne garantit-elle pas qu’un client peut utiliser Internet?
2. Quelle différence entre SSID et BSSID?
3. Pourquoi augmenter la largeur de canal peut-il réduire les performances globales dans un bâtiment dense?
4. Quel coût les retransmissions ajoutent-elles au réseau radio?
5. Un RSSI fort garantit-il un SNR favorable? Explique.
6. Quel est le rôle de 802.11k, 802.11v et 802.11r? En quoi sont-ils différents?
7. Pourquoi faut-il vérifier la validation de certificat dans un WLAN WPA2/WPA3-Enterprise?
8. Comment distinguer une panne DHCP d’un échec DNS?
9. Pourquoi une capture Wireshark en mode monitor peut-elle manquer des trames pertinentes?
10. Que faut-il mesurer avant et après un changement RF?
11. Pourquoi une puissance AP plus élevée peut-elle aggraver le comportement des clients?
12. Pourquoi faut-il tester un changement 802.11r sur le parc de terminaux réel?

### Corrigé succinct

1. Les étapes IP, DNS, routage, pare-feu et application sont distinctes de l’association radio.
2. Le SSID est le nom logique du WLAN; le BSSID identifie la cellule radio observée.
3. Les canaux larges consomment davantage de spectre contigu et peuvent diminuer les possibilités de réutilisation.
4. Elles consomment du temps d’antenne, augmentent la latence et diminuent le débit utile.
5. Non : un bruit ou des interférences élevés peuvent dégrader le SNR même avec un signal puissant.
6. 11k fournit des informations de voisinage, 11v permet des recommandations de transition, 11r accélère certains échanges de sécurité durant le roaming.
7. Une mauvaise validation peut exposer les identifiants à un serveur frauduleux.
8. DHCP attribue la configuration IP; DNS résout les noms une fois que l’interface dispose d’une configuration suffisante. Examiner les échanges et journaux de chaque service.
9. L’adaptateur peut ne pas supporter monitor mode, peut être réglé sur un autre canal, subir des pertes ou être placé hors de portée.
10. Débit utile, latence, pertes, retries, charge/temps d’antenne, BSSID, RSSI/SNR et conditions de mesure comparables.
11. Le client peut ne pas émettre à une puissance équivalente; la liaison montante peut rester faible et les cellules peuvent trop se chevaucher.
12. Les appareils et pilotes ne prennent pas tous en charge les mêmes modes et certains peuvent avoir des problèmes de compatibilité.


## 12. Checklist d’intervention Wi-Fi

### Avant toute modification

- [ ] Décrire le symptôme en termes observables et noter l’heure, la zone, le SSID et le nombre de clients touchés.
- [ ] Identifier si le défaut est lié à la découverte, l’association, l’authentification, l’attribution IP, le DNS, le routage ou l’application.
- [ ] Relever l’état initial : canal, largeur, puissance, RSSI/SNR disponible, retries, clients, charge radio, version du logiciel et changements récents.
- [ ] Comparer un appareil sain dans des conditions similaires.
- [ ] Définir une hypothèse vérifiable, le test, le risque et les critères de réussite.
- [ ] Prévoir un retour arrière et ne changer qu’un facteur à la fois.

### Pendant le diagnostic

- [ ] Corréler les horodatages du terminal, AP, contrôleur, RADIUS, DHCP et pare-feu selon les symptômes.
- [ ] Vérifier la disponibilité des AP, l’uplink Ethernet, l’alimentation PoE et les VLAN.
- [ ] Mesurer la qualité et la capacité RF, pas uniquement la puissance reçue.
- [ ] Vérifier les règles réglementaires et la compatibilité des bandes et canaux.
- [ ] Protéger les captures et journaux contenant des données privées ou des identifiants.

### Après le changement

- [ ] Répéter les mêmes tests dans les mêmes zones et autant que possible aux mêmes conditions de charge.
- [ ] Contrôler le débit utile, la latence, les pertes, les retries, le roaming et l’accès à l’application.
- [ ] Vérifier qu’aucun autre type de client ou service n’a été dégradé.
- [ ] Documenter la configuration avant/après, les résultats et le plan de retour arrière utilisé ou non.
- [ ] Communiquer la cause confirmée, les limites restantes et le plan de surveillance.


## 13. Glossaire de révision

- **802.1X** : contrôle d’accès réseau fondé sur l’authentification, fréquemment utilisé avec EAP en entreprise.
- **802.11** : famille de normes IEEE qui définit les réseaux locaux sans fil Wi-Fi.
- **802.11ax / Wi-Fi 6** : génération améliorant notamment l’efficacité multi-utilisateur avec OFDMA et d’autres mécanismes.
- **802.11be / Wi-Fi 7** : génération plus récente dont certaines fonctionnalités incluent MLO et canaux très larges lorsque disponibles et autorisés.
- **Airtime** : fraction du temps pendant laquelle le canal est consommé par les transmissions, attentes et échanges associés.
- **BSSID** : identifiant d’un BSS / radio AP observable dans les trames 802.11.
- **DFS** : sélection dynamique de fréquence utilisée pour respecter des contraintes de partage du spectre, notamment avec radar dans certains canaux.
- **EAP** : cadre d’authentification qui peut s’appuyer sur différentes méthodes.
- **EDCA** : mécanisme d’accès au médium avec catégories de contention pour la QoS.
- **MCS** : combinaison de modulation et de codage associée à un mode de transmission.
- **MLO** : Multi-Link Operation, fonctionnement multi-lien de certaines implémentations Wi-Fi 7.
- **MU-MIMO** : transmission multi-utilisateur utilisant plusieurs flux spatiaux quand les conditions le permettent.
- **OFDMA** : partage de ressources fréquentielles pour desservir plusieurs stations dans une transmission planifiée.
- **PMF / 802.11w** : protection de certaines trames de gestion robustes.
- **RADIUS** : protocole fréquemment utilisé pour transporter les requêtes d’authentification et des politiques d’accès.
- **RSSI** : indicateur de puissance reçue, à interpréter avec prudence selon le matériel.
- **SAE** : mécanisme d’authentification employé par WPA3-Personal.
- **SNR** : rapport entre signal et bruit.
- **SSID** : nom logique utilisé pour identifier le WLAN à l’utilisateur.
- **WPA2/WPA3** : familles de profils de sécurité Wi-Fi dont les possibilités dépendent des modes et appareils compatibles.


## 14. Références techniques

Les ressources suivantes permettent d’approfondir des mécanismes précis. Les procédures d’administration et les capacités disponibles peuvent changer selon la version du produit; vérifier les guides correspondant aux équipements déployés.

1. [Cisco — Comprendre les mécanismes de roaming 802.11r, 802.11k et 802.11v](https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/221671-understand-802-11r-11k-11v-fast-roams-on.html) — mis à jour en mai 2026.
2. [Cisco — Entreprise : bonnes pratiques Wi-Fi pour les appareils Apple](https://www.cisco.com/c/en/us/products/collateral/wireless/access-points/enterprise-best-practices-ios-ipados-wp.html) — compatibilité et optimisation du roaming.
3. [Cisco — BSS Coloring dans Wi-Fi 6](https://www.cisco.com/c/en/us/td/docs/wireless/controller/9800/26-1/configuration-guide/wl-26-1-cg/bss-coloring/bss-coloring-overview.html) — réutilisation spatiale et BSS voisins.
4. [Wireshark — User’s Guide](https://www.wireshark.org/docs/wsug_html/) — analyse des captures et filtres.
5. [Wireshark — FAQ de capture WLAN](https://www.wireshark.org/download/docs/faq.html) — mode monitor et limites de compatibilité.
6. [Aruba — Campus Wireless Networks: Planning and Overview](https://www.arubanetworks.com/assets/vrd/2018_01_02_Campus_6_x_Planning_and_Overview.pdf) — principes de planification radio (document de génération antérieure, à compléter par la documentation actuelle du constructeur).
7. [Cisco — Présentation des capacités Wi-Fi 6](https://blogs.cisco.com/networking/wi-fi-6-powers-real-world-enterprise-applications) — OFDMA, MU-MIMO, TWT et BSS Coloring.


## Conclusion

Un dépannage intermédiaire du Wi-Fi doit séparer le fonctionnement radio 802.11 des étapes d’authentification, d’autorisation, de réseau IP et d’application. Les canaux, la largeur, la puissance, l’occupation du médium et les retransmissions forment un système interdépendant : améliorer un indicateur isolé peut dégrader le reste du WLAN. La bonne méthode consiste à établir une base de mesure, formuler une hypothèse, réaliser un test contrôlé, comparer les résultats, puis documenter la décision.

Le principe professionnel à retenir est simple : **ne pas conclure « problème Wi-Fi » tant que le premier point de défaillance n’a pas été identifié et étayé par des preuves reproductibles.**
