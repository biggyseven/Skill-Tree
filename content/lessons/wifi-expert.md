# Wi-Fi 802.11 — Niveau Expert

**Niveau :** Expert  
**Prérequis :** fondamentaux Wi-Fi, adressage IP, VLAN, DHCP/DNS, notions de radiofréquence, captures de paquets et principes de sécurité réseau.

Le niveau expert ne consiste pas à activer tous les paramètres « avancés » d’un contrôleur. Il consiste à concevoir un WLAN en fonction d’exigences mesurables, à expliquer les compromis radio et protocole, puis à prouver sur le terrain que la solution répond à ces exigences. Le débit PHY annoncé par une fiche technique ne suffit jamais à prédire l’expérience utilisateur : la performance dépend de l’airtime réellement disponible, de la contention, des retransmissions, de la qualité de la liaison, du comportement des terminaux, de la conception IP, des services AAA et de l’application.

Ce cours adopte une approche multiconstructeur. Les exemples de configuration sont des modèles de conception, pas des commandes universelles : les noms de menus, seuils, options et comportements varient selon le contrôleur, le micrologiciel, le domaine réglementaire et les capacités des clients. Toute modification de production doit être testée sur la plateforme exacte avant déploiement.

> **Fil directeur :** définir le résultat attendu, établir une ligne de base, formuler une hypothèse, changer une variable, mesurer l’effet, conserver ou annuler le changement. Éviter les modifications simultanées qui rendent le diagnostic impossible.

## 1. Architecture d’un WLAN d’entreprise à l’échelle

### 1.1. Les plans à distinguer

Un réseau Wi-Fi professionnel combine plusieurs couches. Sur le **plan radio**, les stations et les points d’accès se partagent un médium commun par canal. Sur le **plan de contrôle WLAN**, les AP diffusent les SSID, annoncent les paramètres, prennent part aux décisions de gestion radio et, selon l’architecture, établissent un tunnel vers un contrôleur. Sur le **plan de données**, les trames sont bridgées localement ou transportées jusqu’à un point central avant de rejoindre VLAN, VRF, pare-feu et passerelles. Les services d’identité et de politiques — RADIUS, PKI, annuaire, NAC — forment une dépendance supplémentaire qui peut rendre un réseau inutilisable même lorsque le RF est excellent.

Il faut donc éviter le diagnostic « le Wi-Fi ne marche pas » sans préciser le niveau observé. Une station peut voir le SSID mais échouer à l’authentification ; être associée sans recevoir de bail DHCP ; obtenir une adresse mais échouer sur DNS ; résoudre les noms mais être bloquée par une ACL ; ou avoir une connectivité IP correcte mais subir des latences d’airtime. Chaque symptôme demande une preuve différente.

### 1.2. Modèles centralisés, distribués et hybrides

Dans une architecture centralisée, les AP établissent généralement un tunnel de contrôle vers un contrôleur. Le trafic utilisateur peut être centralisé ou localement commuté selon le WLAN. Ce modèle facilite certaines politiques communes et opérations à grande échelle, mais le design doit tenir compte de la capacité des contrôleurs, de la résilience des tunnels, des chemins vers les services centraux et des pannes WAN.

Dans une architecture distribuée, le plan de données est davantage traité au niveau de l’AP ou du site. Cette approche peut diminuer le détour réseau et conserver des services locaux en cas de perte d’un contrôleur, si elle est correctement conçue. Elle déplace toutefois une partie des contraintes vers la cohérence de configuration, la distribution des politiques, les services DHCP/DNS locaux, la segmentation et l’observabilité.

Une architecture hybride est fréquente : gestion et certaines décisions sont centralisées, tandis que le trafic de données est localement commuté pour certains SSID ou sites. Il faut documenter, SSID par SSID, le point où se termine le tunnel, le VLAN ou rôle affecté, le chemin vers le pare-feu et le comportement en mode dégradé. Une documentation qui mentionne simplement « contrôleur redondant » ne démontre pas la continuité de service : il faut tester ce qui arrive aux associations existantes, aux nouvelles authentifications, au roaming et aux trafics déjà établis lors d’une perte de nœud.

### 1.3. Vue logique de référence

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" width="100%" height="auto" role="img" aria-label="Plan de canaux pour une zone haute densité : cellules voisines utilisent des canaux différents quand le plan le permet, avec chevauchement de couverture maîtrisé"><defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#63d8ff"/></marker><marker id="arrp" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#c4a4ff"/></marker></defs><style>.t{font:700 16px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.s{font:12.5px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.small{font:11px system-ui,sans-serif;fill:#b8c7d8;text-anchor:middle}.node{stroke-width:2;rx:12}.blue{fill:#14334a;stroke:#5ecbff}.green{fill:#153b2b;stroke:#73e3a2}.purple{fill:#2b2046;stroke:#c4a4ff}.amber{fill:#45331b;stroke:#ffc76b}.red{fill:#451f2a;stroke:#ff858c}.p{fill:none;stroke:#63d8ff;stroke-width:2.6;stroke-dasharray:8 7;marker-end:url(#arr);animation:dash 2.6s linear infinite}.pp{fill:none;stroke:#c4a4ff;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#arrp);animation:dash 3s linear infinite}@keyframes dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.p,.pp{animation:none}}.ap{fill:#102536;stroke:#4f7891;stroke-width:1.5;stroke-dasharray:5 5}.cell{fill:#153b2b;fill-opacity:.38;stroke:#73e3a2;stroke-width:2}.label{font:700 15px system-ui,sans-serif;fill:#f3f7ff;text-anchor:middle}.ch{font:700 14px system-ui,sans-serif;fill:#71e2a2;text-anchor:middle}</style><rect x="15" y="15" width="870" height="390" rx="18" fill="#0b1220" stroke="#24384c"/><text x="450" y="43" class="t">Plan RF : priorité à l’airtime, pas au débit théorique</text>
<circle cx="220" cy="170" r="105" class="cell"/><circle cx="450" cy="170" r="105" class="cell"/><circle cx="680" cy="170" r="105" class="cell"/>
<rect x="158" y="130" width="124" height="70" rx="10" class="node blue"/><text x="220" y="156" class="label">AP-1</text><text x="220" y="180" class="ch">Canal 36</text>
<rect x="388" y="130" width="124" height="70" rx="10" class="node blue"/><text x="450" y="156" class="label">AP-2</text><text x="450" y="180" class="ch">Canal 44</text>
<rect x="618" y="130" width="124" height="70" rx="10" class="node blue"/><text x="680" y="156" class="label">AP-3</text><text x="680" y="180" class="ch">Canal 36</text>
<path d="M220 200 V224" class="p"/><path d="M450 200 V224" class="p"/><path d="M680 200 V224" class="p"/><rect x="170" y="229" width="100" height="34" rx="8" fill="#12283a" stroke="#63d8ff" stroke-width="1.5"/><text x="220" y="251" class="s">Client A</text><rect x="400" y="229" width="100" height="34" rx="8" fill="#12283a" stroke="#63d8ff" stroke-width="1.5"/><text x="450" y="251" class="s">Client B</text><rect x="630" y="229" width="100" height="34" rx="8" fill="#12283a" stroke="#63d8ff" stroke-width="1.5"/><text x="680" y="251" class="s">Client C</text>
<text x="450" y="310" class="s">Les canaux sont un exemple illustratif, pas un plan universel.</text><text x="450" y="334" class="s">Valider domaine réglementaire, DFS, voisinage, capacités clients et mesures sur site.</text>
<rect x="92" y="354" width="716" height="34" rx="9" class="node amber"/><text x="450" y="376" class="s">Un RSSI élevé avec beaucoup de contention peut rester lent.</text></svg></div>

La figure ci-dessus illustre une idée centrale : en environnement dense, augmenter la largeur de canal ou la puissance n’améliore pas nécessairement le service. Les canaux doivent être planifiés selon les bandes autorisées, le voisinage réel, les types de terminaux et le profil du trafic. Dans une salle de conférence où beaucoup de clients envoient peu de données, la capacité dépend souvent davantage du nombre de clients en concurrence et des coûts d’accès au médium que du pic de débit d’un terminal récent.

### 1.4. Exigences à formaliser avant l’installation

Une conception experte commence par des exigences fonctionnelles et mesurables :

- Types de terminaux : ordinateurs, téléphones, scanners, terminaux industriels, IoT, voix sur WLAN, invités et appareils personnels.
- Applications : débit, latence, gigue, pertes tolérées, taille des rafales, durée des sessions, sens dominant du trafic.
- Mobilité : utilisateurs statiques, chariots, appels audio en déplacement, voix/vidéo temps réel, roaming entre bâtiments ou sites.
- Densité : clients associés simultanément par zone, clients actifs au même moment, répartition par bandes et génération radio.
- Sécurité : identité individuelle, segmentation dynamique ou statique, exigences de conformité, gestion des certificats, visibilité des appareils non gérés.
- Résilience : dépendance aux services centralisés, continuité lors de panne d’AP, de contrôleur, de lien filaire ou de serveur RADIUS.
- Exploitation : journalisation, inventaire, sauvegarde de configuration, canaux de support, fenêtres de changement et procédure de retour arrière.

La différence entre **clients associés** et **clients actifs** est importante. Mille terminaux peuvent rester connectés mais générer peu de trafic, alors que cent clients actifs envoient simultanément des flux vidéo ou synchronisent de gros fichiers. Dimensionner seulement à partir du nombre total d’adresses MAC ou du débit WAN sous-estime souvent la concurrence radio.

## 2. Ingénierie RF : du niveau reçu à l’airtime

### 2.1. Puissance, dBm, SNR et bruit

Le RSSI exprime une estimation de la puissance reçue ; le SNR compare le signal utile au bruit observé. Ces mesures sont utiles mais ne décrivent pas seules la qualité. Deux endroits peuvent présenter un RSSI similaire et des performances très différentes si l’un subit des interférences, des collisions, un multipath défavorable, une contention importante ou une différence de capacité entre les deux sens de la liaison.

Le RSSI affiché par un client ou un contrôleur n’est pas toujours mesuré de manière identique. Il peut être moyenné, filtré ou estimé depuis différentes chaînes radio. Comparer des valeurs issues de deux constructeurs exige donc de vérifier la méthode et la bande considérées. Le terminal peut aussi recevoir correctement les signaux de l’AP alors que l’AP reçoit mal le terminal : le lien montant et le lien descendant ne sont pas nécessairement symétriques, en raison des puissances d’émission, antennes, orientations, chaînes radio et implémentations différentes.

Les décibels sont logarithmiques. Une différence de 3 dB représente environ un facteur deux de puissance, 10 dB un facteur dix. Les unités ne doivent pas être mélangées : dBm est une puissance absolue référencée à 1 mW ; dB est un rapport. Pour une chaîne radio, l’EIRP résulte de la puissance conduite, du gain d’antenne et des pertes de câble, selon la convention de mesure. Les limites légales et les modalités de contrôle de puissance dépendent de la bande, du domaine réglementaire et du type d’appareil.

Le SNR n’est pas une valeur d’acceptation universelle. Une modulation très élevée nécessite généralement une qualité de signal élevée, mais une application peut être satisfaite avec une modulation plus basse si l’airtime reste disponible. Inversement, une valeur de SNR jugée « bonne » peut coexister avec des retransmissions si l’environnement contient des sources d’interférence ou si le client et l’AP n’entendent pas les mêmes stations.

### 2.2. Budget de liaison et asymétrie

Un budget de liaison sert à estimer si le signal reçu restera exploitable pour un scénario donné. Il faut tenir compte de la puissance d’émission autorisée, des gains d’antenne, des pertes, de la propagation, des matériaux de construction, du corps humain, des meubles et des marges pour le fading. Une simulation n’est pas une vérité terrain : les plans de construction, matériaux, hauteurs et géométries des antennes doivent être aussi précis que possible, puis confirmés par une étude de site.

La portée d’une radio ne doit pas être déduite uniquement de la puissance maximale de l’AP. Si l’AP entend un client à la limite de sa couverture, ce client peut ne pas atteindre l’AP avec une puissance ou une qualité suffisante. Le design doit donc se baser sur la liaison bidirectionnelle. La réduction de puissance des AP peut parfois améliorer le roaming et diminuer la cellule excessive, mais elle peut aussi créer des trous de couverture. Le réglage doit être validé avec des terminaux représentatifs, pas par une règle arbitraire identique pour tous les sites.

### 2.3. Airtime : la ressource rare

Le Wi-Fi est un médium partagé à l’intérieur d’une zone de contention. Un terminal lent, des retransmissions ou des clients qui occupent longtemps le canal peuvent consommer une part importante du temps d’antenne. Il est donc plus utile d’analyser l’airtime occupé, le nombre de retries, les taux MCS, les largeurs de canal, les temps d’attente et le comportement des flux que de regarder uniquement le débit négocié.

Un modèle pédagogique peut être utilisé pour raisonner sur le temps d’antenne : si un flux utile demande une durée d’émission plus longue à un débit PHY faible, son coût d’airtime pour une même quantité de données est plus élevé. Ce modèle doit ajouter préambules, en-têtes, ACK/Block ACK, intervalles inter-trames, contention et retransmissions pour un calcul réaliste. Le débit applicatif sera toujours inférieur au débit PHY à cause de ces frais et du partage avec les autres stations.

**Exemple illustratif :** une zone possède un canal avec 60 % d’occupation mesurée sur une période représentative. Cela ne signifie pas qu’elle dispose d’exactement 40 % de capacité utile : une partie du temps peut être perdue en collisions, retransmissions, overhead ou trafic que l’application ne considère pas utile. La mesure doit être rapprochée du débit utile, des retards et de la distribution des clients. L’occupation du canal doit être mesurée par radio et par canal, en période normale et aux heures de pointe.

### 2.4. Largeur de canal et compromis densité/débit

Des canaux larges peuvent permettre un débit PHY plus élevé à un client proche de l’AP, mais réduisent le nombre de canaux non chevauchants disponibles dans une bande donnée et rendent chaque transmission plus vulnérable à l’occupation sur une partie du spectre agrégé. La largeur optimale dépend du domaine réglementaire, des canaux disponibles, des exigences de débit, de la densité, du SNR et de la proportion de clients compatibles.

Dans les environnements haute densité, 20 MHz est souvent un meilleur point de départ que 80 MHz ou 160 MHz, car la réutilisation des canaux et l’équité entre clients peuvent être plus importantes que le débit de pointe d’une station. Ce n’est toutefois pas une règle absolue : une salle de production créative avec peu de stations, des transferts volumineux et un spectre propre peut bénéficier d’une largeur supérieure. Les résultats doivent être comparés par des tests contrôlés sur le même trajet et le même type de client.

Sur 2,4 GHz, les canaux sont rares et les recouvrements de canaux adjacents provoquent des problèmes importants. Une largeur de 20 MHz est généralement le choix professionnel prudent. La disponibilité exacte des canaux dépend du pays ; ne pas copier le plan d’un autre domaine réglementaire. En 5 GHz, tenir compte des canaux DFS, des événements radar, des clients qui ne prennent pas en charge certains canaux et des temps de changement de canal. En 6 GHz, la disponibilité des sous-bandes et la puissance permise diffèrent selon le cadre réglementaire et le type de déploiement. Toute recommandation doit être vérifiée dans le pays d’installation.

### 2.5. DFS et sélection dynamique des canaux

DFS (*Dynamic Frequency Selection*) permet l’utilisation de certains canaux partagés avec des systèmes prioritaires, notamment radar, sous conditions réglementaires. Si un événement radar est détecté, l’AP doit respecter les règles applicables pour quitter le canal. Cela peut entraîner une interruption ou une réassociation, selon le client et l’implémentation. Il est incorrect de considérer DFS comme un canal toujours disponible ou de le désactiver systématiquement sans examiner les obligations locales et la conception du site.

Lors d’un incident DFS, collecter l’heure, le canal avant/après, les journaux de détection radar, les clients affectés, la durée de récupération et les changements de canal concurrents. Comparer plusieurs jours ou sites peut aider à séparer une cause réglementaire attendue d’un problème de stabilité du RF. Ne pas attribuer automatiquement toute déconnexion au roaming : le canal a pu changer à la suite d’un événement DFS ou d’une optimisation radio.

### 2.6. Réutilisation de canaux et puissance

La planification doit éviter le raisonnement « une AP par salle et à puissance maximale ». Des cellules trop grandes peuvent augmenter la co-channel interference (CCI), car plusieurs cellules sur le même canal s’entendent et doivent partager le médium. Des cellules trop petites ou trop nombreuses peuvent aussi générer du bruit et de la contention si les canaux ne sont pas planifiés. La puissance, la hauteur et le type d’antenne, l’orientation et la largeur de canal se conçoivent ensemble.

La couverture utile est celle qui permet au client d’échanger dans les deux sens et d’effectuer un roaming convenable, pas simplement celle où un SSID apparaît dans une liste. Une étude passive mesure ce que le client entend ; une étude active mesure le comportement d’un client associé ; une étude de spectre peut identifier des sources non-Wi-Fi que la seule analyse des trames ne révèle pas toujours. Une étude complète combine ces méthodes en fonction du besoin.

## 3. Wi-Fi 6/6E/7 : utiliser la fonctionnalité pertinente

### 3.1. OFDMA, MU-MIMO, BSS Coloring et TWT

Wi-Fi 6, basé sur IEEE 802.11ax, vise notamment une meilleure efficacité dans les environnements où plusieurs stations se disputent les ressources. OFDMA permet à l’AP, dans des transmissions compatibles, de répartir les ressources fréquentielles en unités de ressources (*Resource Units*, RU) destinées à différentes stations. Les échanges coordonnés peuvent réduire certains coûts de contention, notamment lorsque de nombreux clients ont des petits paquets. OFDMA ne signifie pas que tous les terminaux transmettent en continu sans attendre ; la planification, les capacités clients, les tailles de paquets et les conditions radio restent déterminantes.

MU-MIMO utilise plusieurs chaînes spatiales pour servir plusieurs utilisateurs dans des conditions prises en charge par les radios et les clients. OFDMA et MU-MIMO sont des mécanismes différents et peuvent se compléter. Le gain réel dépend des terminaux, de leur géométrie radio, du trafic, des algorithmes du fournisseur et de la situation de contention. Il faut vérifier les capacités des clients plutôt que d’inférer l’utilisation de MU-MIMO depuis la seule génération de l’AP.

BSS Coloring donne une information permettant de distinguer certains transmissions du BSS local et des BSS chevauchants dans un canal partagé. Associé à des paramètres de réutilisation spatiale compatibles, il peut autoriser des décisions plus efficaces sur l’accès au médium. Il n’élimine pas l’interférence : un signal très fort d’un réseau voisin peut toujours perturber la réception. Les seuils de détection doivent être appliqués avec prudence, car être plus agressif peut accroître les collisions ou dégrader certaines stations.

TWT (*Target Wake Time*) permet de négocier des périodes d’activité et de sommeil pour certains clients compatibles, avec des objectifs d’économie d’énergie et de gestion du trafic. Il est surtout pertinent lorsque les terminaux supportent réellement le mécanisme et que le profil de trafic s’y prête. Il n’est pas un bouton universel qui améliore tous les clients, tous les délais et toutes les applications.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 405" width="100%" height="auto" role="img" aria-label="Illustration conceptuelle de l’OFDMA Wi-Fi 6 : l’AP découpe le temps-fréquence en Resource Units afin de servir plusieurs stations dans une transmission coordonnée"><defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#63d8ff"/></marker><marker id="arrp" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#c4a4ff"/></marker></defs><style>.t{font:700 16px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.s{font:12.5px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.small{font:11px system-ui,sans-serif;fill:#b8c7d8;text-anchor:middle}.node{stroke-width:2;rx:12}.blue{fill:#14334a;stroke:#5ecbff}.green{fill:#153b2b;stroke:#73e3a2}.purple{fill:#2b2046;stroke:#c4a4ff}.amber{fill:#45331b;stroke:#ffc76b}.red{fill:#451f2a;stroke:#ff858c}.p{fill:none;stroke:#63d8ff;stroke-width:2.6;stroke-dasharray:8 7;marker-end:url(#arr);animation:dash 2.6s linear infinite}.pp{fill:none;stroke:#c4a4ff;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#arrp);animation:dash 3s linear infinite}@keyframes dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.p,.pp{animation:none}}.ru{stroke:#0b1220;stroke-width:2}.tx{font:700 13px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.gridline{stroke:#3a5063;stroke-width:1}</style><rect x="14" y="12" width="872" height="381" rx="18" fill="#0b1220" stroke="#24384c"/><text x="450" y="40" class="t">Wi-Fi 6 / 802.11ax : partager des ressources temps-fréquence</text>
<text x="91" y="101" class="s">Sans ordonnanceur OFDMA</text><rect x="45" y="120" width="330" height="42" rx="7" class="node blue"/><text x="210" y="146" class="tx">STA A : canal occupé</text><rect x="45" y="169" width="330" height="42" rx="7" class="node amber"/><text x="210" y="195" class="tx">STA B : attend</text><rect x="45" y="218" width="330" height="42" rx="7" class="node amber"/><text x="210" y="244" class="tx">STA C : attend</text>
<text x="655" y="101" class="s">OFDMA : plusieurs RU attribuées</text><rect x="470" y="120" width="355" height="140" rx="7" fill="#0f2030" stroke="#476175"/>
<path d="M470 155 H825 M470 190 H825 M470 225 H825 M588 120 V260 M706 120 V260" class="gridline"/>
<rect x="476" y="126" width="106" height="24" rx="4" fill="#1c5b43" stroke="#73e3a2"/><text x="529" y="143" class="small">RU A</text>
<rect x="594" y="161" width="106" height="24" rx="4" fill="#163f5b" stroke="#63d8ff"/><text x="647" y="178" class="small">RU B</text>
<rect x="712" y="196" width="106" height="24" rx="4" fill="#3d2a5c" stroke="#c4a4ff"/><text x="765" y="213" class="small">RU C</text>
<path d="M375 190 H438" class="p"/><text x="450" y="285" class="s">Schéma conceptuel : tailles et positions des RU variables selon la transmission.</text>
<rect x="105" y="320" width="690" height="44" rx="10" class="node amber"/><text x="450" y="347" class="s">OFDMA réduit certains coûts de contention, mais ne supprime ni interférences ni limites d’airtime.</text></svg></div>

### 3.2. Wi-Fi 6E et la bande 6 GHz

Wi-Fi 6E étend les mécanismes Wi-Fi 6 à la bande 6 GHz lorsque celle-ci est autorisée. Les avantages potentiels incluent un spectre plus large et de nouveaux canaux, ce qui peut réduire la congestion provenant de systèmes plus anciens qui n’opèrent pas dans cette bande. La propagation et les obligations réglementaires diffèrent, et la disponibilité de canaux dépend du pays. Une couverture 6 GHz doit être conçue à partir de mesures et de clients cibles, non à partir d’une hypothèse selon laquelle toutes les fréquences ont une portée identique.

L’accès à 6 GHz peut exiger des méthodes d’authentification et des paramètres de sécurité spécifiques. Les contraintes exactes dépendent de la réglementation, des catégories d’appareils et des règles de certification en vigueur. Avant un déploiement, vérifier les politiques de sécurité compatibles, le support des clients, les exigences de puissance, les mécanismes de coordination de fréquence lorsqu’ils sont applicables et la capacité du réseau filaire en amont.

### 3.3. Wi-Fi 7 / IEEE 802.11be

IEEE 802.11be, commercialisé comme Wi-Fi 7, apporte notamment des canaux allant jusqu’à 320 MHz en 6 GHz lorsque le domaine réglementaire le permet, la modulation 4096-QAM dans des conditions radio suffisamment favorables, le Multi-Link Operation (MLO), le Multi-RU, l’amélioration de l’agrégation des acquittements et la possibilité de *preamble puncturing* selon les capacités du matériel. Les fonctions exactes et leurs combinaisons prises en charge varient selon les AP et clients.

La 4096-QAM peut augmenter l’efficacité spectrale par rapport à 1024-QAM, mais elle demande une qualité de canal élevée. Elle ne constitue donc pas un débit de base garanti à la périphérie d’une cellule. Les canaux 320 MHz occupent une large portion de spectre : leur intérêt se mesure en tenant compte du nombre d’utilisateurs, du spectre disponible, du pays, des interférences et de la possibilité de réutiliser les canaux. Pour un environnement dense, des canaux plus étroits peuvent donner une meilleure capacité agrégée et une meilleure planification.

Le *preamble puncturing* permet à certaines transmissions d’éviter une partie occupée d’un canal plus large tout en utilisant les portions utilisables prévues par le standard et l’implémentation. Ce mécanisme ne doit pas être décrit comme une suppression totale de l’interférence : il dépend du motif de brouillage, du support des composants et du contrôle de l’AP. Vérifier les statistiques du fabricant et les traces plutôt que supposer son activation effective.

MLO permet à des appareils multi-link de maintenir plusieurs liens entre un AP MLD et un client MLD, avec des modes de fonctionnement qui dépendent des capacités radio et des combinaisons de bandes. Selon l’appareil, il peut contribuer à répartir du trafic, à améliorer la fiabilité ou à réduire la latence perçue. Tous les liens ne sont pas nécessairement simultanés dans toutes les configurations : les limites STR/NSTR, le nombre de radios, les bandes et le logiciel importent.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 425" width="100%" height="auto" role="img" aria-label="Wi-Fi 7 Multi-Link Operation : un client multi-link device établit plusieurs liens logiques vers un AP MLD, avec identités liées et possibilités de simultanéité dépendant des capacités radio"><defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#63d8ff"/></marker><marker id="arrp" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#c4a4ff"/></marker><marker id="arrg" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#73e3a2"/></marker></defs><style>.t{font:700 16px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.s{font:12.5px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.small{font:11px system-ui,sans-serif;fill:#b8c7d8;text-anchor:middle}.node{stroke-width:2;rx:12}.blue{fill:#14334a;stroke:#5ecbff}.green{fill:#153b2b;stroke:#73e3a2}.purple{fill:#2b2046;stroke:#c4a4ff}.amber{fill:#45331b;stroke:#ffc76b}.red{fill:#451f2a;stroke:#ff858c}.p{fill:none;stroke:#63d8ff;stroke-width:2.6;stroke-dasharray:8 7;marker-end:url(#arr);animation:dash 2.6s linear infinite}.pp{fill:none;stroke:#c4a4ff;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#arrp);animation:dash 3s linear infinite}@keyframes dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.p,.pp{animation:none}}.band24{fill:#45331b;stroke:#ffc76b;stroke-width:2}.band5{fill:#14334a;stroke:#63d8ff;stroke-width:2}.band6{fill:#153b2b;stroke:#73e3a2;stroke-width:2}.line5{fill:none;stroke:#63d8ff;stroke-width:2.8;stroke-dasharray:8 7;marker-end:url(#arr);animation:dash 2.5s linear infinite}.line6{fill:none;stroke:#73e3a2;stroke-width:2.8;stroke-dasharray:6 7;marker-end:url(#arrg);animation:dash 2.7s linear infinite}@keyframes dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.line5,.line6{animation:none}}</style><rect x="14" y="12" width="872" height="399" rx="18" fill="#0b1220" stroke="#24384c"/><text x="450" y="41" class="t">Wi-Fi 7 / 802.11be : Multi-Link Operation (MLO)</text>
<rect x="45" y="145" width="190" height="110" rx="14" class="node green"/><text x="140" y="180" class="t">Client MLD</text><text x="140" y="204" class="s">Liens logiques associés</text><text x="140" y="225" class="small">Support dépend du terminal</text>
<rect x="665" y="145" width="190" height="110" rx="14" class="node blue"/><text x="760" y="180" class="t">AP MLD</text><text x="760" y="204" class="s">Radio / MAC par lien</text><text x="760" y="225" class="small">Configuration compatible</text>
<path d="M235 165 C360 95 540 95 665 165" class="line5"/><text x="450" y="94" class="s">Lien 5 GHz (exemple)</text>
<path d="M235 202 H665" class="line6"/><text x="450" y="192" class="s">Lien 6 GHz (exemple)</text>
<path d="M235 238 C360 310 540 310 665 238" class="pp"/><text x="450" y="306" class="s">Un ou plusieurs liens actifs selon STR / NSTR, radio et client</text>
<rect x="100" y="340" width="700" height="42" rx="10" class="node amber"/><text x="450" y="366" class="s">MLO ne garantit pas automatiquement le double du débit ni une latence constante.</text></svg></div>

**Règle de conception :** commencer par les problèmes opérationnels qui justifient une fonction. Si le problème est la congestion de petits paquets, il faut examiner airtime, OFDMA et le profil de clients. S’il s’agit de latence ou de continuité lors des déplacements, mesurer le roaming et étudier MLO seulement si les terminaux le prennent en charge. Si l’objectif est une capacité élevée pour quelques stations proches, des canaux larges et les fonctionnalités du Wi-Fi 7 peuvent être adaptés. Une génération plus récente ne remplace ni le plan RF ni le dimensionnement filaire.

## 4. Roaming : expérience applicative et mobilité

### 4.1. Qui décide du roaming ?

Dans une infrastructure Wi-Fi classique, le client garde une grande part de la décision de quitter un BSS et d’en choisir un autre. L’infrastructure peut fournir des informations voisines, une suggestion de transition ou un mécanisme d’authentification accélérée, mais le terminal choisit selon son pilote, son système d’exploitation, ses seuils, les caractéristiques reçues et l’application active. C’est pourquoi un même site peut présenter des résultats différents selon les modèles de téléphone ou d’ordinateur.

Un roaming peut être déclenché lorsque le signal se détériore, lorsqu’un autre AP offre une meilleure qualité ou pour d’autres raisons liées au client. Un appareil peut rester sur un AP peu optimal (« sticky client »), scanner longtemps, tenter un AP qui est moins performant dans le sens montant ou refaire une procédure de sécurité coûteuse. Le RSSI de l’AP visible n’explique pas seul le choix du terminal.

### 4.2. Rôles de 802.11k, 802.11v et 802.11r

- **802.11k — Radio Resource Measurement :** peut aider le client à identifier des AP voisins candidats, par exemple avec un Neighbor Report, et éviter un balayage exhaustif inutile.
- **802.11v — BSS Transition Management :** permet à l’infrastructure de suggérer des options de transition au client compatible. La suggestion n’équivaut pas à un ordre de déconnexion universel : le client garde un rôle déterminant.
- **802.11r — Fast BSS Transition (FT) :** prépare des éléments du mécanisme d’authentification et de clés afin de réduire la latence de changement de BSS dans les déploiements compatibles. Les modes over-the-air et over-the-distribution-system existent ; le fonctionnement exact dépend du WLAN, de la sécurité et du contrôleur.

Ces mécanismes se complètent mais ne sont pas interchangeables. Activer 802.11r ne corrige pas un trou RF ; activer 802.11k ne garantit pas le choix d’un AP optimal ; activer 802.11v ne garantit pas que le client suivra la suggestion. Chaque changement doit être validé avec la matrice de terminaux réels, notamment pour les appareils anciens ou IoT.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 440" width="100%" height="auto" role="img" aria-label="Séquence de roaming du client entre AP-A et AP-B, assistance 802.11k/v facultative, transition 802.11r si compatible et réassociation"><defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#63d8ff"/></marker><marker id="arrp" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#c4a4ff"/></marker></defs><style>.t{font:700 16px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.s{font:12.5px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.small{font:11px system-ui,sans-serif;fill:#b8c7d8;text-anchor:middle}.node{stroke-width:2;rx:12}.blue{fill:#14334a;stroke:#5ecbff}.green{fill:#153b2b;stroke:#73e3a2}.purple{fill:#2b2046;stroke:#c4a4ff}.amber{fill:#45331b;stroke:#ffc76b}.red{fill:#451f2a;stroke:#ff858c}.p{fill:none;stroke:#63d8ff;stroke-width:2.6;stroke-dasharray:8 7;marker-end:url(#arr);animation:dash 2.6s linear infinite}.pp{fill:none;stroke:#c4a4ff;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#arrp);animation:dash 3s linear infinite}@keyframes dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.p,.pp{animation:none}}.lane{stroke:#263d52;stroke-width:1.3;stroke-dasharray:4 5}.time{font:11px system-ui,sans-serif;fill:#aebed0}.em{font:700 13px system-ui,sans-serif;fill:#f3f7ff;text-anchor:middle}</style><rect x="14" y="12" width="872" height="416" rx="18" fill="#0b1220" stroke="#24384c"/><text x="450" y="39" class="t">Roaming : le client décide, le réseau peut l’aider</text>
<rect x="38" y="62" width="180" height="46" rx="10" class="node green"/><text x="128" y="90" class="em">Client (STA)</text>
<rect x="359" y="62" width="180" height="46" rx="10" class="node blue"/><text x="449" y="90" class="em">AP-A / ancien BSS</text>
<rect x="682" y="62" width="180" height="46" rx="10" class="node purple"/><text x="772" y="90" class="em">AP-B / nouveau BSS</text>
<path d="M128 108 V382 M449 108 V382 M772 108 V382" class="lane"/>
<path d="M128 145 H449" class="p"/><text x="288" y="134" class="s">Association active / trafic</text>
<path d="M449 194 H128" class="pp"/><text x="288" y="181" class="s">802.11k : rapport de voisins (si pris en charge)</text>
<path d="M128 242 H449" class="p"/><text x="288" y="230" class="s">802.11v : suggestion BSS Transition (facultative)</text>
<path d="M128 290 H772" class="p"/><text x="450" y="278" class="s">Sondage / authentification FT / réassociation selon le scénario</text>
<path d="M772 339 H128" class="pp"/><text x="450" y="327" class="s">Sécurité et distribution : échange dépendant du mode</text>
<rect x="245" y="365" width="410" height="36" rx="9" class="node amber"/><text x="450" y="387" class="s">Mesurer la coupure réelle sur l’application, pas seulement RSSI.</text></svg></div>

### 4.3. Mesurer le roaming correctement

La durée d’un roaming ne se résume pas toujours au délai entre la dernière trame reçue sur l’AP source et la première trame reçue sur l’AP cible. Le résultat dépend de la synchronisation des horloges, du point de capture, des trames perdues par le sniffer et du chemin de trafic. Il faut mesurer au moins :

1. Temps entre le début du déclin de service et la reprise du trafic applicatif.
2. Durée du scan et de sélection du candidat, si observable.
3. Durée d’authentification/réassociation ou FT.
4. Maintien de l’adresse IP, du VLAN/rôle et des états de sécurité.
5. Pertes UDP/RTP, gigue, trous audio/vidéo et temps de reprise des connexions TCP.

Un test voix doit être fait en marchant à vitesse réaliste, avec plusieurs terminaux, dans les deux directions et près des limites de cellule. Le résultat attendu doit être défini avec le responsable applicatif : une coupure réseau de 80 ms ne se traduit pas toujours par une conséquence audio identique selon le codec, la taille du jitter buffer et la nature du flux. Ne pas promettre une coupure universellement imperceptible à partir de l’activation d’une seule fonctionnalité.

### 4.4. Causes de roaming instable

Les problèmes fréquents comprennent une puissance des AP trop élevée, des cellules qui se chevauchent de manière excessive ou insuffisante, un client qui ne prend pas en charge les mécanismes attendus, un changement DFS, une différence de politique entre contrôleurs, des paramètres de sécurité incohérents, une réauthentification RADIUS lente, un VLAN/rôle différent après transition ou une mauvaise qualité du lien montant. La journalisation doit corréler les événements du contrôleur, du client, du RADIUS et de l’application. Si les horloges ne sont pas synchronisées, la chronologie devient difficile à établir.

## 5. Sécurité avancée et identité

### 5.1. Choisir le mode d’authentification selon le risque

Une PSK partagée est opérationnellement simple mais sa révocation est difficile si elle est diffusée à beaucoup d’utilisateurs. Un mot de passe commun n’offre pas la même traçabilité qu’une identité individuelle. WPA3-Personal utilise SAE plutôt qu’une simple réutilisation de la poignée de main PSK traditionnelle, mais la sécurité opérationnelle dépend toujours de la force du secret, des appareils et de la configuration.

WPA3-Enterprise s’appuie généralement sur 802.1X et un serveur d’authentification, avec des modes de sécurité dont le support dépend de l’équipement. EAP-TLS, avec certificats client et serveur, constitue une option forte lorsque l’organisation peut gérer la PKI, la distribution, l’expiration et la révocation des certificats. Les méthodes EAP avec identifiants utilisateur demandent un contrôle rigoureux du certificat serveur et du nom attendu afin d’éviter qu’un terminal accepte un serveur d’authentification frauduleux.

OWE (*Opportunistic Wireless Encryption*) peut chiffrer le lien radio d’un réseau ouvert compatible sans fournir à lui seul l’identité ou les autorisations d’un utilisateur. Un SSID invité ouvert avec OWE ne remplace donc ni la segmentation ni les règles de sortie Internet. Il faut distinguer le chiffrement du lien, l’authentification de l’identité et l’autorisation d’accéder à une ressource.

### 5.2. 802.1X/EAP/RADIUS : responsabilités distinctes

802.1X définit un cadre d’accès contrôlé au réseau. EAP transporte une méthode d’authentification ; l’AP ou le contrôleur agit généralement comme authenticator, tandis que le serveur RADIUS traite l’échange selon la méthode sélectionnée. Le serveur peut retourner des attributs d’autorisation qui déterminent un VLAN, un rôle, une ACL ou une durée de session selon l’implémentation.

L’accès peut échouer alors que le mot de passe est correct : certificat expiré, chaîne de confiance manquante, horloge client fausse, nom du serveur non reconnu, méthode EAP différente, transport RADIUS bloqué, secret partagé mal configuré, politique d’accès non satisfaite ou réponse AAA trop lente. Une capture radio limitée peut ne pas révéler tous les détails EAP, surtout avec les protections et le chiffrement ; combiner journaux du client, contrôleur et serveur RADIUS.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 445" width="100%" height="auto" role="img" aria-label="Chemin de contrôle d’un client Wi-Fi entreprise : authentification 802.1X EAP via AP contrôleur et serveur RADIUS, puis accès VLAN ou rôle selon la politique"><defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#63d8ff"/></marker><marker id="arrp" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#c4a4ff"/></marker></defs><style>.t{font:700 16px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.s{font:12.5px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.small{font:11px system-ui,sans-serif;fill:#b8c7d8;text-anchor:middle}.node{stroke-width:2;rx:12}.blue{fill:#14334a;stroke:#5ecbff}.green{fill:#153b2b;stroke:#73e3a2}.purple{fill:#2b2046;stroke:#c4a4ff}.amber{fill:#45331b;stroke:#ffc76b}.red{fill:#451f2a;stroke:#ff858c}.p{fill:none;stroke:#63d8ff;stroke-width:2.6;stroke-dasharray:8 7;marker-end:url(#arr);animation:dash 2.6s linear infinite}.pp{fill:none;stroke:#c4a4ff;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#arrp);animation:dash 3s linear infinite}@keyframes dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.p,.pp{animation:none}}.auth{fill:none;stroke:#c4a4ff;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#arrp)}.auth path{animation:dash 2.8s linear infinite}.info{font:12px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.em{font:700 13px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}</style><rect x="14" y="12" width="872" height="421" rx="18" fill="#0b1220" stroke="#24384c"/><text x="450" y="40" class="t">Accès entreprise : identité, autorisation et trafic sont distincts</text>
<rect x="40" y="102" width="170" height="78" rx="12" class="node green"/><text x="125" y="132" class="em">Client</text><text x="125" y="154" class="s">Supplicant EAP</text>
<rect x="270" y="102" width="170" height="78" rx="12" class="node blue"/><text x="355" y="132" class="em">Point d’accès</text><text x="355" y="154" class="s">Authenticator</text>
<rect x="500" y="102" width="170" height="78" rx="12" class="node purple"/><text x="585" y="132" class="em">RADIUS</text><text x="585" y="154" class="s">EAP / politique</text>
<rect x="725" y="102" width="135" height="78" rx="12" class="node amber"/><text x="792" y="132" class="em">AAA</text><text x="792" y="154" class="s">Identité / rôles</text>
<path d="M210 126 H270" class="p"/><text x="240" y="114" class="small">EAPOL</text><path d="M270 155 H210" class="pp"/>
<path d="M440 126 H500" class="pp"/><text x="470" y="114" class="small">RADIUS</text><path d="M500 155 H440" class="p"/>
<path d="M670 140 H725" class="pp"/><text x="697" y="126" class="small">Policy</text>
<path d="M355 180 V220 H320 V246" class="p"/><path d="M792 180 V220 H580 V246" class="pp"/>
<rect x="280" y="246" width="340" height="64" rx="12" class="node green"/><text x="450" y="272" class="em">Accès accordé selon la politique</text><text x="450" y="292" class="s">VLAN / rôle / ACL / durée de session</text>
<path d="M450 310 V344" class="p"/><rect x="180" y="344" width="540" height="52" rx="12" class="node blue"/><text x="450" y="366" class="em">Trafic utilisateur chiffré par le mode choisi</text><text x="450" y="384" class="s">WPA3-Enterprise, PMF et politique réseau à valider séparément</text></svg></div>

### 5.3. PMF, gestion des trames et protection

Protected Management Frames (PMF, associé à IEEE 802.11w et intégré aux exigences des générations de sécurité récentes selon le mode) protège certaines trames de gestion contre des attaques de falsification ou d’injection. Le niveau d’exigence dépend du type de sécurité et des règles de certification. L’activation de PMF doit être testée avec les équipements hérités et les appareils IoT : un paramètre imposé qui n’est pas supporté peut empêcher l’association de ces clients.

Il faut également distinguer la protection des trames de gestion des autres contrôles : chiffrement de données, segmentation VLAN/VRF, ACL, isolation des clients, contrôle des accès filaires, protection du plan de gestion, segmentation des invités et surveillance des AP non autorisés. PMF n’empêche pas le brouillage radio, et WPA3 ne remplace pas une politique de segmentation bien conçue.

### 5.4. Segmentation et moindre privilège

La segmentation devrait traduire les profils de risque en règles vérifiables. Exemples : un SSID invité a accès à Internet mais pas aux sous-réseaux privés ; un terminal IoT ne peut initier des connexions que vers ses serveurs nécessaires ; un terminal géré d’entreprise peut atteindre les applications métier via les contrôles prévus ; les outils d’administration utilisent un plan distinct et des comptes privilégiés protégés.

La segmentation dynamique peut affecter des rôles ou ACL selon l’identité et l’état de conformité, si l’infrastructure la supporte. Elle peut faciliter la gestion, mais augmente les exigences de cohérence entre RADIUS, contrôleur, switches, pare-feu et règles de secours. Toujours prévoir le comportement en cas d’échec AAA : autoriser, refuser ou placer dans un rôle limité. Le choix doit être explicite, documenté et testé ; il ne doit pas être laissé aux valeurs par défaut par accident.

### 5.5. Certificats : cycle de vie opérationnel

Une PKI pour le Wi-Fi d’entreprise nécessite des procédures pour :

- émettre et distribuer les certificats client et serveur ;
- mettre en confiance l’autorité de certification sur les terminaux gérés ;
- vérifier le nom attendu du serveur EAP ;
- définir la durée de vie et le renouvellement avant expiration ;
- révoquer ou retirer un terminal perdu, compromis ou sortant de l’organisation ;
- surveiller les expirations et incidents de validation de chaîne ;
- tester un renouvellement complet sur un échantillon de systèmes avant de le généraliser.

L’échec simultané de nombreux clients à une date peut être lié à un certificat serveur expiré, une chaîne modifiée ou un mécanisme de validation changé, plutôt qu’à un problème RF. Tout plan de déploiement doit coordonner l’équipe identité, les administrateurs de terminaux, le Wi-Fi et le support utilisateur.

## 6. QoS, voix et applications sensibles à la latence

### 6.1. QoS de bout en bout

La QoS doit rester cohérente du terminal à l’application distante : classification, marquage DSCP, confiance ou remarking aux frontières, mapping vers les User Priorities 802.11, catégories d’accès WMM, files d’attente des switches et du WAN, puis comportement des récepteurs. Un marquage élevé ne crée pas de capacité physique ; il détermine un traitement relatif dans les équipements qui le respectent.

Dans WMM, les catégories d’accès distinguent notamment Voice, Video, Best Effort et Background. Le médium reste partagé et soumis à la contention. La catégorie Voice peut obtenir des paramètres d’accès plus favorables, mais si plusieurs terminaux envoient trop de trafic prioritaire, la catégorie elle-même se congestionne. Les politiques doivent empêcher un terminal non fiable de marquer arbitrairement tout son trafic comme voix prioritaire.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 405" width="100%" height="auto" role="img" aria-label="Trajet QoS pour la voix sur Wi-Fi : marquage applicatif, mapping DSCP vers WMM, admission et airtime, puis validation de bout en bout"><defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#63d8ff"/></marker><marker id="arrp" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#c4a4ff"/></marker></defs><style>.t{font:700 16px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.s{font:12.5px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.small{font:11px system-ui,sans-serif;fill:#b8c7d8;text-anchor:middle}.node{stroke-width:2;rx:12}.blue{fill:#14334a;stroke:#5ecbff}.green{fill:#153b2b;stroke:#73e3a2}.purple{fill:#2b2046;stroke:#c4a4ff}.amber{fill:#45331b;stroke:#ffc76b}.red{fill:#451f2a;stroke:#ff858c}.p{fill:none;stroke:#63d8ff;stroke-width:2.6;stroke-dasharray:8 7;marker-end:url(#arr);animation:dash 2.6s linear infinite}.pp{fill:none;stroke:#c4a4ff;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#arrp);animation:dash 3s linear infinite}@keyframes dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.p,.pp{animation:none}}.step{fill:#122b3e;stroke:#63d8ff;stroke-width:2}.num{font:700 12px system-ui,sans-serif;fill:#63d8ff;text-anchor:middle}</style><rect x="14" y="12" width="872" height="381" rx="18" fill="#0b1220" stroke="#24384c"/><text x="450" y="41" class="t">QoS : une chaîne cohérente, pas un simple bouton « priorité »</text>
<rect x="28" y="116" width="145" height="92" rx="11" class="node green"/><text x="100" y="146" class="t">App voix</text><text x="100" y="169" class="s">DSCP / RTP</text><text x="100" y="188" class="small">latence sensible</text>
<rect x="205" y="116" width="145" height="92" rx="11" class="node blue"/><text x="277" y="146" class="t">LAN / switch</text><text x="277" y="169" class="s">trust / remark</text><text x="277" y="188" class="small">files d’attente</text>
<rect x="382" y="116" width="145" height="92" rx="11" class="node purple"/><text x="454" y="146" class="t">AP / WMM</text><text x="454" y="169" class="s">UP / AC_VO</text><text x="454" y="188" class="small">accès au média</text>
<rect x="559" y="116" width="145" height="92" rx="11" class="node amber"/><text x="631" y="146" class="t">Airtime RF</text><text x="631" y="169" class="s">contention / retry</text><text x="631" y="188" class="small">SNR, charge, DFS</text>
<rect x="736" y="116" width="138" height="92" rx="11" class="node green"/><text x="805" y="146" class="t">Récepteur</text><text x="805" y="169" class="s">jitter / pertes</text><text x="805" y="188" class="small">QoE mesurée</text>
<path d="M173 160 H205" class="p"/><path d="M350 160 H382" class="p"/><path d="M527 160 H559" class="p"/><path d="M704 160 H736" class="p"/>
<rect x="118" y="259" width="664" height="62" rx="12" class="node red"/><text x="450" y="284" class="t">Un marquage élevé ne crée pas de capacité RF</text><text x="450" y="305" class="s">Si l’airtime est saturé ou le mapping erroné, la voix peut encore subir jitter et pertes.</text></svg></div>

### 6.2. Mesurer latence, gigue et pertes

Une valeur moyenne de latence peut masquer des pointes ; mesurer les percentiles (p50, p95, p99) et corréler avec l’occupation de canal, le taux de retransmissions, le signal, les changements de canal et la charge du contrôleur. Pour un flux audio, une perte courte et groupée peut être plus perceptible que des pertes sporadiques de même pourcentage. La taille du jitter buffer et le codec affectent l’expérience, il faut donc inclure une mesure applicative.

Séparer les composantes du délai : attente d’accès au canal, airtime de transmission, retransmissions MAC, files d’attente AP, commutation/routage, pare-feu, WAN et délai serveur. Un test `ping` seul ne localise pas tout le problème ; il peut différer de l’application en protocole, priorisation, taille des paquets et itinéraire. Comparer un test filaire et un test Wi-Fi depuis la même zone aide à isoler le segment radio.

### 6.3. Multicast, découverte et IoT

La découverte locale d’appareils (par exemple certaines applications d’impression ou de diffusion) peut reposer sur mDNS, SSDP ou des groupes multicast. Le multicast n’est pas toujours transmis comme unicast et peut être affecté par l’économie d’énergie, le proxying, la conversion multicast-to-unicast ou les limites du contrôleur. Les optimisations doivent être testées avec les besoins applicatifs. Une option qui améliore le débit moyen peut casser une fonction de découverte, un flux IPTV ou une communication de groupe si le comportement n’est pas vérifié.

Les appareils IoT anciens peuvent nécessiter des bandes, largeurs de canal, méthodes de sécurité ou intervalles spécifiques. Ils peuvent tolérer mal le PMF obligatoire, WPA3 only, le 5 GHz/6 GHz, les canaux DFS ou le roaming accéléré. Prévoir un SSID ou une politique distincte seulement si l’inventaire, la gestion et l’isolation justifient le coût opérationnel. Éviter de maintenir un SSID hérité sans propriétaire ni date de retrait.

## 7. Capacité et dimensionnement expert

### 7.1. Partir des usages, pas du nombre d’AP

Le dimensionnement ne se résume pas à « une AP pour x mètres carrés ». La couverture et la capacité sont deux objectifs distincts. Une zone peut être couverte par une AP mais contenir trop de clients actifs ; à l’inverse, placer trop d’AP sur le même canal augmente la contention. L’AP est une ressource radio limitée, partagée par les clients d’un BSS et impactée par les BSS voisins.

La démarche doit estimer : nombre de clients totaux et actifs, distribution par zone, usages simultanés, débits utiles cibles, tailles et directions de flux, proportion de terminaux anciens, mobilité, spectre réellement disponible, options de largeur de canal, contraintes de câblage et puissance PoE. Le dimensionnement doit considérer les scénarios de pointe, pas seulement la moyenne journalière.

### 7.2. Exemple de calcul de capacité

Supposons une salle de formation comptant 120 participants, avec 90 terminaux qui transmettent activement pendant un exercice synchronisé. L’exigence métier est une expérience web interactive, non un débit soutenu de plusieurs centaines de mégabits par appareil. Le premier travail est de définir les transactions et la latence admissible, puis de réaliser un pilote avec le même type de clients et de contenu. Si chacun envoie de petites rafales, le nombre de contentions et l’overhead peuvent compter davantage que le débit maximal de chaque radio.

Dans une autre salle, 20 stations peuvent transférer de très gros fichiers depuis un serveur local. La largeur de canal, le nombre de flux spatiaux, le chemin Ethernet en amont et la capacité du serveur peuvent devenir plus importants. On doit concevoir en fonction des deux scénarios, plutôt qu’appliquer une seule densité d’AP à tout le bâtiment.

Le calcul préliminaire suivant aide à comparer des hypothèses, mais ne remplace pas une mesure :

\[
\text{Débit utile agrégé estimé} = \text{temps d'air utile} \times \text{débit utile pendant ce temps}
\]

Le « temps d’air utile » doit exclure au moins les phases de contention, le temps d’attente, les retransmissions, l’overhead de contrôle et les transmissions d’autres clients. Dans un réseau partagé, le temps d’air utile varie au fil des secondes et la capacité obtenue par un seul client peut différer de la capacité répartie équitablement entre de nombreux clients. Ne jamais transformer ce modèle de haut niveau en promesse commerciale sans pilote.

### 7.3. Surabonnement filaire et goulots d’étranglement

Une radio multi-gigabit connectée à un port Ethernet insuffisant peut devenir limitée par le câble en amont, surtout lorsque plusieurs radios sont agrégées. Vérifier la négociation de lien, la compatibilité multi-gigabit, le PoE disponible, la capacité de commutation, la bande passante des uplinks, les politiques QoS, les limites des tunnels et les performances du contrôleur ou pare-feu.

Surveiller les drops et erreurs de port, les files d’attente, les CPU, la perte de tunnel, les retransmissions TCP, les débits négociés et les erreurs de duplex ou de câblage. Le fait qu’un contrôleur rapporte une capacité radio très élevée ne prouve pas que le chemin applicatif peut la transporter. Tester de bout en bout depuis un serveur filaire connu, pas uniquement avec une application de speed test Internet.

### 7.4. Capacité résiduelle et panne

Un design expert évalue ce qu’il reste lorsque survient une panne : un AP hors service, une alimentation PoE perdue, un uplink coupé, un contrôleur indisponible, une bande perturbée ou plusieurs AP contraints à quitter un canal DFS. La question n’est pas uniquement « y a-t-il encore un signal ? », mais « le service répond-il encore aux critères en charge ? ».

Exemple de vérification : planifier une panne d’AP dans une zone dense et observer l’association des clients voisins, l’airtime, les débits utiles, la latence p95 et les appels en cours. Si les AP restants acceptent les associations mais saturent l’airtime, la résilience radio n’atteint pas l’objectif métier. Documenter les limites acceptables par service : un portail de consultation et une communication vocale ne nécessitent pas toujours le même critère de réussite.

## 8. Étude de site, plan de canaux et validation

### 8.1. Étude prédictive et étude sur site

Une étude prédictive est utile pour déterminer une implantation initiale, comparer des options d’antenne et identifier les zones à risque. Elle dépend de la qualité des plans, des matériaux, de la hauteur, du mobilier et des paramètres de puissance. Une étude passive mesure les AP et l’environnement radio vus par un outil ; une étude active teste une association et des échanges avec le réseau ; une analyse de spectre étudie les signaux dans les bandes observées, y compris les sources non-Wi-Fi selon l’appareil.

La validation post-déploiement doit être exécutée avec des terminaux proches de ceux utilisés au quotidien. Un adaptateur d’étude très performant peut surestimer l’expérience d’un smartphone bas de gamme ou d’un scanner. Inclure les trajets de roaming, les postes de travail, les zones de réunion, les ascenseurs si couverts, les entrepôts et les frontières entre cellules.

### 8.2. Définir des critères d’acceptation

Les critères doivent être écrits avant le test. Par exemple :

- couverture bidirectionnelle suffisante sur les zones de travail ;
- seuils RSSI/SNR et taux de retransmissions définis par application et validés sur matériel réel ;
- durée maximale de perte de trafic durant le roaming de la voix ;
- réussite d’authentification et attribution correcte du rôle ;
- obtention d’une adresse IP, résolution DNS et accès aux applications attendues ;
- latence, gigue, pertes et débit utile mesurés dans la période représentative ;
- fonctionnement en cas de panne d’AP, d’uplink ou de dépendance AAA ;
- preuve de conformité aux contraintes réglementaires et de sécurité.

Les valeurs concrètes doivent venir du besoin, du matériel, du profil d’application et du cadre local. Une valeur RSSI générique de cours n’est pas suffisante pour accepter un réseau de voix, un réseau de collecte de données industrielles ou un WLAN d’invités.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 395" width="100%" height="auto" role="img" aria-label="Cycle de conception expert WLAN : exigences, prédiction, survey, pilote, validation post-déploiement, mesure et boucle d’amélioration"><defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#63d8ff"/></marker><marker id="arrp" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#c4a4ff"/></marker></defs><style>.t{font:700 16px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.s{font:12.5px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.small{font:11px system-ui,sans-serif;fill:#b8c7d8;text-anchor:middle}.node{stroke-width:2;rx:12}.blue{fill:#14334a;stroke:#5ecbff}.green{fill:#153b2b;stroke:#73e3a2}.purple{fill:#2b2046;stroke:#c4a4ff}.amber{fill:#45331b;stroke:#ffc76b}.red{fill:#451f2a;stroke:#ff858c}.p{fill:none;stroke:#63d8ff;stroke-width:2.6;stroke-dasharray:8 7;marker-end:url(#arr);animation:dash 2.6s linear infinite}.pp{fill:none;stroke:#c4a4ff;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#arrp);animation:dash 3s linear infinite}@keyframes dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.p,.pp{animation:none}}.phase{fill:#132536;stroke:#63d8ff;stroke-width:2}.n{font:700 12px system-ui,sans-serif;fill:#63d8ff;text-anchor:middle}.st{font:700 13px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.cap{font:11px system-ui,sans-serif;fill:#c1cedd;text-anchor:middle}</style><rect x="14" y="12" width="872" height="371" rx="18" fill="#0b1220" stroke="#24384c"/><text x="450" y="40" class="t">Cycle de vie : concevoir, mesurer, valider, puis ajuster</text>
<rect x="35" y="95" width="180" height="84" rx="12" class="phase"/><text x="125" y="121" class="n">01</text><text x="125" y="143" class="st">Exigences</text><text x="125" y="162" class="cap">capacité / voix / sécurité</text>
<rect x="253" y="95" width="180" height="84" rx="12" class="node purple"/><text x="343" y="121" class="n">02</text><text x="343" y="143" class="st">Prédiction RF</text><text x="343" y="162" class="cap">plans / matériaux / AP</text>
<rect x="471" y="95" width="180" height="84" rx="12" class="node green"/><text x="561" y="121" class="n">03</text><text x="561" y="143" class="st">Survey / pilote</text><text x="561" y="162" class="cap">mesures terrain</text>
<rect x="689" y="95" width="176" height="84" rx="12" class="node amber"/><text x="777" y="121" class="n">04</text><text x="777" y="143" class="st">Acceptation</text><text x="777" y="162" class="cap">tests reproductibles</text>
<path d="M215 137 H253" class="p"/><path d="M433 137 H471" class="p"/><path d="M651 137 H689" class="p"/>
<path d="M777 179 V238 H561 V263" class="pp"/><rect x="411" y="263" width="300" height="54" rx="12" class="node blue"/><text x="561" y="286" class="st">Mesures en production</text><text x="561" y="304" class="cap">client réel, airtime, incidents</text>
<path d="M411 289 H125 V179" class="pp"/><text x="265" y="278" class="small">boucle d’amélioration</text>
<text x="450" y="351" class="s">Toute modification RF doit être liée à une hypothèse, un test et un retour arrière.</text></svg></div>

### 8.3. Préparer la matrice de test

Pour chaque test, consigner : identifiant, zone, date et heure, terminal/OS/pilote, SSID, bande/canal, AP source/cible, profil de sécurité, version firmware, charge estimée, actions exactes, mesures, résultat attendu, résultat constaté, capture/log associé et responsable. Sans cela, un résultat « ça marche » n’est pas reproductible.

Une bonne matrice inclut les cas positifs et négatifs. Exemple : un employé géré reçoit le rôle attendu ; un invité ne peut pas joindre les sous-réseaux privés ; un certificat expiré échoue proprement ; le terminal reprend le trafic après roaming ; la perte d’un serveur RADIUS produit le comportement de secours défini ; un client hérité est évalué sur le SSID qui lui est destiné. Le résultat négatif est aussi important que le résultat positif pour confirmer que les règles de sécurité sont appliquées.

## 9. Dépannage à partir des preuves

### 9.1. Ordre de diagnostic

Quand un utilisateur signale une lenteur, commencer par préciser la portée : un seul client ou plusieurs, une zone ou tout le site, un SSID ou tous, une application ou tout le trafic, un horaire spécifique ou permanent. Puis vérifier la chaîne dans l’ordre : présence/association radio, authentification, sécurité, VLAN/rôle, DHCP, passerelle, DNS, routage, pare-feu, application. Cette séquence évite de modifier le RF quand la cause est un bail DHCP ou une règle réseau.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 430" width="100%" height="auto" role="img" aria-label="Arbre de diagnostic Wi-Fi : distinguer association, authentification, DHCP, DNS, passerelle, accès applicatif et problème radio avec observations vérifiables"><defs><marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#63d8ff"/></marker><marker id="arrp" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#c4a4ff"/></marker></defs><style>.t{font:700 16px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.s{font:12.5px system-ui,sans-serif;fill:#c0ccdc;text-anchor:middle}.small{font:11px system-ui,sans-serif;fill:#b8c7d8;text-anchor:middle}.node{stroke-width:2;rx:12}.blue{fill:#14334a;stroke:#5ecbff}.green{fill:#153b2b;stroke:#73e3a2}.purple{fill:#2b2046;stroke:#c4a4ff}.amber{fill:#45331b;stroke:#ffc76b}.red{fill:#451f2a;stroke:#ff858c}.p{fill:none;stroke:#63d8ff;stroke-width:2.6;stroke-dasharray:8 7;marker-end:url(#arr);animation:dash 2.6s linear infinite}.pp{fill:none;stroke:#c4a4ff;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#arrp);animation:dash 3s linear infinite}@keyframes dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.p,.pp{animation:none}}.q{fill:#132536;stroke:#63d8ff;stroke-width:2}.leaf{fill:#153b2b;stroke:#73e3a2;stroke-width:2}.warn{fill:#45331b;stroke:#ffc76b;stroke-width:2}.tx{font:700 13px system-ui,sans-serif;fill:#f2f7ff;text-anchor:middle}.sub{font:11px system-ui,sans-serif;fill:#c1cedd;text-anchor:middle}</style><rect x="14" y="12" width="872" height="406" rx="18" fill="#0b1220" stroke="#24384c"/><text x="450" y="40" class="t">Diagnostic : suivre la chaîne d’accès, puis mesurer le RF</text>
<rect x="315" y="62" width="270" height="45" rx="10" class="node blue"/><text x="450" y="90" class="tx">Le client est-il associé ?</text>
<path d="M450 107 V130 H220 V148" class="p"/><path d="M450 107 V130 H680 V148" class="p"/><text x="318" y="124" class="small">NON</text><text x="585" y="124" class="small">OUI</text>
<rect x="95" y="148" width="250" height="54" rx="10" class="warn"/><text x="220" y="171" class="tx">Radio / SSID / sécurité</text><text x="220" y="188" class="sub">scan, RSSI/SNR, auth frames</text>
<rect x="555" y="148" width="250" height="54" rx="10" class="node blue"/><text x="680" y="171" class="tx">IP et passerelle disponibles ?</text><text x="680" y="188" class="sub">DHCP, VLAN, relay, ARP/ND</text>
<path d="M680 202 V222 H460 V240" class="p"/><text x="588" y="219" class="small">OUI</text>
<rect x="330" y="240" width="260" height="54" rx="10" class="node purple"/><text x="460" y="263" class="tx">DNS et application fonctionnent ?</text><text x="460" y="280" class="sub">résolution, route, TLS, service</text>
<path d="M460 294 V315" class="p"/><rect x="280" y="315" width="360" height="54" rx="10" class="leaf"/><text x="460" y="338" class="tx">Comparer client, AP et réseau filaire</text><text x="460" y="355" class="sub">capture synchronisée + compteurs + test témoin</text>
<rect x="46" y="240" width="220" height="54" rx="10" class="warn"/><text x="156" y="263" class="tx">Mesurer airtime / retry</text><text x="156" y="280" class="sub">pas RSSI seul</text><path d="M345 175 H266 V240" class="pp"/></svg></div>

### 9.2. Symptôme : association réussie, pas d’adresse IP

Hypothèses : serveur DHCP injoignable, scope épuisé, relay mal configuré, VLAN incorrect, tunnel de données cassé, politique RADIUS attribuant un rôle inattendu ou filtrage au niveau d’un switch. Collecter les logs DHCP, la capture des échanges Discover/Offer/Request/Ack, le VLAN/role appliqué et les événements du contrôleur. Si un autre client filaire du même VLAN reçoit un bail, comparer le chemin réel du trafic Wi-Fi plutôt que conclure immédiatement que le scope DHCP est sain dans tous les cas.

### 9.3. Symptôme : connexion lente mais RSSI fort

Causes possibles : airtime élevé, CCI, interférence non-Wi-Fi, client lent, mauvais canal/largeur, retransmissions, économie d’énergie, uplink congestionné, QoS incorrecte ou serveur distant lent. Les mesures utiles comprennent l’occupation de canal, les taux de retry, le MCS/NSS, les débits utiles, la latence et la gigue par application, les erreurs de port et la comparaison avec un test filaire dans la même période.

Ne pas changer le canal, la largeur, la puissance et la QoS simultanément. Modifier un paramètre, maintenir le scénario aussi constant que possible, mesurer puis décider. Si plusieurs variables changent en même temps, une amélioration observée ne permet pas de savoir quelle modification est responsable et ne peut pas être extrapolée de manière fiable.

### 9.4. Symptôme : roaming interrompant un appel

Collecter les traces client et AP, la séquence de déauthentification/désassociation, les trames d’authentification et de réassociation, les journaux 802.11r/k/v et RADIUS si impliqué. Mesurer la durée du trou applicatif et vérifier l’identité de la cible, la politique de sécurité et la conservation du rôle. Si le client ne supporte pas FT ou suit des critères propriétaires, ajuster le plan d’essai, pas seulement le contrôleur.

### 9.5. Symptôme : seuls certains modèles échouent

Comparer capacités de bandes, DFS, largeurs de canal, WPA3/PMF, méthode EAP, version pilote, économie d’énergie, MLO, 802.11r et les fonctionnalités optionnelles activées. Un client peut annoncer une capacité mais avoir une implémentation qui pose problème avec un firmware précis. Isoler un SSID pilote ou un sous-ensemble d’AP peut aider à tester une hypothèse, mais les exceptions permanentes doivent avoir un propriétaire, une justification de sécurité et une date de réévaluation.

### 9.6. Trames utiles dans une capture 802.11

Les captures peuvent montrer les Beacon et Probe frames, Authentication, Association/Reassociation, les réponses, les trames EAPOL, les ACK/Block ACK, les retransmissions radio observées par le sniffer, les événements de roaming et certaines trames de contrôle. Une capture incomplète ne permet pas de prouver qu’une trame n’a pas été envoyée : le sniffer peut être sur un autre canal, manquer des paquets, ne pas prendre en charge la largeur ou l’encodage utilisé, ou être trop éloigné.

Le mode monitor et les adaptateurs de capture ont des limites différentes de celles d’un client. Pour capturer le roaming, la capture sur un seul canal peut rater des trames sur le canal cible. Une capture multi-radio ou plusieurs sondes synchronisées peut être nécessaire. La synchronisation NTP, la précision des horloges, la perte de capture et l’emplacement du capteur doivent être notés dans le rapport.

Pour examiner les données chiffrées, respecter les droits d’accès et les règles de protection des données. Les secrets de session ou journaux d’authentification ne doivent pas être partagés librement. Le chiffrement ne cache pas nécessairement toutes les métadonnées ; une capture reste un artefact sensible qui peut révéler des identifiants, des adresses, des habitudes de déplacement et le détail du réseau.

### 9.7. Métriques et corrélation

Ne pas surveiller le RSSI seul. Une supervision utile combine : clients associés/actifs, taux de réussite d’association, temps d’authentification, latence RADIUS, succès DHCP, utilisation d’airtime, noise floor, retries, MCS, nombre de stations par radio, occupation des canaux, changements DFS, événements de roaming, pertes et gigue applicative, disponibilité AP/contrôleur, erreurs filaires et capacité PoE.

Les métriques doivent conserver une granularité compatible avec les incidents courts. Une moyenne sur quinze minutes peut masquer une pointe de deux secondes qui interrompt une conversation. Corréler par horodatage les événements radio, AAA, DHCP, pare-feu et application. Définir des alertes à partir d’une ligne de base et du niveau de service, en limitant les alertes redondantes ou qui n’entraînent aucune action.

## 10. Opérations, changements et automatisation

### 10.1. Gérer les changements RF comme des modifications de production

Un changement de puissance ou de canal touche potentiellement des dizaines de clients et voisins ; ce n’est pas une opération purement locale. Toute modification doit comprendre un motif, les AP et radios concernés, l’impact prévu, les mesures de base, les tests, les risques, la fenêtre, les critères d’arrêt et le retour arrière. Les changements RF automatiques sont eux aussi des changements : il faut connaître leur comportement, surveiller leurs décisions et comprendre s’ils peuvent déplacer de nombreux clients simultanément.

Une procédure de changement devrait limiter la portée initiale à une petite zone, puis étendre si le résultat est stable. Il faut éviter de mener simultanément une mise à jour du contrôleur, une modification de sécurité et une refonte du plan radio. La multiplication des changements empêche d’attribuer correctement la cause à un résultat et augmente le temps de restauration si quelque chose se passe mal.

### 10.2. Standardiser les profils

Créer des profils de SSID explicites : entreprise gérée, invités, IoT ou voix lorsque ces besoins existent réellement. Chaque profil doit préciser la méthode de sécurité, PMF, bandes permises, méthodes EAP, rôles, VLAN/ACL, options de roaming, politique de multicast, QoS, comportement en cas de panne AAA, limites de durée de session et propriétaire métier. Un SSID supplémentaire consomme du temps d’antenne pour ses balises et accroît la complexité ; ne pas en créer sans besoin justifié.

Les profils de radio doivent documenter largeur de canal, canaux admissibles, DFS, puissance minimale/maximale, restrictions par modèle, politique de réutilisation et comportement de l’optimisation automatique. Le réglage doit être versionné et comparé aux lignes de base. Les noms de paramètres ne sont pas toujours identiques selon le constructeur : utiliser une abstraction de configuration interne, puis valider la transformation vers chaque plateforme.

### 10.3. Automatiser les contrôles, pas les suppositions

Une automatisation peut détecter une AP avec une version inattendue, une radio désactivée, un SSID manquant, un certificat expirant, un changement de canal inhabituel, un taux d’échec d’authentification anormal ou une hausse de retries. Elle doit distinguer une alerte informative d’une action corrective automatique. Par exemple, un système qui change le canal dès qu’il voit une hausse d’occupation peut créer de l’instabilité s’il ne tient pas compte des voisins et de la nature du trafic.

Un flux fiable est : collecter l’état réel, valider les préconditions, calculer la différence, présenter l’impact, approuver le changement, appliquer à petite échelle, vérifier les métriques et annuler si les seuils se dégradent. L’automatisation doit être idempotente : exécuter à nouveau le même plan lorsque la cible est déjà conforme ne doit pas produire des modifications inutiles. Conserver le résultat de chaque action et le lien vers la version de configuration.

### 10.4. Sauvegarde, conformité et secrets

Sauvegarder les configurations du contrôleur, des AP, des switches et des profils AAA. Garder les secrets RADIUS et clés dans un coffre ou un mécanisme de secret approprié, non dans des scripts ou dépôts non protégés. Les exports doivent être contrôlés afin d’éviter d’inclure les identifiants personnels, PSK ou clés de session dans les rapports diffusés.

Une revue de conformité vérifie les AP inconnus, les SSID obsolètes, la sécurité réelle vs la politique, l’utilisation des VLAN attendus, la gestion des certificats, les comptes administrateurs, les versions logicielles, la séparation invités/entreprise et la capacité du réseau en mode dégradé. Les exceptions documentées devraient avoir une date d’expiration et un responsable.

## 11. Ateliers pratiques

Les ateliers se réalisent sur un laboratoire autorisé ou une infrastructure de test. Ne pas tester le brouillage, la désauthentification ou des attaques sur des réseaux sans autorisation explicite. Une analyse passive et des tests de configuration peuvent être menés sans perturber de tiers.

### Atelier A — Réseau dense lent malgré une couverture forte

**Situation :** les utilisateurs d’une salle de réunion signalent des lenteurs à midi. Le contrôleur rapporte un RSSI moyen élevé, mais l’occupation de canal et les retries augmentent à l’heure concernée. Un test filaire vers le même serveur reste stable.

**Démarche attendue :**

1. Préciser l’heure et les zones ; comparer plusieurs clients et générations.
2. Collecter la charge par radio, canaux, largeur, RSSI/SNR, retries, taux MCS et latence applicative.
3. Examiner la réutilisation de canaux et les signaux voisins ; vérifier si les radios co-canal se surchargent.
4. Tester à titre contrôlé un canal/largeur ou une redistribution de puissance dans un périmètre pilote.
5. Rejouer exactement le même scénario et comparer la latence p95, pertes et débit utile.

**Corrigé indicatif :** les indices orientent vers une contention ou des retransmissions plutôt que vers une simple faiblesse du signal. Le diagnostic n’est confirmé qu’après une mesure liée à une hypothèse. La première action n’est pas nécessairement d’ajouter des AP ni d’élargir les canaux.

### Atelier B — Coupure de voix pendant le déplacement

**Situation :** les appels se coupent lors du passage entre deux zones. La carte de couverture paraît correcte. Les logs montrent plusieurs événements de réassociation et une authentification prolongée pour certains clients.

**Démarche attendue :**

1. Enregistrer un appel test et se déplacer selon un trajet reproductible.
2. Capturer les deux côtés de la frontière radio ou utiliser plusieurs sondes synchronisées.
3. Identifier le BSSID source et cible, la durée de scan, la méthode de transition et les erreurs EAP/RADIUS.
4. Comparer 802.11k/v/r et les capacités réelles de chacun des terminaux.
5. Mesurer la perte de paquets applicatifs et vérifier l’absence de changement inattendu de VLAN, rôle ou adresse IP.

**Corrigé indicatif :** une couverture suffisante ne prouve pas un roaming fluide. Un délai AAA ou une incompatibilité FT peut étendre le trou de trafic. Le réglage proposé doit passer un test de compatibilité et conserver une méthode de retour arrière.

### Atelier C — Migration vers Wi-Fi 7 et 6 GHz

**Situation :** une organisation veut remplacer ses AP avant de définir les besoins. Les utilisateurs attendent un débit « plusieurs fois plus rapide » partout. Les terminaux existants sont hétérogènes, et certaines zones sont très denses.

**Démarche attendue :**

1. Inventorier clients, applications, bande, nombre de chaînes, support MLO et sécurité.
2. Identifier les cas d’usage qui requièrent davantage de débit, meilleure latence ou plus grande capacité.
3. Confirmer les canaux et la puissance légalement disponibles dans le pays.
4. Comparer largeur de canal et réutilisation spatiale selon le nombre de clients par zone.
5. Piloter avec des clients représentatifs et tester débit utile, latence, roaming, sécurité et mode dégradé.

**Corrigé indicatif :** Wi-Fi 7 apporte des capacités nouvelles mais ne transforme pas automatiquement l’expérience des terminaux hérités. Un plan mixte peut être préférable, selon les besoins et les coûts. La validation comprend aussi le réseau filaire, PoE, contrôle, sécurité et opérations.

### Atelier D — Échec WPA3-Enterprise sur un sous-ensemble d’appareils

**Situation :** après l’activation d’une politique de certificat plus stricte, certains terminaux ne s’associent plus, alors que les autres fonctionnent normalement.

**Démarche attendue :** vérifier la chaîne CA, le nom attendu du serveur EAP, la date/heure, le certificat client, la méthode EAP, la version OS/pilote et les logs RADIUS. Comparer un appareil sain et un appareil défaillant avec les mêmes paramètres radio, sans affaiblir la validation du certificat en production comme « solution ».

**Corrigé indicatif :** l’authentification est une hypothèse de premier plan ; un RSSI similaire et l’échec sur plusieurs AP renforcent cette piste. Corriger la distribution ou la confiance du certificat, ou traiter proprement le profil hérité. Ne jamais conseiller aux utilisateurs de désactiver la vérification du certificat serveur.

## 12. Liste de contrôle de conception et d’exploitation

### Avant déploiement

- [ ] Exigences métier mesurables et scénarios de pointe définis.
- [ ] Inventaire des clients, bandes, sécurité, roaming et contraintes IoT établi.
- [ ] Domaine réglementaire, canaux autorisés, DFS et règles 6 GHz vérifiés.
- [ ] Étude prédictive documentée puis affinée par une étude terrain.
- [ ] Plan de canaux, puissance, largeurs et réutilisation justifiés.
- [ ] Chemins données, contrôleur, DHCP/DNS, RADIUS, pare-feu et routage documentés.
- [ ] Segmentation, certificats, PMF et politique de secours AAA testés.
- [ ] Uplinks, PoE, commutation et capacité de contrôleur vérifiés.

### Avant d’accepter le site

- [ ] Couverture mesurée avec les clients représentatifs.
- [ ] Débit utile, latence, gigue et pertes mesurés à l’heure de pointe.
- [ ] Authentification, attribution VLAN/rôle, DHCP, DNS et accès aux services validés.
- [ ] Roaming testé sur les parcours réels et pour les applications sensibles.
- [ ] Les clients hérités ont un comportement défini et documenté.
- [ ] Les critères de panne AP/uplink/contrôleur/RADIUS ont été testés.
- [ ] Les résultats, captures, versions et anomalies sont conservés.

### En production

- [ ] Baseline et alertes couvrent airtime, retry, auth, DHCP, roaming et application.
- [ ] Modifications RF et sécurité passent par un changement versionné.
- [ ] Procédure de retour arrière et contacts d’escalade à jour.
- [ ] Sauvegardes testées et secrets protégés.
- [ ] Exceptions, SSID hérités et certificats ont un propriétaire et une échéance.
- [ ] Les incidents récurrents alimentent un plan d’amélioration mesuré.

## 13. Quiz expert

**1. Pourquoi le RSSI ne suffit-il pas à diagnostiquer un réseau lent ?**  
Il décrit la puissance reçue, mais pas à lui seul la contention, l’occupation du canal, les interférences, la symétrie, les retransmissions ou les performances applicatives.

**2. Dans quel cas 20 MHz peut-il fournir une meilleure capacité agrégée que 80 MHz ?**  
Dans un environnement dense où le spectre disponible et la réutilisation des canaux comptent plus que le débit de pointe d’un seul terminal.

**3. Que fait 802.11k par rapport à 802.11v ?**  
802.11k peut fournir des informations sur les voisins radio ; 802.11v permet notamment de suggérer une transition. Ni l’un ni l’autre ne garantit que le client suit la recommandation.

**4. Pourquoi 802.11r peut-il réduire le délai de roaming ?**  
Il prépare une partie des échanges de transition et de la dérivation de clés avant le changement de BSS, si le client et l’infrastructure prennent en charge le scénario.

**5. Pourquoi WPA3 ne suffit-il pas à sécuriser tout le réseau ?**  
Il protège le lien selon le mode et la configuration, mais ne remplace pas l’identité, l’autorisation, la segmentation, la gestion des certificats ni les contrôles du réseau filaire.

**6. Que faut-il surveiller lors d’un déploiement Wi-Fi 7 ?**  
Les capacités client et AP, MLO, disponibilité réglementaire des canaux, qualité RF, réutilisation de spectre, réseau filaire/PoE, sécurité et performances mesurées sur les applications.

**7. Comment prouver que le roaming est satisfaisant ?**  
Par un trajet reproductible avec des clients réels et une mesure du trou de trafic applicatif, des trames de transition, de la latence et des pertes, pas seulement par l’affichage d’un nouveau BSSID.

**8. Pourquoi une capture peut-elle ne pas contenir une trame attendue ?**  
Le sniffer peut être sur un autre canal, perdre des paquets, mal décoder une largeur/modulation ou être trop éloigné. Absence dans une capture ne prouve pas toujours absence sur le réseau.

**9. Quel est l’intérêt d’un test filaire témoin ?**  
Il aide à déterminer si le ralentissement est spécifique au segment radio ou se produit aussi sur le chemin filaire, à condition de comparer le même serveur et la même période.

**10. Pourquoi ne pas activer tous les paramètres avancés par défaut ?**  
Chaque fonction a des prérequis et des compromis. Le support du client, la densité, la sécurité, le spectre et le comportement du logiciel doivent justifier l’activation.

## 14. Glossaire

- **AP (Access Point)** : point d’accès Wi-Fi.
- **Airtime** : temps pendant lequel le médium radio est occupé.
- **BSS / BSSID** : ensemble de service de base / identifiant radio généralement associé à une adresse MAC de BSS.
- **CCI / ACI** : co-channel interference / adjacent-channel interference.
- **DFS** : Dynamic Frequency Selection, mécanisme réglementaire de sélection dynamique de fréquence dans certaines bandes.
- **EAP / RADIUS / 802.1X** : cadre d’authentification et de transport de politiques.
- **EIRP** : puissance isotrope rayonnée équivalente.
- **FT (802.11r)** : Fast BSS Transition.
- **MCS / NSS** : modulation and coding scheme / nombre de flux spatiaux.
- **MLO / MLD** : Multi-Link Operation / Multi-Link Device, notions introduites par Wi-Fi 7.
- **OFDMA / RU** : partage coordonné de ressources fréquentielles / Resource Unit.
- **PMF** : Protected Management Frames.
- **RSSI / SNR** : indicateur de puissance reçue / rapport signal-bruit.
- **TWT** : Target Wake Time.
- **WMM / DSCP** : Wi-Fi Multimedia / champ de différenciation des services IP utilisé pour la QoS.

## 15. Références techniques

Les normes définissent le comportement du protocole ; les guides de constructeur décrivent des profils de mise en œuvre. Les détails opérationnels doivent être vérifiés pour le matériel, le logiciel et le domaine réglementaire réellement déployés.

- [IEEE 802.11 Working Group — normes et publications](https://www.ieee802.org/11/)
- [IEEE 802.11be-2024 — statut de publication](https://www.ieee802.org/11/)
- [Cisco — Guide de conception des grands réseaux Wi-Fi publics](https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/222000-design-guide-cx-wireless-for-large-pub.html)
- [Cisco Meraki — Guide technique Wi-Fi 6 / 802.11ax](https://documentation.meraki.com/Wireless/Design_and_Configure/Architecture_and_Best_Practices/Wi-Fi_6_%28802.11ax%29_Technical_Guide)
- [Cisco — 802.11r Fast Transition](https://www.cisco.com/c/en/us/td/docs/wireless/controller/technotes/80211r-ft/b-80211r-dg.html)
- [Cisco — Migration vers 6 GHz et Wi-Fi 7](https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/223061-migrate-to-wi-fi-7-and-6ghz.html)
- [Android Open Source Project — Wi-Fi 7 et MLO](https://source.android.com/docs/core/connect/wifi-7)
- [Juniper Mist — principes Wi-Fi 7](https://www.juniper.net/documentation/us/en/software/mist/wi-fi-7-guide/wi-fi-7/topics/concept/how-wi-fi-7-works.html)
- [Wi-Fi Alliance — programmes de certification](https://www.wi-fi.org/discover-wi-fi)

---

**Principe à retenir :** concevoir à partir des besoins, mesurer l’airtime et la qualité applicative, appliquer la sécurité par identité et moindre privilège, et ne considérer une optimisation terminée qu’après un test reproductible.
