# IDS / IPS et DPI — Débutant

**Niveau :** DÉBUTANT

Un réseau doit transporter les communications nécessaires au travail tout en limitant les comportements malveillants. Un pare-feu applique surtout une politique de circulation : il décide quels flux peuvent franchir une frontière. Les technologies IDS, IPS et DPI complètent ce rôle en observant ou en inspectant le trafic afin de repérer des activités suspectes, des protocoles inattendus, des tentatives d’exploitation et certains signes de compromission.

Ce cours explique les concepts depuis les bases, puis les met en pratique dans un laboratoire maîtrisé. Il distingue l’observation, la détection, l’alerte et le blocage : ce sont des actions différentes qui n’ont ni les mêmes risques ni les mêmes exigences opérationnelles. Les exemples sont conçus pour l’apprentissage défensif sur des équipements et des systèmes que l’on est autorisé à administrer.

À la fin du cours, l’apprenant doit pouvoir expliquer la différence entre un IDS et un IPS, décrire le rôle du DPI, comprendre ce qu’un capteur peut réellement voir, lire une alerte élémentaire, reconnaître un faux positif et commencer une investigation sans interrompre inutilement les communications légitimes.

> **Analogie** : Un IDS ressemble à une caméra et à un agent qui signalent un comportement inhabituel. Un IPS ressemble à un agent de sécurité placé à l’entrée, capable de refuser le passage selon des règles. Le DPI est la capacité d’examiner plus précisément ce qui transite, comme vérifier le contenu d’un colis plutôt que de regarder seulement son étiquette. Dans la pratique, les produits combinent souvent plusieurs de ces fonctions.

---

## 1. La théorie et les algorithmes

### 1.1 Comprendre le problème à résoudre

Un réseau transporte des paquets. Chaque paquet possède des informations de contrôle — par exemple les adresses IP, le protocole et parfois les ports TCP ou UDP — ainsi que des données. Un équipement de filtrage peut décider sur la base des adresses et des ports, mais ces informations ne suffisent pas toujours à reconnaître une tentative d’exploitation ou un usage abusif d’une application autorisée.

Supposons qu’une entreprise autorise les connexions HTTPS vers son portail. Une règle de pare-feu peut autoriser TCP vers le port 443. Cette règle ne prouve pas que chaque requête HTTP reçue est légitime : une session autorisée peut transporter des requêtes malformées, automatisées ou conçues pour abuser d’une application vulnérable. C’est l’un des problèmes que les technologies d’inspection peuvent aider à identifier.

Un IDS/IPS ne remplace toutefois ni un développement applicatif sécurisé, ni la gestion des correctifs, ni le contrôle d’accès, ni les sauvegardes, ni la réponse aux incidents. Il ajoute une couche de visibilité et, dans le cas de l’IPS, une possibilité de prévention. Une alerte est un indice à vérifier, pas une preuve automatique qu’un système est compromis.

### 1.2 IDS : Intrusion Detection System

Un système de détection d’intrusion (**IDS**) observe des événements réseau ou système et signale ceux qui correspondent à une règle, à une anomalie ou à un comportement suspect. Il peut analyser le trafic d’un segment réseau, les journaux d’un serveur, les appels système d’un poste ou des métadonnées issues d’autres outils.

Un IDS réseau (*NIDS*) est souvent connecté à un port miroir du commutateur, à un TAP réseau ou à une source de trafic équivalente. Le capteur reçoit une copie du trafic. Dans une architecture passive classique, les paquets originaux continuent leur route sans traverser le capteur. Si le capteur s’arrête, il peut y avoir une perte de visibilité, mais il ne coupe normalement pas le trafic de production.

Un IDS hôte (*HIDS*) s’exécute sur un serveur ou un poste. Selon le produit, il peut inspecter des journaux, l’intégrité de fichiers, les processus, les connexions, les événements de sécurité ou les comportements de l’ordinateur. Il est utile pour observer ce qu’un capteur réseau ne peut pas voir, notamment certaines activités qui se déroulent entièrement sur l’hôte.

**Ce qu’un IDS fait bien :** alerter sans nécessairement changer le trajet des paquets, conserver des indices pour investigation, mesurer les tendances et aider à comprendre des comportements anormaux.

**Ce qu’un IDS ne garantit pas :** qu’une attaque sera détectée à coup sûr, qu’une alerte est toujours exacte, ni qu’il bloquera une activité malveillante. La qualité dépend du placement, de la couverture, des règles, des mises à jour, de la capacité du capteur et de la qualité des données observées.

### 1.3 IPS : Intrusion Prevention System

Un système de prévention d’intrusion (**IPS**) inspecte le trafic et peut appliquer une action immédiate lorsqu’une règle de prévention est déclenchée : abandonner un paquet, réinitialiser une connexion, bloquer temporairement une source ou demander une action à un autre équipement. Les actions disponibles varient selon les produits.

Dans une architecture *inline*, les paquets passent à travers l’équipement IPS avant d’atteindre leur destination. Le capteur est donc dans le chemin de communication. Cette position lui permet de bloquer certains trafics en temps réel, mais elle introduit un risque opérationnel : une erreur de configuration, une surcharge, une panne ou une règle trop agressive peut interrompre des communications légitimes.

Il faut distinguer **mode détection** et **mode prévention**. De nombreux produits offrent un mode d’observation, d’audit ou de simulation où les règles produisent des alertes sans bloquer. C’est généralement un meilleur point de départ pour comprendre le trafic normal et mesurer les faux positifs avant d’activer des actions de blocage.

Un IPS peut être intégré à un pare-feu de nouvelle génération (NGFW), à une appliance de sécurité, à un logiciel sur un hôte ou à une plate-forme de protection distribuée. Le nom commercial ne suffit pas pour comprendre son fonctionnement : il faut lire la documentation du produit et identifier précisément où les paquets sont inspectés et où les décisions sont appliquées.

### 1.4 IDS et IPS : différences essentielles

| Critère | IDS | IPS |
|---|---|---|
| Objectif principal | Détecter et signaler | Détecter et empêcher si la politique le prévoit |
| Position typique | Hors chemin, sur trafic copié | En ligne ou intégré à un point d’application |
| Action immédiate sur le paquet original | Généralement non | Oui, si l’action et le déploiement le permettent |
| Risque de couper un flux par erreur | Faible pour le trajet réseau, hors actions automatisées | Plus élevé, car le trafic traverse le dispositif |
| Usage fréquent au démarrage | Observation et apprentissage | Souvent observation avant activation du blocage |
| Dépendances | Visibilité, règles, capacité, journaux | Les mêmes, plus disponibilité et latence du chemin critique |

Les deux rôles peuvent coexister. Un capteur IDS peut envoyer des alertes à une plate-forme de supervision. Un IPS peut appliquer une règle à proximité de la frontière. Une équipe sécurité peut aussi utiliser plusieurs capteurs avec des vues complémentaires : réseau, hôte, DNS, identité et journaux applicatifs.

> **Piège :** Ne déduis pas qu’un système est un IPS simplement parce qu’il affiche un bouton « Block ». Vérifie si ce blocage est réellement appliqué au trafic, si l’équipement est en ligne, quelles conditions déclenchent l’action et si l’échec du dispositif laisse passer ou bloque les paquets.

### 1.5 DPI : Deep Packet Inspection

L’inspection approfondie des paquets (**DPI**) est une technique qui examine des informations plus riches que les seuls en-têtes IP et transport. Selon le contexte, le moteur peut reconstituer une partie du flux, reconnaître un protocole applicatif, analyser des champs, comparer des motifs à des signatures et appliquer une politique. Le DPI n’est pas nécessairement un produit autonome : c’est une capacité présente dans divers outils de sécurité et de réseau.

Un traitement typique peut comprendre :

1. **Capture et normalisation** : recevoir le paquet, vérifier les champs, gérer les formats attendus et éliminer certains cas invalides.
2. **Analyse de flux** : associer les paquets à une communication et suivre son état lorsqu’une information suffisante est disponible.
3. **Décodage du protocole** : déterminer si les données correspondent à Ethernet, IP, TCP, UDP, DNS, HTTP, TLS ou à un protocole pris en charge.
4. **Reconstruction** : remettre en ordre les segments d’un flux, gérer les retransmissions et reconstruire les parties de conversation nécessaires à l’inspection.
5. **Détection** : comparer les données à des signatures, des règles de protocole, des indicateurs de comportement ou des seuils.
6. **Décision** : enregistrer l’événement, lever une alerte, laisser passer, bloquer ou transmettre l’information à un autre système selon la politique.

Cette chaîne reste conceptuelle. L’ordre exact, les algorithmes et les capacités diffèrent entre moteurs. Un capteur peut ne pas reconstruire l’ensemble du contenu, et l’analyse peut être limitée par les performances, le type de protocole ou le chiffrement.

### 1.6 Pourquoi inspecter au niveau applicatif ?

Une connexion vers le port TCP 443 est souvent HTTPS, mais un port n’est pas une preuve du contenu. Certaines applications utilisent des ports non standards et certains protocoles peuvent être encapsulés. L’identification applicative combine plusieurs indices : ports, signatures de protocole, états de connexion, métadonnées, motifs dans les données et, selon l’outil, comportements observés dans le temps.

Le DPI peut aider à reconnaître des anomalies comme une requête incohérente avec le protocole, un ordre de messages invalide, un contenu interdit par la politique, une signature d’exploitation connue ou un taux anormal de requêtes. Il ne remplace pas toujours une analyse complète de l’application : une requête peut être syntaxiquement valide et rester abusive au regard des règles métier.

Une règle qui inspecte un champ HTTP n’est pertinente que si le capteur a accès à ce champ. Si le trafic est chiffré et que le moteur ne dispose pas d’une méthode autorisée pour accéder au contenu, il peut ne voir que des métadonnées, le début de la négociation ou des caractéristiques de flux. Il faut donc expliquer explicitement ce que le capteur a observé au moment de qualifier une alerte.

### 1.7 Les principales méthodes de détection

#### Détection par signatures

Une signature décrit une séquence ou une condition associée à un événement connu. Elle peut porter sur un protocole, un motif de données, une combinaison de champs ou une suite d’événements. L’avantage est l’explicabilité : un analyste peut examiner quelle règle a correspondu. La limite est qu’une menace inconnue, modifiée ou encodée différemment peut ne pas correspondre à une signature connue.

Les signatures doivent être entretenues : mise à jour du moteur et des ensembles de règles, désactivation raisonnée des règles inadaptées, validation des variables de réseau et analyse des changements. Importer beaucoup de règles sans comprendre leur portée ne garantit pas une bonne protection ; cela peut accroître le bruit et la consommation de ressources.

#### Détection par anomalies

La détection d’anomalies compare le comportement observé à une référence ou à un modèle : volume de connexions, fréquence de requêtes, taille des échanges, destinations, types de protocoles ou horaires d’activité. Un écart mérite une investigation, mais ne prouve pas une attaque. Une campagne légitime, une mise à jour ou une sauvegarde peut aussi provoquer un pic.

Une bonne référence tient compte des cycles opérationnels, des périodes de pointe, des changements planifiés et de la variabilité normale. Une référence trop rigide génère des faux positifs ; une référence trop large peut laisser passer des activités anormales. Il faut documenter les hypothèses et réévaluer les seuils à mesure que le réseau évolue.

#### Analyse de protocole et de comportement

Le moteur vérifie si les messages suivent les règles d’un protocole, si les transitions d’état sont plausibles, si des champs contradictoires apparaissent ou si une suite d’opérations est inhabituelle. Cette analyse peut repérer des incohérences que de simples motifs ne couvrent pas.

Le résultat dépend de la capacité du moteur à reconstruire correctement le flux et à interpréter le protocole de la même manière que le système de destination. Une différence de traitement entre le capteur et le serveur peut créer un angle mort. C’est une raison importante d’utiliser des moteurs entretenus et de tester les règles avec des captures représentatives.

### 1.8 Faux positifs et faux négatifs

Un **faux positif** est une alerte déclenchée par une activité légitime. Un **faux négatif** est une activité malveillante qui n’est pas détectée. Aucun système ne peut éliminer ces deux catégories dans tous les contextes. Les réglages arbitrent entre couverture, bruit, latence, charge et risque de blocage.

| Résultat | L’activité est malveillante | L’activité est légitime |
|---|---|---|
| Le système déclenche une alerte | Détection correcte (vrai positif) | Faux positif |
| Le système ne déclenche pas d’alerte | Faux négatif | Résultat normal (vrai négatif) |

Une équipe débutante doit éviter de traiter chaque alerte comme une urgence. Elle doit aussi éviter de désactiver immédiatement une règle bruyante. Une méthode plus fiable consiste à conserver un échantillon autorisé, comparer le contexte, déterminer si la règle est trop large, puis ajuster son champ ou son seuil et vérifier que la détection recherchée reste possible.

Les indicateurs usuels comprennent :

- **Précision** : proportion d’alertes déclenchées qui correspondent réellement à un événement recherché.
- **Rappel / sensibilité** : proportion des événements pertinents qui ont été détectés dans un jeu de référence connu.
- **Taux de faux positifs** : proportion d’événements légitimes incorrectement signalés.
- **Volume d’alertes** : nombre d’événements à traiter, utile pour mesurer la charge opérationnelle mais insuffisant pour juger seul de la qualité.

Ces mesures nécessitent un échantillon de référence et une définition claire de ce qui constitue un événement positif. Le volume brut d’alertes ne dit pas combien de menaces ont été correctement détectées.

### 1.9 Où placer un capteur ?

Le placement détermine ce que le système voit. Un capteur près de l’accès Internet peut observer les flux entrants et sortants d’une frontière. Un capteur entre des zones internes peut révéler des déplacements latéraux. Un agent hôte fournit une visibilité sur un serveur précis. Aucun point unique n’offre nécessairement une vue complète.

Les options courantes sont :

- **TAP réseau** : dispositif qui copie le trafic vers un capteur. La capacité dépend du modèle et du lien observé.
- **Port miroir SPAN** : fonctionnalité du commutateur qui copie certaines interfaces ou certains VLAN vers un port d’analyse. La configuration dépend de la plate-forme.
- **Déploiement inline** : le trafic traverse directement l’IPS. Le dispositif participe à la disponibilité du service.
- **Agent hôte** : composant installé sur un système pour surveiller des événements locaux.
- **Capteur virtuel ou cloud** : déploiement dans une infrastructure virtualisée, avec une visibilité dépendante des points de capture proposés par l’environnement.

Un port miroir peut perdre des paquets si le volume agrégé excède la capacité du port de destination. Le capteur semble alors silencieux ou voit une communication incomplète. Il faut vérifier la capacité du chemin de capture, les compteurs de pertes et les statistiques du moteur avant de conclure qu’aucun événement ne se produit.

### 1.10 Schéma animé : IDS passif et IPS en ligne

Le schéma compare deux implantations. Dans la rangée du haut, le trafic continue vers le serveur tandis qu’une copie est envoyée au capteur IDS. Dans la rangée du bas, le trafic traverse l’IPS avant d’atteindre le serveur. Les flèches sont animées ; les libellés occupent des bandes séparées pour éviter tout chevauchement.

<style>
.idsips-figure { margin: 1.5rem 0; max-width: 100%; color: #e4e4e7; }
.idsips-scroll { max-width: 100%; overflow-x: auto; border: 1px solid #3f3f46; border-radius: 1rem; background: #111318; padding: .5rem; }
.idsips-svg { display: block; width: 100%; max-width: 1000px; min-width: 760px; height: auto; margin: 0 auto; }
.idsips-svg text { fill: #e4e4e7; font-family: Inter, Arial, sans-serif; font-size: 15px; }
.idsips-svg .idsips-lane { fill: #181a20; stroke: #41434c; }
.idsips-svg .idsips-card { fill: #242833; stroke: #8b93a5; stroke-width: 1.5; }
.idsips-svg .idsips-card--ids { fill: #102b39; stroke: #38bdf8; }
.idsips-svg .idsips-card--ips { fill: #30231b; stroke: #fb923c; }
.idsips-svg .idsips-heading { font-size: 18px; font-weight: 700; fill: #fff; }
.idsips-svg .idsips-sub { font-size: 13px; fill: #cbd5e1; }
.idsips-svg .idsips-wire { fill: none; stroke: #93a4b8; stroke-width: 3; stroke-dasharray: 8 8; animation: idsips-flow 1.4s linear infinite; }
.idsips-svg .idsips-mirror { fill: none; stroke: #38bdf8; stroke-width: 2.5; stroke-dasharray: 5 6; animation: idsips-flow 1.1s linear infinite; }
.idsips-svg .idsips-block { stroke: #fb923c; stroke-width: 4; }
@keyframes idsips-flow { to { stroke-dashoffset: -32; } }
@media (prefers-reduced-motion: reduce) { .idsips-svg * { animation: none !important; } }
</style>

<div class="idsips-figure">
  <div class="idsips-scroll" role="group" aria-label="Schéma comparatif IDS et IPS ; sur petit écran, faire défiler horizontalement pour lire tous les libellés.">
    <svg class="idsips-svg" viewBox="0 0 960 430" role="img" aria-labelledby="idsips-title idsips-desc">
      <title id="idsips-title">Différence entre placement IDS et IPS</title>
      <desc id="idsips-desc">Le capteur IDS reçoit une copie du trafic et reste hors du chemin principal. L’IPS se trouve en ligne entre le pare-feu et le serveur, où il peut interrompre un flux.</desc>
      <rect class="idsips-lane" x="8" y="8" width="944" height="194" rx="14" />
      <text class="idsips-heading" x="28" y="36">IDS — observation passive</text>
      <text class="idsips-sub" x="28" y="57">Une copie est analysée ; le trafic original continue.</text>
      <rect class="idsips-card" x="28" y="83" width="130" height="57" rx="9" />
      <text x="93" y="107" text-anchor="middle">Client</text><text class="idsips-sub" x="93" y="127" text-anchor="middle">source</text>
      <path class="idsips-wire" d="M158 111 H208" />
      <polygon points="201,105 211,111 201,117" fill="#93a4b8" />
      <rect class="idsips-card" x="211" y="83" width="145" height="57" rx="9" />
      <text x="283" y="107" text-anchor="middle">Pare-feu</text><text class="idsips-sub" x="283" y="127" text-anchor="middle">politique d’accès</text>
      <path class="idsips-wire" d="M356 111 H406" />
      <polygon points="399,105 409,111 399,117" fill="#93a4b8" />
      <rect class="idsips-card" x="409" y="83" width="140" height="57" rx="9" />
      <text x="479" y="107" text-anchor="middle">Commutateur</text><text class="idsips-sub" x="479" y="127" text-anchor="middle">port miroir</text>
      <path class="idsips-wire" d="M549 111 H760" />
      <polygon points="753,105 763,111 753,117" fill="#93a4b8" />
      <rect class="idsips-card" x="763" y="83" width="164" height="57" rx="9" />
      <text x="845" y="107" text-anchor="middle">Serveur</text><text class="idsips-sub" x="845" y="127" text-anchor="middle">service protégé</text>
      <path class="idsips-mirror" d="M479 140 V158 H611" />
      <polygon points="604,152 614,158 604,164" fill="#38bdf8" />
      <rect class="idsips-card--ids" x="614" y="144" width="174" height="43" rx="8" />
      <text x="701" y="162" text-anchor="middle">Capteur IDS</text><text class="idsips-sub" x="701" y="179" text-anchor="middle">alerte et journaux</text>
      <rect class="idsips-lane" x="8" y="214" width="944" height="208" rx="14" />
      <text class="idsips-heading" x="28" y="244">IPS — inspection en ligne</text>
      <text class="idsips-sub" x="28" y="265">Les paquets traversent le dispositif ; une règle peut bloquer le flux.</text>
      <rect class="idsips-card" x="28" y="292" width="130" height="58" rx="9" />
      <text x="93" y="316" text-anchor="middle">Client</text><text class="idsips-sub" x="93" y="336" text-anchor="middle">source</text>
      <path class="idsips-wire" d="M158 321 H208" />
      <polygon points="201,315 211,321 201,327" fill="#93a4b8" />
      <rect class="idsips-card" x="211" y="292" width="145" height="58" rx="9" />
      <text x="283" y="316" text-anchor="middle">Pare-feu</text><text class="idsips-sub" x="283" y="336" text-anchor="middle">filtrage</text>
      <path class="idsips-wire" d="M356 321 H398" />
      <polygon points="391,315 401,321 391,327" fill="#93a4b8" />
      <rect class="idsips-card--ips" x="401" y="292" width="154" height="58" rx="9" />
      <text x="478" y="316" text-anchor="middle">IPS en ligne</text><text class="idsips-sub" x="478" y="336" text-anchor="middle">inspecte / décide</text>
      <path class="idsips-wire" d="M555 321 H760" />
      <polygon points="753,315 763,321 753,327" fill="#93a4b8" />
      <rect class="idsips-card" x="763" y="292" width="164" height="58" rx="9" />
      <text x="845" y="316" text-anchor="middle">Serveur</text><text class="idsips-sub" x="845" y="336" text-anchor="middle">service protégé</text>
      <line class="idsips-block" x1="590" y1="307" x2="590" y2="335" />
      <text class="idsips-sub" x="610" y="303">Blocage possible</text><text class="idsips-sub" x="610" y="321">si la règle</text><text class="idsips-sub" x="610" y="339">correspond</text>
      <text class="idsips-sub" x="28" y="391">À retenir : IDS = visibilité et alerte ; IPS = visibilité et action possible sur le trafic.</text>
    </svg>
  </div>
</div>

### 1.11 Les signatures et les règles

Une règle IDS/IPS décrit une condition de détection et une action associée. Selon l’outil, elle peut spécifier un protocole, des adresses ou ports, un type de message, une direction, un motif de données et un identifiant unique. Les règles sont parfois regroupées en ensembles gérés par un éditeur ou une communauté.

Un identifiant ne dit pas à lui seul si une règle est bonne pour ton environnement. Il faut lire son objectif, les préconditions, les limites connues, la version de la règle et l’action recommandée. Une signature qui détecte un comportement très général peut avoir un taux de faux positifs élevé si elle est appliquée à des segments où ce comportement est normal.

Une politique raisonnable distingue au moins :

- **Alerte** : consigner un événement et demander une analyse.
- **Journalisation** : garder les détails nécessaires à la recherche, dans le respect de la politique de données.
- **Abandon** : jeter le paquet ou la session lorsque le moteur et sa position le permettent.
- **Réinitialisation** : tenter d’interrompre une connexion, action dont l’efficacité dépend du protocole et de l’état de session.
- **Limitation** : réduire un débit ou un nombre d’événements lorsque le produit prend cette mesure en charge.
- **Désactivation ou exclusion limitée** : éviter une règle uniquement après analyse, avec une portée et une durée documentées.

Évite les exclusions globales destinées à faire disparaître les alertes. Elles peuvent masquer une véritable tentative d’attaque. Quand une exception est indispensable, limite-la à un système, un flux ou une règle précise, ajoute une justification et une date de révision, puis surveille les conséquences.

### 1.12 Lire une alerte

Une alerte courante peut contenir : l’heure, le capteur, l’identifiant de règle, le nom de signature, l’adresse source, l’adresse de destination, le protocole, les ports, l’action, une catégorie et des métadonnées sur le flux. Les journaux détaillés peuvent inclure les paquets observés ou certaines informations applicatives, selon la configuration.

Pour lire une alerte, pose les questions suivantes :

1. **Qu’a observé le capteur ?** Une signature, un dépassement de seuil, une incohérence de protocole ou une donnée venant d’un autre outil ?
2. **Où le capteur était-il placé ?** Sur un segment miroir, sur l’hôte, en ligne ou derrière un équipement qui a déjà transformé le trafic ?
3. **Quelle est la portée de la règle ?** Quels hôtes, protocoles et conditions sont concernés ?
4. **Le même événement apparaît-il ailleurs ?** Cherche des alertes corrélées, des journaux système ou applicatifs et des événements d’authentification.
5. **Quel est l’impact démontré ?** Une alerte seule n’indique pas forcément qu’un exploit a réussi.
6. **Quelle action proportionnée peut être prise ?** Collecter davantage de preuves, isoler un hôte si nécessaire, corriger une configuration ou escalader vers l’équipe appropriée.

Une enquête doit conserver les heures avec fuseau ou référence commune, l’identifiant de l’alerte, les commandes exécutées, les observations et les décisions. Cela facilite la comparaison entre capteurs et évite de confondre une intuition avec un fait observé.

### 1.13 Schéma animé : chaîne de traitement DPI

Le DPI n’est pas une simple recherche de mots dans un paquet isolé. Le schéma ci-dessous montre une chaîne simplifiée allant de l’arrivée des paquets à une décision. Les étapes peuvent être fusionnées ou ordonnées différemment selon le produit ; le dessin sert à comprendre les responsabilités essentielles.

<style>
.dpi-figure { margin: 1.5rem 0; max-width: 100%; color: #e4e4e7; }
.dpi-scroll { max-width: 100%; overflow-x: auto; border: 1px solid #3f3f46; border-radius: 1rem; background: #111318; padding: .5rem; }
.dpi-svg { display: block; width: 100%; max-width: 1000px; min-width: 800px; height: auto; margin: 0 auto; }
.dpi-svg text { fill: #e4e4e7; font-family: Inter, Arial, sans-serif; font-size: 14px; }
.dpi-svg .dpi-heading { fill: #fff; font-weight: 700; font-size: 19px; }
.dpi-svg .dpi-card { fill: #222630; stroke: #64748b; stroke-width: 1.4; }
.dpi-svg .dpi-card--decision { fill: #142c25; stroke: #4ade80; }
.dpi-svg .dpi-flow { fill: none; stroke: #60a5fa; stroke-width: 3; stroke-dasharray: 8 8; animation: dpi-flow 1.25s linear infinite; }
.dpi-svg .dpi-step { fill: #38bdf8; opacity: .85; animation: dpi-pulse 1.5s ease-in-out infinite; }
.dpi-svg .dpi-step:nth-child(2) { animation-delay: .35s; }
.dpi-svg .dpi-step:nth-child(3) { animation-delay: .7s; }
@keyframes dpi-flow { to { stroke-dashoffset: -32; } }
@keyframes dpi-pulse { 0%, 100% { opacity: .25; } 50% { opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .dpi-svg * { animation: none !important; } }
</style>

<div class="dpi-figure">
  <div class="dpi-scroll" role="group" aria-label="Chaîne d’inspection approfondie ; faire défiler horizontalement sur petit écran.">
    <svg class="dpi-svg" viewBox="0 0 960 310" role="img" aria-labelledby="dpi-title dpi-desc">
      <title id="dpi-title">Étapes d’une inspection approfondie</title>
      <desc id="dpi-desc">Les paquets sont normalisés, regroupés en flux, décodés au niveau protocolaire, évalués par les règles puis associés à une décision de journalisation, d’alerte ou de blocage.</desc>
      <text class="dpi-heading" x="24" y="32">Du paquet à la décision</text>
      <text x="24" y="55" fill="#a1a1aa">Chaîne conceptuelle — les produits peuvent regrouper ou réordonner certaines étapes.</text>
      <path class="dpi-flow" d="M164 130 H196 M339 130 H371 M514 130 H546 M689 130 H721" />
      <polygon points="190,124 200,130 190,136" fill="#60a5fa" />
      <polygon points="365,124 375,130 365,136" fill="#60a5fa" />
      <polygon points="540,124 550,130 540,136" fill="#60a5fa" />
      <polygon points="715,124 725,130 715,136" fill="#60a5fa" />
      <rect class="dpi-card" x="20" y="85" width="144" height="90" rx="12" />
      <text x="92" y="113" text-anchor="middle" font-weight="700">1. Capture</text><text x="92" y="137" text-anchor="middle">Paquets reçus</text><text x="92" y="156" text-anchor="middle">et normalisés</text>
      <rect class="dpi-card" x="196" y="85" width="143" height="90" rx="12" />
      <text x="267" y="113" text-anchor="middle" font-weight="700">2. Flux</text><text x="267" y="137" text-anchor="middle">Association</text><text x="267" y="156" text-anchor="middle">et état</text>
      <rect class="dpi-card" x="371" y="85" width="143" height="90" rx="12" />
      <text x="442" y="113" text-anchor="middle" font-weight="700">3. Décodage</text><text x="442" y="137" text-anchor="middle">Protocole et</text><text x="442" y="156" text-anchor="middle">reconstruction</text>
      <rect class="dpi-card" x="546" y="85" width="143" height="90" rx="12" />
      <text x="617" y="113" text-anchor="middle" font-weight="700">4. Détection</text><text x="617" y="137" text-anchor="middle">Signatures et</text><text x="617" y="156" text-anchor="middle">comportement</text>
      <rect class="dpi-card--decision" x="721" y="85" width="218" height="90" rx="12" />
      <text x="830" y="113" text-anchor="middle" font-weight="700">5. Décision</text><text x="830" y="137" text-anchor="middle">Journaliser, alerter,</text><text x="830" y="156" text-anchor="middle">laisser passer ou bloquer</text>
      <circle class="dpi-step" cx="178" cy="130" r="5" /><circle class="dpi-step" cx="354" cy="130" r="5" /><circle class="dpi-step" cx="529" cy="130" r="5" />
      <rect x="24" y="211" width="912" height="68" rx="12" fill="#191b22" stroke="#393d49" />
      <text x="44" y="238" font-weight="700">Limite importante</text><text x="44" y="260">Si le contenu est chiffré ou absent du point de capture, le moteur ne peut pas inspecter les données auxquelles il n’a pas accès.</text>
    </svg>
  </div>
</div>

### 1.14 Le chiffrement et les limites du DPI

TLS protège la confidentialité et l’intégrité du contenu échangé entre les extrémités. Un capteur qui observe uniquement le trafic chiffré ne doit pas être présenté comme s’il avait lu les messages applicatifs. Selon la version du protocole, la configuration et l’endroit où se trouve le capteur, il peut observer des adresses, des ports, des volumes, des horaires, certains éléments de négociation et d’autres métadonnées ; une part croissante du contenu reste chiffrée.

Plusieurs stratégies existent, chacune avec ses limites :

- **Inspection des métadonnées** : exploiter les informations disponibles sans déchiffrer le contenu. Cela aide à comprendre les flux mais ne fournit pas une inspection complète du texte applicatif.
- **Capteur côté serveur ou hôte** : observer le trafic après déchiffrement, les journaux de l’application ou les événements du système, si les autorisations et l’architecture le permettent.
- **Inspection TLS autorisée par un intermédiaire** : dans certains environnements, un équipement termine puis recrée la session TLS pour inspecter le contenu. Cela impose une gouvernance explicite, une gestion rigoureuse des certificats, des exceptions, de la confidentialité et des risques de disponibilité.
- **Télémétrie applicative** : utiliser les journaux du proxy, du serveur Web, de l’API ou de l’identité, en réduisant la collecte de données sensibles.

Ne contourne pas le chiffrement et ne collecte pas de contenu personnel sans base légitime et autorisation appropriée. Dans un laboratoire pédagogique, privilégie des données synthétiques et des services de test. L’objectif est de comprendre les limites de la visibilité, pas de surveiller secrètement les utilisateurs.

### 1.14.1 Schéma animé : ce que le capteur voit dans un flux TLS

Le chiffrement ne signifie pas que tout est invisible : des métadonnées peuvent rester observables, mais le contenu applicatif ne doit pas être présenté comme lisible par un capteur passif qui n’a pas accès aux clés ou au point de déchiffrement. Ce schéma sépare ces deux niveaux de visibilité.

<style>
tlsdpi-figure { margin: 1.5rem 0; max-width: 100%; color: #e4e4e7; }
.tlsdpi-scroll { max-width: 100%; overflow-x: auto; border: 1px solid #3f3f46; border-radius: 1rem; background: #111318; padding: .5rem; }
.tlsdpi-svg { display: block; width: 100%; max-width: 1000px; min-width: 780px; height: auto; margin: 0 auto; }
.tlsdpi-svg text { fill: #e4e4e7; font-family: Inter, Arial, sans-serif; font-size: 15px; }
.tlsdpi-svg .tlsdpi-head { fill: #fff; font-size: 19px; font-weight: 700; }
.tlsdpi-svg .tlsdpi-box { fill: #222630; stroke: #64748b; stroke-width: 1.4; }
.tlsdpi-svg .tlsdpi-encrypted { fill: #172842; stroke: #60a5fa; stroke-width: 1.5; }
.tlsdpi-svg .tlsdpi-metadata { fill: #142e27; stroke: #4ade80; stroke-width: 1.5; }
.tlsdpi-svg .tlsdpi-path { fill: none; stroke: #60a5fa; stroke-width: 3; stroke-dasharray: 8 8; animation: tlsdpi-flow 1.3s linear infinite; }
.tlsdpi-svg .tlsdpi-mirror { fill: none; stroke: #4ade80; stroke-width: 2.5; stroke-dasharray: 6 7; animation: tlsdpi-flow 1.1s linear infinite; }
@keyframes tlsdpi-flow { to { stroke-dashoffset: -32; } }
@media (prefers-reduced-motion: reduce) { .tlsdpi-svg * { animation: none !important; } }
</style>

<div class="tlsdpi-figure">
  <div class="tlsdpi-scroll" role="group" aria-label="Visibilité d’un capteur sur une connexion TLS ; faire défiler horizontalement sur petit écran.">
    <svg class="tlsdpi-svg" viewBox="0 0 960 360" role="img" aria-labelledby="tlsdpi-title tlsdpi-desc">
      <title id="tlsdpi-title">Visibilité du contenu TLS</title>
      <desc id="tlsdpi-desc">Un capteur passif reçoit une copie du flux TLS chiffré et peut étudier certaines métadonnées, mais pas lire directement le contenu applicatif. Un capteur situé au point de terminaison peut utiliser les journaux applicatifs autorisés après déchiffrement.</desc>
      <text class="tlsdpi-head" x="24" y="32">Inspecter un flux chiffré : visibilité et limites</text>
      <rect class="tlsdpi-box" x="24" y="75" width="154" height="68" rx="10" />
      <text x="101" y="103" text-anchor="middle" font-weight="700">Client</text><text x="101" y="125" text-anchor="middle">application</text>
      <path class="tlsdpi-path" d="M178 109 H260" /><polygon points="253,103 263,109 253,115" fill="#60a5fa" />
      <rect class="tlsdpi-encrypted" x="263" y="75" width="230" height="68" rx="10" />
      <text x="378" y="103" text-anchor="middle" font-weight="700">Tunnel TLS</text><text x="378" y="125" text-anchor="middle">charge utile chiffrée</text>
      <path class="tlsdpi-path" d="M493 109 H700" /><polygon points="693,103 703,109 693,115" fill="#60a5fa" />
      <rect class="tlsdpi-box" x="703" y="75" width="230" height="68" rx="10" />
      <text x="818" y="103" text-anchor="middle" font-weight="700">Serveur / terminaison</text><text x="818" y="125" text-anchor="middle">accès au contenu local</text>
      <path class="tlsdpi-mirror" d="M378 143 V174" /><polygon points="372,167 378,177 384,167" fill="#4ade80" />
      <rect class="tlsdpi-metadata" x="263" y="180" width="230" height="64" rx="10" />
      <text x="378" y="205" text-anchor="middle" font-weight="700">Capteur passif</text><text x="378" y="226" text-anchor="middle">copie chiffrée / métadonnées</text>
      <rect class="tlsdpi-box" x="24" y="270" width="440" height="64" rx="10" />
      <text x="244" y="294" text-anchor="middle" font-weight="700">Sans accès au déchiffrement</text><text x="244" y="316" text-anchor="middle">Ne pas prétendre lire les requêtes applicatives.</text>
      <rect class="tlsdpi-box" x="496" y="270" width="437" height="64" rx="10" />
      <text x="714" y="294" text-anchor="middle" font-weight="700">À l’extrémité autorisée</text><text x="714" y="316" text-anchor="middle">Corréler les journaux applicatifs et les événements hôte.</text>
    </svg>
  </div>
</div>

### 1.15 Débit, latence et pertes

L’inspection consomme des ressources : CPU, mémoire, stockage, accélérateurs éventuels et bande passante entre les cartes réseau. Lorsque le volume dépasse la capacité du capteur, des paquets peuvent être perdus, les délais peuvent augmenter, ou l’appareil peut appliquer un comportement de dégradation. La façon dont il réagit dépend du produit et du mode d’installation.

Quelques notions utiles :

- **Débit** : quantité de données traitées par unité de temps, par exemple Mbit/s ou Gbit/s.
- **Paquets par seconde** : nombre de paquets traités dans une seconde. Deux flux au même débit peuvent solliciter très différemment un capteur si la taille des paquets change.
- **Connexions ou flux simultanés** : nombre d’états de communication que l’équipement doit conserver.
- **Latence** : temps supplémentaire introduit dans le traitement.
- **Perte à la capture** : paquets que le capteur ne reçoit pas ou ne traite pas ; elle peut rendre les alertes incomplètes.
- **Capacité effective** : débit soutenu avec les fonctionnalités, règles, journaux, interfaces et tailles de paquets réellement utilisés, et non seulement le chiffre marketing maximal.

La bonne pratique consiste à mesurer le trafic réaliste, à suivre la santé du capteur et à prévoir de la marge. Un test de débit seul ne couvre pas tous les coûts : une règle complexe, une reconstruction de flux ou une journalisation très détaillée peut modifier le profil de charge.

### 1.16 Schéma animé : du signal au triage

Une alerte utile doit être qualifiée, priorisée et suivie. Le schéma présente une boucle de travail simple : signal, contexte, décision initiale, investigation et amélioration de la règle. La boucle évite de transformer chaque alerte en blocage automatique.

<style>
.triage-figure { margin: 1.5rem 0; max-width: 100%; color: #e4e4e7; }
.triage-scroll { max-width: 100%; overflow-x: auto; border: 1px solid #3f3f46; border-radius: 1rem; background: #111318; padding: .5rem; }
.triage-svg { display: block; width: 100%; max-width: 1000px; min-width: 780px; height: auto; margin: 0 auto; }
.triage-svg text { fill: #e4e4e7; font-family: Inter, Arial, sans-serif; font-size: 14px; }
.triage-svg .triage-head { font-size: 19px; font-weight: 700; fill: #fff; }
.triage-svg .triage-box { fill: #222630; stroke: #64748b; stroke-width: 1.4; }
.triage-svg .triage-box--good { fill: #143026; stroke: #4ade80; }
.triage-svg .triage-box--warn { fill: #35291a; stroke: #fbbf24; }
.triage-svg .triage-path { fill: none; stroke: #60a5fa; stroke-width: 3; stroke-dasharray: 7 7; animation: triage-flow 1.4s linear infinite; }
@keyframes triage-flow { to { stroke-dashoffset: -28; } }
@media (prefers-reduced-motion: reduce) { .triage-svg * { animation: none !important; } }
</style>

<div class="triage-figure">
  <div class="triage-scroll" role="group" aria-label="Processus de traitement d’une alerte ; défilement horizontal possible sur mobile.">
    <svg class="triage-svg" viewBox="0 0 960 360" role="img" aria-labelledby="triage-title triage-desc">
      <title id="triage-title">Cycle de traitement d’une alerte de sécurité</title>
      <desc id="triage-desc">Un signal est enrichi par le contexte, trié par priorité, investigué, puis clôturé ou utilisé pour améliorer la règle. Le blocage exige une décision proportionnée.</desc>
      <text class="triage-head" x="24" y="34">Une alerte est le début de l’investigation</text>
      <path class="triage-path" d="M170 111 H204 M354 111 H388 M538 111 H572 M722 111 H756" />
      <polygon points="198,105 208,111 198,117" fill="#60a5fa" /><polygon points="382,105 392,111 382,117" fill="#60a5fa" /><polygon points="566,105 576,111 566,117" fill="#60a5fa" /><polygon points="750,105 760,111 750,117" fill="#60a5fa" />
      <rect class="triage-box" x="20" y="72" width="150" height="78" rx="11" />
      <text x="95" y="101" text-anchor="middle" font-weight="700">1. Signal</text><text x="95" y="123" text-anchor="middle">Alerte IDS/IPS</text>
      <rect class="triage-box" x="204" y="72" width="150" height="78" rx="11" />
      <text x="279" y="101" text-anchor="middle" font-weight="700">2. Contexte</text><text x="279" y="123" text-anchor="middle">Hôte, flux, heure</text>
      <rect class="triage-box--warn" x="388" y="72" width="150" height="78" rx="11" />
      <text x="463" y="101" text-anchor="middle" font-weight="700">3. Priorité</text><text x="463" y="123" text-anchor="middle">Impact et urgence</text>
      <rect class="triage-box" x="572" y="72" width="150" height="78" rx="11" />
      <text x="647" y="101" text-anchor="middle" font-weight="700">4. Vérifier</text><text x="647" y="123" text-anchor="middle">Preuves croisées</text>
      <rect class="triage-box--good" x="756" y="72" width="180" height="78" rx="11" />
      <text x="846" y="101" text-anchor="middle" font-weight="700">5. Réponse</text><text x="846" y="123" text-anchor="middle">Corriger / clôturer</text>
      <path class="triage-path" d="M846 150 V199 H279 V160" />
      <polygon points="273,166 279,156 285,166" fill="#60a5fa" />
      <rect x="24" y="219" width="912" height="100" rx="12" fill="#191b22" stroke="#393d49" />
      <text x="46" y="249" font-weight="700">Après le traitement</text>
      <text x="46" y="273">Documenter la cause, mesurer les faux positifs, ajuster la règle si nécessaire et contrôler le résultat.</text>
      <text x="46" y="298" fill="#a1a1aa">Ne bloque pas automatiquement une source partagée sans évaluer le risque de coupure de services légitimes.</text>
    </svg>
  </div>
</div>

### 1.17 Algorithme de décision de base

Le traitement d’un événement peut être résumé par l’algorithme suivant. Il ne remplace pas la procédure d’incident de l’organisation : il donne une séquence de réflexion pour un premier diagnostic.

```text
ENTRÉE : événement provenant d’un capteur IDS/IPS

1. Vérifier que l’horodatage, le capteur et la règle sont connus.
2. Identifier les hôtes, le protocole, la direction et le segment concerné.
3. Lire la description de la règle et les conditions qui l’ont déclenchée.
4. Chercher des événements associés dans les journaux autorisés.
5. Estimer la gravité et l’impact à partir des preuves disponibles.
6. Si un impact sérieux est plausible : escalader selon la procédure.
7. Sinon : collecter davantage d’éléments avant de modifier la politique.
8. Appliquer une action proportionnée et approuvée.
9. Valider que le service fonctionne et que la menace n’est plus observée.
10. Documenter le résultat et toute modification de règle.

SORTIE : événement qualifié, action justifiée et trace d’investigation.
```

> **Astuce :** Avant de demander un blocage, résume l’alerte en une phrase : « Le capteur X a vu le comportement Y sur le flux Z à l’heure T ; voici les preuves qui suggèrent un risque et voici le service potentiellement affecté. » Cette formulation force à séparer observation, interprétation et action.

### 1.18 Où se situent les différentes familles d’outils ?

| Famille | Ce qu’elle observe généralement | Utilité principale | Limite fréquente |
|---|---|---|---|
| IDS réseau | Paquets copiés et flux visibles au point de capture | Détecter des motifs et anomalies réseau | Visibilité incomplète si capture partielle ou trafic chiffré |
| IPS réseau | Paquets qui traversent l’équipement | Bloquer des comportements identifiés en ligne | Peut ajouter latence et risque de coupure |
| IDS/EDR hôte | Événements système et processus sur un poste/serveur | Voir l’activité locale et enrichir l’investigation | Nécessite un agent et une gestion des systèmes |
| NDR / analyse comportementale réseau | Métadonnées, flux et parfois paquets | Rechercher des écarts de comportement et corréler des flux | Qualité liée à la visibilité, au modèle et au contexte |
| WAF | Requêtes HTTP(S) au point où elles sont interprétables | Protéger des applications Web avec des règles adaptées | Ne protège pas à lui seul tous les protocoles ou défauts métiers |
| SIEM | Événements agrégés provenant de plusieurs systèmes | Centraliser, corréler et enquêter | Une mauvaise normalisation produit des corrélations trompeuses |
| Pare-feu | Principalement règles de flux, état et fonctions supplémentaires selon le produit | Contrôler le passage entre zones | Autoriser un port ne signifie pas valider la sécurité applicative |

Ces catégories se recouvrent parfois. Les produits évoluent, et un équipement peut offrir plusieurs fonctions. Il vaut mieux raisonner par capacité réelle et emplacement dans l’architecture que par seul nom commercial.

---

## 2. Configuration et pratique

### 2.1 Préparer un petit laboratoire

Le laboratoire doit être isolé de la production. Utilise une machine virtuelle ou un réseau de test où tu as l’autorisation d’observer le trafic. Pour débuter, un capteur passif est plus facile à maîtriser qu’un IPS en ligne, car une erreur ne modifie pas directement le chemin réseau.

Exemple d’architecture :

```text
[VM Client de test] ─────── [Réseau virtuel de laboratoire] ─────── [VM Serveur de test]
                                      |
                                      +── copie de trafic ── [VM Capteur IDS]

Le capteur IDS observe la copie. Il ne doit pas être utilisé pour surveiller un réseau tiers.
```

Avant de commencer, note les adresses IP, les interfaces, le système d’exploitation, la version du moteur de détection, le jeu de règles et l’heure de la machine. Vérifie que les systèmes disposent d’un moyen de retour arrière, par exemple un instantané de VM. Ne connecte pas une règle de blocage non validée au réseau d’entreprise.

### 2.2 Installer et vérifier Suricata

Suricata est un moteur de sécurité réseau qui peut détecter des événements à l’aide de règles et produire des journaux structurés. Les commandes exactes dépendent de la distribution, du paquet installé et de la version. Consulte toujours la documentation de la version présente sur ton laboratoire.

Sur une distribution Debian/Ubuntu où le paquet est disponible dans les dépôts configurés, l’installation peut ressembler à ceci :

```bash
sudo apt update
sudo apt install suricata
```

Confirme ensuite la version et les chemins de configuration :

```bash
suricata --build-info
suricata --help
```

Avant de démarrer une capture, valide la configuration avec le fichier réellement installé. Sur de nombreuses installations, le test prend cette forme :

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml -v
```

La commande `-T` teste la configuration ; elle ne doit pas être confondue avec le lancement normal de la capture. Si le chemin diffère sur ta distribution, utilise celui indiqué par le gestionnaire de paquets. Corrige les erreurs avant d’ajouter une interface ou de modifier le mode de détection.

### 2.3 Choisir l’interface de capture

Liste les interfaces disponibles :

```bash
ip -brief address
ip link show
```

Une interface de test peut s’appeler `enp0s3`, `ens33` ou autrement. Ne copie pas un nom d’interface depuis ce document sans le vérifier sur ta machine. Un démarrage sur la mauvaise interface peut produire un capteur silencieux alors que la configuration paraît valide.

Pour une observation simple dans un laboratoire, la commande suivante illustre le lancement sur une interface. Vérifie au préalable la syntaxe de ta version, les droits nécessaires et l’emplacement des journaux :

```bash
sudo suricata -c /etc/suricata/suricata.yaml -i enp0s3
```

Exécute une seule instance sur une interface donnée sauf si la configuration documentée prévoit explicitement plusieurs instances. Sur une machine de laboratoire, arrête proprement le processus selon le mode de lancement choisi et consulte les journaux de démarrage pour détecter les problèmes d’accès, de pilote ou de capture.

### 2.4 Consulter les événements

Selon la configuration, Suricata peut produire des fichiers tels que `eve.json` et `fast.log` dans un répertoire de journalisation. Les noms et les types d’événements activés dépendent du fichier YAML. Une commande courante pour parcourir les dernières lignes JSON est :

```bash
sudo tail -f /var/log/suricata/eve.json
```

Chaque entrée JSON peut représenter une alerte, des statistiques de flux, un événement DNS, HTTP, TLS ou un autre type activé. Utilise un parseur JSON ou un outil d’analyse adapté pour filtrer les événements dans un environnement de travail. Évite d’exposer des journaux bruts publiquement : ils peuvent contenir des adresses, des noms d’hôtes ou d’autres métadonnées sensibles.

Si aucun événement n’apparaît, vérifie d’abord que le processus fonctionne, que la bonne interface est choisie, que cette interface reçoit réellement les paquets du laboratoire et que le format de journal est activé. Le silence ne prouve pas l’absence d’activité malveillante.

### 2.5 Ajouter une règle de test défensive

Les règles Suricata suivent une grammaire spécifique. La ligne suivante illustre une règle d’alerte simple pour observer les requêtes ICMP Echo dans un laboratoire privé ; elle n’est pas destinée à bloquer ou perturber le trafic :

```text
alert icmp any any -> $HOME_NET any (msg:"LAB ICMP Echo observé"; itype:8; sid:1000001; rev:1;)
```

Les éléments essentiels sont :

- `alert` indique qu’il faut produire une alerte si la condition correspond.
- `icmp` identifie le protocole de couche réseau visé par cette règle.
- `any any` signifie que la source n’est pas restreinte par cette partie de la règle.
- `->` décrit la direction évaluée par la règle.
- `$HOME_NET` doit être défini de façon cohérente avec le réseau de laboratoire.
- `msg` fournit un libellé que l’analyste verra dans l’alerte.
- `itype:8` vise les messages Echo Request IPv4 ; cela ne couvre pas à lui seul les mêmes mécanismes en IPv6.
- `sid` identifie la règle, et `rev` sa révision.

Ajoute uniquement la règle de test à l’emplacement prévu par ta configuration, puis lance à nouveau le test de configuration avant le redémarrage. Les chemins et le mécanisme d’inclusion des règles varient ; n’écrase pas un fichier de règles fourni par le paquet sans comprendre comment il est maintenu.

Génère ensuite un ping depuis un client de laboratoire autorisé vers une adresse de test du réseau surveillé. Vérifie que l’alerte attendue apparaît et qu’elle contient l’adresse source et la destination pertinentes. Si elle ne se produit pas, reprends méthodiquement l’interface de capture, la définition de `$HOME_NET`, l’ordre des règles et les journaux de démarrage.

> **Danger :** Ne teste pas une signature contre une adresse publique ou une machine qui ne t’appartient pas. Même un test simple peut être interprété comme une activité indésirable. Garde les expériences dans un environnement isolé et autorisé.

### 2.6 Comprendre l’observation d’un trafic miroir sur Cisco

Sur un commutateur compatible, une session SPAN peut copier des paquets d’un port source vers un port de destination relié au capteur. La syntaxe varie selon les familles Cisco et les versions IOS/IOS XE. Le fragment ci-dessous est un exemple conceptuel représentatif ; vérifie le guide de ta plate-forme, car les restrictions sur les ports source, les VLAN et les sessions miroir peuvent différer.

```text
configure terminal
 monitor session 1 source interface GigabitEthernet1/0/1 both
 monitor session 1 destination interface GigabitEthernet1/0/24
end
show monitor session 1
```

Dans cet exemple, le port `GigabitEthernet1/0/1` est observé dans les deux directions, et `GigabitEthernet1/0/24` reçoit la copie. Les interfaces sont fictives et doivent être adaptées au commutateur du laboratoire. Le port de destination SPAN a souvent des contraintes d’utilisation : il ne doit pas être traité comme un port utilisateur ordinaire.

Une session SPAN ne bloque pas automatiquement les paquets qui correspondent à une signature. Elle fournit une copie à l’outil d’analyse. C’est la fonction de détection et la politique associée qui décident quelles alertes sont produites. Pour bloquer, il faut un mécanisme de prévention réellement positionné dans le chemin, ou un autre contrôle explicite et validé.

Après configuration, vérifie l’état de la session, la réception des paquets sur le capteur et les compteurs de pertes du commutateur si disponibles. Si le trafic agrégé de plusieurs ports dépasse la capacité de sortie du SPAN, la copie peut être incomplète. L’IPS/IDS doit donc être dimensionné et positionné selon la charge attendue.

### 2.7 Scénario guidé : une alerte DNS inhabituelle

Un capteur déclenche une alerte liée à un volume inhabituel de requêtes DNS provenant d’un poste de laboratoire. Avant toute action, tu dois distinguer les faits des hypothèses.

**Étape 1 — Vérifier la source.** Confirme l’adresse IP, l’adresse MAC si elle est disponible, le nom d’hôte et l’heure. Attention : une adresse peut être traduite par NAT ou réattribuée par DHCP ; le contexte temporel est important.

**Étape 2 — Lire la règle.** Détermine si elle détecte un nom de domaine particulier, une fréquence élevée, un type de requête inhabituel ou une signature précise. Le mot « DNS » seul ne décrit pas la condition de déclenchement.

**Étape 3 — Regarder les événements associés.** Cherche d’autres requêtes de la même source, les destinations interrogées et les journaux du résolveur administré. Si possible, corrèle avec l’inventaire, l’activité de l’utilisateur et les changements planifiés.

**Étape 4 — Évaluer le risque.** Un logiciel peut faire beaucoup de requêtes légitimes pendant une mise à jour. Des noms générés de façon inhabituelle ou des volumes persistants vers des destinations inattendues peuvent justifier une analyse supplémentaire, mais ne suffisent pas automatiquement à conclure à une compromission.

**Étape 5 — Répondre proportionnellement.** Si le comportement reste suspect, collecte les éléments autorisés et escalade vers l’équipe sécurité. Une règle de blocage du DNS peut interrompre des services importants ; ne l’applique pas sur un réseau réel sans vérifier les dépendances et le plan de retour arrière.

**Étape 6 — Clôturer.** Note la cause retenue, le niveau de confiance, les preuves, la mesure prise et les raisons de l’action. Si la règle génère un faux positif, prépare une amélioration ciblée et teste-la avant son déploiement.

### 2.8 Comparer IDS et IPS dans un même laboratoire

| Test | Configuration IDS passive | Configuration IPS en ligne |
|---|---|---|
| Voir un ping entre deux VM | Oui si le point de capture le reçoit | Oui si le trafic traverse l’IPS |
| Produire une alerte de signature de test | Oui, selon la règle et la visibilité | Oui, selon la règle et la visibilité |
| Bloquer le ping original grâce à la règle | Non dans une architecture passive pure | Possible si une règle de prévention valide le permet |
| Si le capteur est déconnecté | Perte d’observation | Risque de panne ou de contournement selon le mode de défaillance |
| Mesurer le risque de faux positif | Observer l’alerte sans perturber la session | Tester en mode non bloquant, puis planifier le passage en blocage |

Ce laboratoire doit confirmer le fonctionnement, pas rechercher la saturation ou la perturbation de systèmes. L’objectif est d’apprendre à vérifier le placement et la politique avant de tirer une conclusion sur les capacités du capteur.

---

## 3. Dépannage et sécurité

### 3.1 Le capteur n’affiche aucune alerte

Une absence d’alerte peut avoir plusieurs causes. Il faut commencer par les conditions les plus simples avant de modifier les règles.

1. **Le capteur est-il actif ?** Vérifie l’état du service, les journaux de démarrage et l’utilisation des ressources.
2. **Reçoit-il des paquets ?** Confirme l’interface, le port miroir ou la source de capture. Utilise une observation de test et vérifie les compteurs.
3. **La configuration est-elle valide ?** Un test de syntaxe peut révéler des chemins inexistants, une règle mal formée ou une variable réseau mal définie.
4. **La règle est-elle chargée ?** Vérifie le journal de démarrage et l’identifiant de la règle. Une règle écrite dans un fichier jamais inclus ne sera pas évaluée.
5. **Le test correspond-il à la condition ?** Une règle HTTP n’est pas déclenchée par un ping. Une signature IPv4 précise ne couvre pas automatiquement IPv6.
6. **Le trafic est-il chiffré ou incomplet ?** Le capteur peut ne pas avoir accès au contenu attendu ou manquer certains segments.
7. **Une exclusion a-t-elle été appliquée ?** Revois les variables, les désactivations locales et les exceptions de politique.

Ne désactive pas toutes les protections pour « voir si ça marche ». Procède par test contrôlé et garde une trace de chaque modification afin de pouvoir revenir à l’état précédent.

### 3.2 Trop d’alertes : maîtriser le bruit

Un volume élevé d’alertes peut provenir d’une signature trop générale, d’un réseau mal décrit, d’un seuil trop bas, d’un trafic de découverte légitime ou d’une véritable activité anormale. L’objectif n’est pas de rendre le tableau de bord silencieux ; il est d’obtenir des événements exploitables.

Méthode de travail :

- Regroupe les alertes par règle, source, destination, protocole et période.
- Choisis un échantillon représentatif, pas seulement la première alerte.
- Lis la définition de la signature et confirme ce qu’elle est censée détecter.
- Compare avec le trafic normal documenté et les changements récents.
- Si le comportement est légitime, ajuste le seuil ou la portée de façon la plus limitée possible.
- Si la règle est obsolète ou inadaptée, documente pourquoi et qui a approuvé son changement.
- Après modification, surveille les alertes semblables et vérifie qu’un événement de test connu peut encore être détecté.

> **Piège :** Exclure une adresse IP entière parce qu’elle déclenche des alertes peut masquer plusieurs systèmes derrière un NAT ou un proxy. Vérifie l’identité réelle de la source et la portée exacte de l’exception.

### 3.3 Faux positif ou vrai incident ?

Une bonne investigation cherche une preuve indépendante. Une alerte d’exploitation Web peut être rapprochée des journaux du proxy, des codes de réponse HTTP, des changements de fichiers, des événements d’authentification et des journaux système. Un scan détecté peut provenir d’un inventaire autorisé ou d’un outil malveillant ; il faut confirmer qui l’a initié et si une autorisation existe.

Le niveau de confiance doit être explicite : « confirmé », « probable », « possible » ou « non déterminé » peuvent être utilisés si l’organisation les définit. Ne transforme pas une corrélation temporelle en causalité sans preuve. Une attaque peut aussi échouer ; le fait de détecter une tentative ne signifie pas nécessairement que l’hôte a été compromis.

Pour un événement sérieux, conserve les informations pertinentes avant de modifier la politique. Une règle de blocage ou une suppression de journal peut détruire certains indices et compliquer l’analyse. Respecte les procédures de réponse aux incidents de ton organisation.

### 3.4 Trafic asymétrique et visibilité incomplète

Dans un réseau routé, le trafic aller et retour peut emprunter des chemins différents. Un capteur qui ne voit qu’un côté d’une conversation peut avoir du mal à reconstruire son état, à interpréter les retransmissions ou à reconnaître un protocole. Ce phénomène est particulièrement important pour les moteurs qui dépendent de la reconstruction de flux.

Vérifie la topologie et les points de capture :

- Le lien observé transporte-t-il les deux directions ?
- Les chemins aller et retour passent-ils par le même équipement ?
- Un port miroir ou un TAP fournit-il une copie dans les deux directions lorsque c’est nécessaire ?
- Une traduction NAT, un tunnel ou un répartiteur de charge modifie-t-il ce que voit le capteur ?
- Les compteurs indiquent-ils des pertes sur la capture ou sur l’interface ?

Ne conclus pas qu’une session est malveillante uniquement parce qu’elle apparaît incomplète. Il peut s’agir d’un problème de visibilité, d’un flux asymétrique ou d’une limitation de capture.

### 3.5 Le capteur est lent ou perd des paquets

La charge peut provenir du débit, du nombre de paquets, de nombreux petits flux, de règles trop coûteuses, d’une journalisation excessive ou de ressources insuffisantes. Il faut mesurer plutôt que supposer.

Points de contrôle :

- CPU, mémoire, stockage, files réseau et erreurs de carte d’interface.
- Débit en bits/s et paquets/s, idéalement séparés par interface ou type de flux.
- Statistiques de pertes du moteur, de la carte réseau et du commutateur de capture.
- Nombre de sessions simultanées et taux de nouvelles connexions.
- Volume d’événements et de journaux émis.
- Différence entre la charge habituelle et celle au moment de l’incident.

Commence par une capture et des règles adaptées à l’objectif. Active les journaux très détaillés sur une durée limitée et dans un périmètre connu. L’ajout de toutes les règles disponibles peut augmenter la charge et rendre le diagnostic moins clair.

### 3.6 Le blocage IPS interrompt un service légitime

Un faux positif en mode IPS est plus sensible, car il peut affecter directement une communication. La première priorité est de suivre le processus approuvé de gestion d’incident et de rétablir le service de façon contrôlée.

Une procédure prudente peut comprendre :

1. Recueillir l’heure, le flux affecté, la règle, l’action et l’étendue de l’impact.
2. Vérifier qu’il s’agit bien du dispositif IPS plutôt que d’un pare-feu, d’un routage ou de l’application elle-même.
3. Déterminer si l’organisation dispose d’un mode non bloquant ou d’une exception temporaire approuvée.
4. Appliquer uniquement la modification minimale autorisée, avec un propriétaire et une durée de validité.
5. Vérifier le rétablissement à l’aide d’un test fonctionnel et surveiller le flux.
6. Reproduire la situation en laboratoire, ajuster la règle et la faire valider avant déploiement permanent.
7. Documenter les risques, le retour arrière et les observations après changement.

La bascule en mode « fail-open » ou « fail-close » dépend du produit, du modèle de risque et des exigences de disponibilité. Il n’existe pas de choix universel : laisser passer en cas de panne améliore la disponibilité mais réduit la prévention, tandis que bloquer tout trafic en cas de panne peut interrompre un service. Ce choix doit être explicite et documenté.

> **Danger :** Ne modifie pas une politique de prévention en production sous la pression d’un seul message d’alerte sans comprendre la règle, l’impact et la procédure de retour arrière. Une exception temporaire doit avoir une portée minimale, un responsable et une date d’expiration.

### 3.7 Le chiffrement crée-t-il un angle mort ?

Le chiffrement n’est pas une anomalie et ne constitue pas en soi une preuve de menace. Il protège les utilisateurs et les applications. Il peut néanmoins réduire la visibilité du capteur lorsque celui-ci n’a pas accès au contenu déchiffré. Le dépannage doit identifier précisément la limite : métadonnées disponibles, journaux d’extrémité, télémétrie applicative ou inspection TLS autorisée.

Si une inspection TLS est envisagée, il faut prendre en compte les données personnelles, les obligations légales, les applications qui ne tolèrent pas l’interception, la gestion de la clé, la confiance des certificats, la journalisation et les risques de disponibilité. Les exceptions doivent être fondées sur des exigences explicites et testées. Ne collecte pas les contenus confidentiels sans base et autorisation appropriées.

### 3.8 Sécuriser le capteur et ses journaux

Un système de détection contient des informations précieuses sur le réseau : adresses internes, noms d’hôtes, habitudes de communication, alertes et parfois extraits de données. Il doit donc être protégé comme un système de sécurité à part entière.

Bonnes pratiques :

- Limiter l’administration aux personnes autorisées et utiliser une authentification robuste.
- Maintenir le système, le moteur, les règles et les dépendances à jour selon un processus de validation.
- Restreindre les ports et services d’administration, ainsi que l’accès aux journaux.
- Synchroniser l’heure par une source fiable et conserver les références temporelles.
- Définir la rétention, les droits d’accès et les conditions d’exportation des événements.
- Éviter les captures complètes permanentes lorsque des métadonnées suffisent ; réduire ou masquer les informations sensibles si possible.
- Sauvegarder la configuration et vérifier périodiquement la possibilité de restauration.
- Surveiller l’état de santé du capteur lui-même : service, capacité, pertes et absence soudaine d’événements.
- Tester les mises à jour de règles avant de les généraliser ; garder une version précédente utilisable.

Un capteur non supervisé peut devenir une fausse assurance. Il faut générer des tests de santé connus, vérifier qu’ils apparaissent dans les journaux et alerter l’équipe si cette chaîne cesse de fonctionner.

### 3.9 Exercice guidé : alerte HTTP déclenchée sur un site interne

**Situation.** Un capteur signale une signature suspecte dans une requête HTTP provenant d’un poste vers un serveur interne. Le service est important pour les utilisateurs.

**Questions de départ :**

1. L’IPS est-il en ligne ou le capteur reçoit-il une copie ?
2. La règle a-t-elle déclenché une simple alerte ou une action de blocage ?
3. Quelle partie de la requête est concernée, et cette donnée était-elle visible du capteur ?
4. Le poste source est-il connu, et quel utilisateur ou service l’utilisait à ce moment ?
5. Le serveur a-t-il renvoyé un code d’erreur, traité la requête ou généré un événement de sécurité ?
6. D’autres capteurs ont-ils observé le même comportement ?

**Chemin de résolution recommandé :** conserve les détails de l’alerte, identifie la règle, récupère les journaux pertinents et compare les heures. Vérifie s’il s’agissait d’un test interne planifié ou d’un comportement applicatif connu. Si l’activité reste suspecte, escalade selon la procédure et cherche des preuves de conséquence sur le serveur. Si un faux positif est confirmé, propose une exception limitée ou un ajustement de la règle dans le processus de changement. Vérifie enfin que les requêtes légitimes fonctionnent toujours et que la règle couvre encore le comportement qu’elle devait détecter.

**Résultat attendu.** L’apprenant doit pouvoir distinguer la détection (l’alerte est produite), la prévention (un paquet ou un flux est bloqué), et la confirmation d’incident (des preuves supplémentaires montrent un impact ou une compromission).

### 3.10 Checklist avant activation de la prévention

- [ ] Le mode de fonctionnement et le point de placement sont compris.
- [ ] Le trafic attendu est visible dans les deux directions si le moteur en dépend.
- [ ] Le moteur, la configuration et le jeu de règles ont été testés.
- [ ] Les règles importantes ont été observées en mode alerte ou simulation.
- [ ] Les faux positifs courants ont été analysés et leurs corrections documentées.
- [ ] La capacité est suffisante pour les profils de trafic attendus.
- [ ] Les journaux et alertes sont surveillés ; l’heure est cohérente.
- [ ] L’équipe connaît l’impact possible d’un blocage et la procédure d’escalade.
- [ ] Le retour arrière est écrit, testé et accessible.
- [ ] Les propriétaires du service ont validé la fenêtre de changement.
- [ ] Un test fonctionnel permettra de confirmer le résultat après activation.
- [ ] Un moyen de supervision confirme que le capteur lui-même reste opérationnel.

### 3.11 Exercices de révision

**Exercice 1.** Un IDS reçoit une copie du trafic via SPAN et déclenche une alerte. Peut-il, par cette seule architecture passive, garantir que le paquet a été bloqué sur le réseau ? Explique pourquoi.

**Correction.** Non. Une architecture passive ne fait qu’observer la copie. Une action de blocage exige un mécanisme en ligne ou une action externe distincte, et il faut vérifier qu’elle a effectivement été appliquée.

**Exercice 2.** Une règle d’inspection HTTP ne déclenche rien sur une connexion HTTPS chiffrée. Donne trois vérifications possibles avant de conclure à un défaut de règle.

**Correction.** Vérifier si le capteur a accès au contenu, si la capture inclut le bon flux et les deux directions, et si l’inspection TLS ou une visibilité côté serveur est prévue. Vérifier aussi si la règle est chargée et applicable au protocole réellement observé.

**Exercice 3.** Plusieurs alertes proviennent d’un scanner interne autorisé. Quelle est la réponse la plus sûre : désactiver toutes les règles, ignorer l’alerte sans trace ou documenter une exception limitée ?

**Correction.** Documenter une exception ciblée seulement après confirmation du scanner autorisé, de son périmètre et de sa fenêtre d’activité. Conserver la raison, la portée, le responsable, l’expiration et une validation après changement.

**Exercice 4.** Un IPS commence à bloquer un flux métier après une mise à jour du jeu de règles. Quelles informations recueillir avant de changer la politique ?

**Correction.** La règle et sa version, l’action appliquée, les sources/destinations, le protocole, l’heure, les journaux du service, le changement récemment effectué, l’étendue de l’impact et le mode de retour arrière. Il faut confirmer que le blocage provient bien de l’IPS.

**Exercice 5.** Le capteur signale des pertes de paquets. Pourquoi est-il dangereux de considérer les alertes restantes comme une vue complète du trafic ?

**Correction.** Les pertes peuvent empêcher la reconstruction de flux et cacher des segments nécessaires à une détection. Les alertes peuvent être incomplètes ; il faut corriger le point de capture ou la capacité et documenter la période concernée.

**Exercice 6.** Une signature correspond à une tentative d’exploitation connue, mais le serveur semble fonctionner normalement. Peut-on conclure que l’incident est clos ?

**Correction.** Pas immédiatement. L’alerte indique une correspondance avec une règle, mais il faut confirmer la précision de la signature, le contexte et les journaux du serveur. L’attaque peut avoir échoué, la règle peut être un faux positif, ou une conséquence peut ne pas être visible sur le seul capteur.

---

## Points à retenir

- Un **IDS** détecte et signale ; un **IPS** peut aussi agir sur le trafic lorsque le dispositif et le mode de déploiement le permettent.
- Le **DPI** examine des informations de protocole ou de contenu plus approfondies que les seuls en-têtes. Il dépend de la visibilité du capteur et du protocole.
- Un port miroir et un TAP fournissent une copie du trafic ; ils ne sont pas équivalents à un IPS en ligne.
- Les signatures, l’analyse de protocole et la détection d’anomalies offrent des perspectives différentes, chacune avec ses limites.
- Une alerte n’est pas à elle seule une preuve de compromission. Elle doit être reliée au contexte, aux journaux et à l’impact observé.
- Les faux positifs, faux négatifs, pertes à la capture, asymétries de routage et limitations liées au chiffrement doivent être pris en compte.
- Le mode passif est un bon point de départ pour comprendre le trafic et évaluer les règles avant d’activer des blocages en production.
- Les règles doivent être testées, les exceptions documentées et toute action de prévention accompagnée d’un plan de retour arrière.
- Les schémas de ce cours utilisent des animations CSS ; les libellés restent dans des zones fixes et séparées. Sur les petits écrans, les diagrammes larges peuvent être parcourus horizontalement pour préserver leur lisibilité.
- Les essais pratiques doivent rester dans un laboratoire autorisé, utiliser des données de test et respecter les règles de confidentialité de l’organisation.

## Références et lectures complémentaires

1. **NIST SP 800-94 — Guide to Intrusion Detection and Prevention Systems (IDPS)** : principes, familles de capteurs, déploiement, gestion et entretien. La publication finale est ancienne ; NIST indique que le projet de révision de 2012 n’a pas été finalisé. À utiliser pour les concepts fondamentaux, avec les documentations actuelles des produits pour les détails d’implémentation. https://csrc.nist.gov/pubs/sp/800/94/final
2. **Documentation officielle Suricata** : configuration, règles, sorties d’événements et statistiques. https://docs.suricata.io/
3. **Manuel utilisateur Snort 3** : architecture, règles, mode IDS et options de fonctionnement. https://github.com/snort3/snort3/blob/master/doc/user/snort_user.text
4. **RFC 9846 — The Transport Layer Security (TLS) Protocol Version 1.3** : fonctionnement et objectifs de sécurité de TLS 1.3 ; elle a remplacé la RFC 8446 en juillet 2026. https://www.rfc-editor.org/rfc/rfc9846.html
5. **MITRE ATT&CK** : connaissances sur les tactiques, techniques et procédures adverses, à utiliser pour contextualiser les événements sans traiter une correspondance comme une preuve unique. https://attack.mitre.org/
6. **Documentation du constructeur ou du fournisseur** : guide de configuration IDS/IPS, gestion du mode inline, limites de débit, journalisation, procédure de mise à jour et retour arrière de la version réellement installée.

Les commandes et paramètres de configuration évoluent selon les versions. Utilise la documentation de la version présente dans ton laboratoire avant d’appliquer un exemple sur un équipement réel.
