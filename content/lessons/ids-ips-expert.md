# IDS / IPS et DPI — Expert

**Niveau :** EXPERT

Ce cours poursuit les niveaux Débutant et Intermédiaire. Il suppose que les notions d’IDS passif, d’IPS en ligne, de signatures, de faux positifs, de réassemblage TCP et d’inspection applicative sont déjà connues. Le travail expert consiste maintenant à concevoir un dispositif défendable à l’échelle d’une infrastructure réelle : sélectionner les points d’observation, prouver la couverture, préserver la fidélité des flux, faire évoluer les règles avec maîtrise, dimensionner l’inspection, interpréter les angles morts et organiser une réponse qui ne transforme pas un incident de sécurité en panne de production.

Les exemples utilisent surtout Suricata, Zeek, Linux, Wireshark et des fonctions réseau génériques. Les commandes et paramètres sont des modèles de laboratoire : vérifie les versions, les noms d’interfaces, la syntaxe exacte et les politiques locales avant de les adapter. Les schémas sont en SVG et CSS pur ; aucun JavaScript n’est nécessaire dans le Markdown. Ils utilisent des libellés séparés, une largeur minimale lisible et un conteneur défilant horizontalement pour éviter les chevauchements sur petit écran.

> **Analogie** : Un dispositif IDS/IPS expert ressemble à une chaîne de contrôle industriel. Les capteurs mesurent, le moteur d’analyse interprète, la politique décide et les actionneurs appliquent éventuellement la décision. Une mesure absente, un capteur mal placé, une horloge décalée ou un actionneur trop agressif peut invalider toute la chaîne, même si chaque composant paraît fonctionner seul.

---

## 1. Théorie et modèles d’inspection

### 1.1 Partir des objectifs de détection, pas du produit

Une architecture sérieuse commence par les questions auxquelles elle doit répondre. Souhaite-t-on détecter une exploitation Web, un déplacement latéral, une exfiltration, un protocole non autorisé, une commande de contrôle, un scan interne, un transfert suspect ou une dérive de politique ? Ces objectifs ne requièrent pas nécessairement les mêmes capteurs ni les mêmes preuves.

Une signature réseau est performante lorsqu’un indicateur stable existe dans le trafic observable : séquence de protocole, structure de requête, motif de payload ou comportement de session. Une détection comportementale examine plutôt l’écart par rapport à une référence : fréquence, destination inhabituelle, volume de données, échecs répétés ou relations entre hôtes. Une analyse de sécurité réseau comme Zeek produit des événements riches et structurés qui peuvent alimenter la chasse et la corrélation ; elle n’est pas, à elle seule, un IPS inline capable de jeter le paquet. Suricata peut fonctionner en analyse passive ou dans des modes inline, selon son intégration. Ces rôles sont complémentaires plutôt qu’interchangeables. [1][2]

Définis chaque objectif par six éléments : actif protégé, point réseau concerné, comportement à identifier, données qui le prouvent, décision attendue et impact maximal d’une erreur. Pour chaque cas, précise si la détection doit déclencher une alerte, une investigation, une limitation temporaire ou un blocage automatique. Le niveau de confiance nécessaire à une action irréversible doit être supérieur à celui nécessaire à une simple collecte.

| Objectif | Signal utile | Capteur probable | Action initiale recommandée |
|---|---|---|---|
| Exploit d’une application exposée | Requête et contexte du protocole | IPS inline, WAF, NIDS | Alerte puis blocage si règle validée |
| Mouvement latéral interne | Connexions rares, authentifications et séquences | NDR/Zeek, EDR, journaux d’identité | Corrélation et investigation |
| Exfiltration | Volume, destinations, durée et type de session | NDR, proxy, DNS, DLP selon contexte | Enrichir, préserver les preuves, limiter au besoin |
| Protocole non autorisé | Décodage et comportement incompatibles avec la politique | NIDS/IPS et contrôle réseau | Alerter, puis appliquer une politique explicite |
| Saturation de capteur | Dropped packets, queues, pertes d’ingestion | Supervision IDS et système | Restaurer la visibilité avant de conclure à l’absence d’attaque |

> **Piège :** Un tableau de bord vert ne prouve pas que la détection fonctionne. Il faut prouver que le capteur voit le trafic attendu, qu’il ne le perd pas, que ses règles sont chargées, que son horloge est cohérente et que les alertes arrivent jusqu’à l’équipe qui les traite.

### 1.2 Couverture : où voit-on réellement le trafic ?

La couverture est une propriété de l’architecture, pas seulement du nombre de sondes. Un port SPAN peut ne pas refléter tous les paquets lorsque le trafic miroir dépasse la capacité du port de sortie. Une capture au bord d’un réseau ne voit pas nécessairement les échanges entre deux machines d’un même VLAN. Une sonde sur un seul lien d’un routage ECMP peut ne voir qu’une partie des sessions. Une asymétrie de chemin peut présenter au capteur un seul sens d’une connexion, ce qui perturbe le suivi d’état, le réassemblage et la détection.

Établis une matrice de visibilité par zone et par sens. Pour chaque capteur, consigne les interfaces, les VLAN/VRF, les directions, les filtres d’acquisition, le taux de perte observé, la source horaire, la version du moteur, le jeu de règles et l’horodatage de la dernière validation. Associe aux flux des identifiants de segment ou des étiquettes de zone, sans transformer ces métadonnées en vérité absolue : un changement de routage ou de NAT peut modifier les points d’observation.

### Schéma 1 — Architecture de capteurs et visibilité de bout en bout

<style>
.ids-expert-diagram{margin:1.5rem 0 2rem;max-width:100%;overflow-x:auto;overscroll-behavior-x:contain;border:1px solid #3f3f46;border-radius:1rem;background:#18181b;color:#e4e4e7;padding:.75rem}
.ids-expert-diagram svg{display:block;width:100%;min-width:900px;height:auto;font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
.ids-expert-diagram .node{fill:#27272a;stroke:#71717a;stroke-width:1.5}
.ids-expert-diagram .node-blue{fill:#172554;stroke:#60a5fa;stroke-width:1.6}
.ids-expert-diagram .node-green{fill:#052e16;stroke:#4ade80;stroke-width:1.6}
.ids-expert-diagram .node-amber{fill:#451a03;stroke:#fbbf24;stroke-width:1.6}
.ids-expert-diagram .label{fill:#f4f4f5;font-size:15px;font-weight:700;text-anchor:middle}
.ids-expert-diagram .sub{fill:#d4d4d8;font-size:12px;text-anchor:middle}
.ids-expert-diagram .muted{fill:#a1a1aa;font-size:12px;text-anchor:middle}
.ids-expert-diagram .route{fill:none;stroke:#71717a;stroke-width:3}
.ids-expert-diagram .flow{fill:none;stroke-width:3.2;stroke-dasharray:9 10;animation:idsExpertFlow 1.5s linear infinite}
.ids-expert-diagram .flow-blue{stroke:#60a5fa}
.ids-expert-diagram .flow-green{stroke:#4ade80;animation-duration:1.2s}
.ids-expert-diagram .flow-amber{stroke:#fbbf24;animation-duration:1.8s}
.ids-expert-diagram .pulse{transform-box:fill-box;transform-origin:center;animation:idsExpertPulse 1.8s ease-in-out infinite}
.ids-expert-diagram .d1{animation-delay:.35s}.ids-expert-diagram .d2{animation-delay:.7s}.ids-expert-diagram .d3{animation-delay:1.05s}
.ids-expert-diagram .scan{animation:idsExpertScan 3.2s ease-in-out infinite}
@keyframes idsExpertFlow{to{stroke-dashoffset:-38}}
@keyframes idsExpertPulse{0%,100%{opacity:.45;transform:scale(.96)}50%{opacity:1;transform:scale(1.07)}}
@keyframes idsExpertScan{0%,100%{transform:translateX(0);opacity:.25}50%{transform:translateX(22px);opacity:1}}
@media(prefers-reduced-motion:reduce){.ids-expert-diagram *{animation:none!important;scroll-behavior:auto!important;transition:none!important}}
</style>

<div class="ids-expert-diagram">
<svg viewBox="0 0 1120 430" role="img" aria-label="Architecture de visibilité : le trafic traverse le routeur et le pare-feu vers les serveurs, une copie est envoyée vers une sonde passive, les événements vont au SIEM et la sonde est supervisée séparément.">
  <text x="24" y="28" fill="#93c5fd" font-size="14" font-weight="700">CHEMIN DE PRODUCTION ET CHEMIN D’OBSERVATION</text>
  <rect class="node-blue" x="28" y="86" width="150" height="78" rx="12"/><text class="label" x="103" y="116">Routeur</text><text class="sub" x="103" y="139">Bord / transit</text>
  <rect class="node" x="232" y="86" width="150" height="78" rx="12"/><text class="label" x="307" y="116">Pare-feu</text><text class="sub" x="307" y="139">Zones / NAT</text>
  <rect class="node-green" x="436" y="86" width="170" height="78" rx="12"/><text class="label" x="521" y="116">Switch cœur</text><text class="sub" x="521" y="139">VLAN / SPAN ou TAP</text>
  <rect class="node" x="672" y="86" width="168" height="78" rx="12"/><text class="label" x="756" y="116">Serveurs</text><text class="sub" x="756" y="139">Applications / données</text>
  <rect class="node-blue" x="450" y="260" width="190" height="72" rx="12"/><text class="label" x="545" y="290">Sonde NIDS</text><text class="sub" x="545" y="312">Moteur, règles, compteurs</text>
  <rect class="node-amber" x="768" y="260" width="176" height="72" rx="12"/><text class="label" x="856" y="290">Collecteur / SIEM</text><text class="sub" x="856" y="312">Événements corrélés</text>
  <rect class="node" x="968" y="86" width="126" height="78" rx="12"/><text class="label" x="1031" y="116">Supervision</text><text class="sub" x="1031" y="139">Santé capteur</text>
  <path class="route" d="M178 125 H232 M382 125 H436 M606 125 H672 M840 125 H968"/><path class="flow flow-blue" d="M180 125 H230 M384 125 H434 M608 125 H670"/>
  <path class="route" d="M521 164 V220 H545 V260"/><path class="flow flow-green" d="M521 164 V220 H545 V258"/>
  <path class="route" d="M640 296 H768"/><path class="flow flow-amber" d="M642 296 H766"/>
  <path class="route" d="M856 260 V212 H1031 V164"/><path class="flow flow-amber" d="M856 258 V212 H1031 V166"/>
  <text class="sub" x="312" y="200">Flux applicatif</text><text class="sub" x="553" y="240">Copie de trafic</text><text class="sub" x="705" y="282">Alertes / logs</text>
  <circle class="pulse" cx="198" cy="125" r="5" fill="#60a5fa"/><circle class="pulse d1" cx="406" cy="125" r="5" fill="#60a5fa"/><circle class="pulse d2" cx="622" cy="125" r="5" fill="#4ade80"/><circle class="pulse d3" cx="700" cy="296" r="5" fill="#fbbf24"/>
  <text class="muted" x="560" y="384">Une sonde passive observe une copie ; elle ne bloque pas le paquet d’origine.</text>
  <text class="muted" x="560" y="405">La supervision doit suivre pertes de capture, CPU, mémoire, horloge et pipeline d’alertes.</text>
</svg>
</div>

> **Astuce :** Utilise des captures de référence et des compteurs du commutateur pour prouver la couverture. Une règle qui ne déclenche jamais peut être mal conçue, mais peut aussi être placée sur un point qui ne reçoit pas le trafic concerné.

### 1.3 Passif, inline, proxy et télémétrie : ne pas confondre les garanties

Le mode passif sert à observer, à enregistrer et à investiguer. L’IPS inline peut appliquer une décision avant le passage du trafic, mais il devient une dépendance du chemin de production. Un proxy ou un WAF termine parfois la connexion et reconstruit une nouvelle session : cette architecture offre un contexte applicatif différent de celui d’une sonde qui ne voit que les paquets. La télémétrie de flux, les journaux applicatifs et les événements de l’hôte complètent la vision réseau.

Le choix doit donc être fait flux par flux. Les flux critiques à faible latence peuvent nécessiter une stratégie de détection plus prudente. Les applications exposées, bien caractérisées et couvertes par des règles validées peuvent bénéficier d’un blocage inline. Les segments où l’impact d’un faux blocage est majeur peuvent commencer en alerte seule. En environnement industriel, médical ou embarqué, les contraintes de disponibilité et les conséquences de sécurité physique doivent être analysées avec les propriétaires du système.

| Mode | Avantage principal | Risque principal | Test obligatoire |
|---|---|---|---|
| NIDS passif | Pas de dépendance directe du trajet | Perte de copie ou visibilité partielle | Comparer source, destination et compteurs de perte |
| IPS inline | Blocage immédiat | Latence, bypass, panne de chemin ou faux blocage | Test de débit, panne d’alimentation, fail-open/fail-closed |
| Proxy/WAF | Contexte applicatif riche | Compatibilité, terminaison TLS, comportement applicatif modifié | Tests de protocole et de bout en bout |
| NDR/Zeek | Corrélation temporelle et métadonnées riches | Dépendance aux données et à l’analyse différée | Validation des logs, horodatages et trous de capture |

---

## 2. Reconstruction des flux et résistance aux ambiguïtés

### 2.1 Le paquet capturé n’est pas toujours la session vue par l’application

Les signatures réseau travaillent sur des données observées. L’application reçoit cependant une séquence interprétée par sa pile TCP/IP et son parseur. La fragmentation IP, le réordonnancement TCP, les retransmissions, les segments qui se chevauchent, les anomalies de protocole et l’asymétrie peuvent créer des différences entre la représentation du capteur et celle de la destination.

Le réassemblage TCP regroupe les segments en un flux ordonné, dans la mesure où le capteur dispose des données nécessaires. Un IPS doit, en plus, prendre une décision suffisamment tôt pour laisser passer, bloquer ou modifier le trafic. La politique de résolution des segments qui se chevauchent doit être cohérente avec la pile de l’hôte ciblé. Si le moteur et la destination interprètent différemment les octets, une signature peut manquer un contenu malveillant ou bloquer une requête valide.

Les techniques d’évasion peuvent exploiter des différences de normalisation, des décalages entre parseurs, des champs contradictoires ou des flux incomplets. L’objectif défensif est de détecter l’ambiguïté, de la journaliser, de normaliser lorsque c’est supporté et de mesurer l’impact. Il ne faut pas considérer l’absence d’alerte comme une preuve que le trafic est bénin quand la capture est incomplète.

### Schéma 2 — Du paquet au flux reconstitué

<div class="ids-expert-diagram">
<svg viewBox="0 0 1120 380" role="img" aria-label="Quatre segments TCP arrivent dans le désordre, sont réordonnés par le moteur de flux, normalisés puis analysés comme une seule requête par le moteur de détection.">
  <text x="24" y="28" fill="#93c5fd" font-size="14" font-weight="700">RECONSTRUCTION DU FLUX ET NORMALISATION</text>
  <text class="sub" x="102" y="66">Capture brute</text><text class="sub" x="395" y="66">Ordonnancement TCP</text><text class="sub" x="690" y="66">Flux normalisé</text><text class="sub" x="976" y="66">Analyse</text>
  <rect class="node" x="25" y="88" width="155" height="48" rx="8"/><text class="label" x="102" y="108">Segment 3</text><text class="sub" x="102" y="126">offset 1200</text>
  <rect class="node-blue" x="25" y="146" width="155" height="48" rx="8"/><text class="label" x="102" y="166">Segment 1</text><text class="sub" x="102" y="184">offset 0</text>
  <rect class="node" x="25" y="204" width="155" height="48" rx="8"/><text class="label" x="102" y="224">Segment 4</text><text class="sub" x="102" y="242">offset 1800</text>
  <rect class="node-blue" x="25" y="262" width="155" height="48" rx="8"/><text class="label" x="102" y="282">Segment 2</text><text class="sub" x="102" y="300">offset 600</text>
  <path class="flow flow-blue" d="M180 170 H265"/><path class="route" d="M265 170 H303"/>
  <rect class="node-green" x="303" y="98" width="185" height="160" rx="12"/><text class="label" x="395" y="128">Moteur de flux</text><text class="sub" x="395" y="155">ordre / ACK / fenêtre</text><text class="sub" x="395" y="178">réassemblage</text><text class="sub" x="395" y="201">timeouts / chevauchements</text><text class="sub" x="395" y="225">état de session</text>
  <path class="flow flow-green" d="M488 178 H555"/>
  <rect class="node-blue" x="555" y="126" width="230" height="105" rx="12"/><text class="label" x="670" y="156">Requête reconstituée</text><text class="sub" x="670" y="182">Méthode + cible + en-têtes</text><text class="sub" x="670" y="204">et corps si disponible</text>
  <path class="flow flow-amber" d="M785 178 H865"/>
  <rect class="node-amber" x="865" y="126" width="220" height="105" rx="12"/><text class="label" x="975" y="156">Moteur de détection</text><text class="sub" x="975" y="182">Signature / anomalie</text><text class="sub" x="975" y="204">alerte / drop / enrichissement</text>
  <text class="muted" x="560" y="348">Un flux incomplet ou interprété différemment par le capteur et l’hôte</text><text class="muted" x="560" y="366">doit être traité comme une limite de confiance, pas comme une absence de menace.</text>
  <circle class="pulse" cx="217" cy="170" r="6" fill="#60a5fa"/><circle class="pulse d1" cx="520" cy="178" r="6" fill="#4ade80"/><circle class="pulse d2" cx="824" cy="178" r="6" fill="#fbbf24"/>
</svg>
</div>

### 2.2 Évasion, normalisation et source de vérité

Une bonne configuration doit rendre explicite le traitement des données invalides ou ambiguës : paquet malformé, checksum incorrect, connexion asymétrique, flux tronqué, fragmentation excessive, timeout de réassemblage ou dépassement de mémoire. Selon la politique et le mode de déploiement, le moteur peut journaliser, ignorer, réinitialiser l’état, rejeter ou bloquer. Les comportements précis dépendent du moteur, de sa version et du mode IDS/IPS.

Pour les applications critiques, compare les décisions du capteur avec le comportement observé au serveur. Une capture côté client, une capture côté serveur et les journaux de l’application peuvent révéler qu’une connexion a suivi un autre chemin, que le NAT a modifié l’identité apparente ou que la session a été interrompue avant l’étape supposée. La capture doit respecter les obligations de confidentialité ; limite son périmètre, protège son stockage et fixe une durée de conservation.

> **Danger :** Ne teste jamais une technique d’évasion sur un réseau de production sans autorisation formelle, plan de retour arrière et supervision. Les laboratoires de ce cours doivent utiliser des captures fournies, des machines isolées ou un environnement expressément approuvé.

### 2.3 Validation d’une règle à partir de plusieurs points de vue

Une alerte exploitable doit être corroborée. Commence par valider l’horodatage et le sens du flux ; identifie le capteur, le VLAN ou la zone ; vérifie la règle, la révision du jeu de règles et l’action réelle. Recherche ensuite les paquets ou métadonnées qui ont déclenché la signature, les événements voisins du même flux, les connexions vers l’hôte, les journaux de l’application et les actions du pare-feu. Une différence entre l’alerte et le comportement de l’hôte peut être due à un faux positif, à une règle trop large, à un flux incomplet ou à un parseur divergent.

---

## 3. Moteurs de détection et gouvernance des règles

### 3.1 Signature, protocole, comportement et corrélation

Une détection basée sur une signature reconnaît une séquence ou une structure connue. Elle est généralement explicable et peut être très efficace quand l’indicateur est stable. Elle est plus fragile lorsque le contenu varie, est chiffré, compressé, fragmenté, encodé autrement ou modifié par un intermédiaire.

La détection protocolaire vérifie si les messages, champs et séquences ont un sens selon le protocole. Elle peut repérer des méthodes inattendues, des commandes invalides, des anomalies de séquence ou des usages incompatibles avec la politique. L’analyse comportementale détecte des écarts dans la fréquence, la destination, le volume, la durée ou la relation entre hôtes. La corrélation relie plusieurs événements dans le temps — par exemple une résolution DNS inhabituelle, une connexion sortante nouvelle et un transfert volumineux — afin de produire une hypothèse d’incident plus solide.

Chaque approche a ses limites. Une signature simple peut être contournée par une variante ; une anomalie statistique peut signaler une activité métier normale ; une corrélation peut propager une erreur si les identifiants ou horloges ne sont pas fiables. Combine les signaux, mais conserve les preuves sources et le chemin logique qui a conduit à la conclusion.

### Schéma 3 — Plusieurs signaux vers une décision justifiable

<div class="ids-expert-diagram">
<svg viewBox="0 0 1120 400" role="img" aria-label="Les signatures, les anomalies de protocole et les anomalies comportementales convergent vers une corrélation, un enrichissement de contexte puis une décision graduée.">
  <text x="24" y="28" fill="#93c5fd" font-size="14" font-weight="700">DÉTECTION MULTI-SIGNAL ET DÉCISION GRADUÉE</text>
  <rect class="node-blue" x="25" y="78" width="205" height="67" rx="10"/><text class="label" x="127" y="105">Signatures</text><text class="sub" x="127" y="126">motifs / règles versionnées</text>
  <rect class="node-green" x="25" y="166" width="205" height="67" rx="10"/><text class="label" x="127" y="193">Protocole</text><text class="sub" x="127" y="214">séquence / conformité</text>
  <rect class="node-amber" x="25" y="254" width="205" height="67" rx="10"/><text class="label" x="127" y="281">Comportement</text><text class="sub" x="127" y="302">baseline / écart / fréquence</text>
  <path class="flow flow-blue" d="M230 112 H310 L360 190"/><path class="flow flow-green" d="M230 200 H360"/><path class="flow flow-amber" d="M230 288 H310 L360 210"/>
  <rect class="node" x="360" y="135" width="190" height="132" rx="12"/><text class="label" x="455" y="164">Corrélation</text><text class="sub" x="455" y="188">temps / identité / zone</text><text class="sub" x="455" y="210">contexte métier</text><text class="sub" x="455" y="232">preuves conservées</text>
  <path class="flow flow-blue" d="M550 201 H620"/>
  <rect class="node-blue" x="620" y="148" width="190" height="106" rx="12"/><text class="label" x="715" y="177">Qualification</text><text class="sub" x="715" y="200">confiance / impact</text><text class="sub" x="715" y="221">propriétaire / urgence</text>
  <path class="flow flow-green" d="M810 201 H858"/>
  <rect class="node-green" x="858" y="72" width="230" height="60" rx="10"/><text class="label" x="973" y="98">Journaliser / enrichir</text><text class="sub" x="973" y="118">faible certitude</text>
  <rect class="node-amber" x="858" y="160" width="230" height="60" rx="10"/><text class="label" x="973" y="186">Investigation</text><text class="sub" x="973" y="206">suspicion crédible</text>
  <rect x="858" y="248" width="230" height="60" rx="10" fill="#450a0a" stroke="#f87171" stroke-width="1.6"/><text class="label" x="973" y="274">Prévention contrôlée</text><text class="sub" x="973" y="294">confiance élevée / risque validé</text>
  <path class="route" d="M838 201 H845 V102 H858 M845 190 H858 M845 201 V278 H858"/>
  <text class="muted" x="560" y="350">Ne fais pas d’une alerte isolée une certitude : garde le score, les preuves, le propriétaire</text><text class="muted" x="560" y="369">et les conditions ayant autorisé une action automatique.</text>
  <circle class="pulse" cx="287" cy="151" r="6" fill="#60a5fa"/><circle class="pulse d1" cx="585" cy="201" r="6" fill="#4ade80"/><circle class="pulse d2" cx="835" cy="201" r="6" fill="#fbbf24"/>
</svg>
</div>

### 3.2 Gouvernance des signatures : source, version, contexte et retour arrière

Les signatures doivent être gérées comme du code de production. Chaque ensemble possède une provenance, une version, une date, une description, un niveau de confiance, un périmètre de test et une procédure de retour arrière. Conserve l’identifiant de signature et la révision dans les journaux, sinon une enquête menée plusieurs jours plus tard peut être impossible à reproduire après une mise à jour de règles.

Le processus recommandé est : récupérer les règles d’une source de confiance, vérifier l’intégrité et les versions, exécuter une vérification syntaxique, rejouer un corpus de captures représentatif, mesurer les alertes et la charge, déployer d’abord sur un capteur de test ou en alerte seule, comparer avec le trafic métier, puis activer le blocage de façon ciblée. Un changement de politique doit avoir un propriétaire et un plan de restauration. Une règle très bruyante ne doit pas être désactivée à l’aveugle : il faut comprendre si le problème vient d’un seuil trop large, d’un parseur, d’un flux légitime particulier ou d’une vraie activité menaçante.

| Métadonnée d’une règle | Pourquoi elle compte |
|---|---|
| Identifiant et révision | Retrouver exactement la règle ayant déclenché l’événement |
| Source et licence | Comprendre l’origine et les conditions d’utilisation |
| Actif ou service ciblé | Éviter d’appliquer le mauvais profil à une application |
| Seuil et fenêtre temporelle | Maîtriser la sensibilité et le bruit |
| Action configurée | Distinguer alert, drop, reject ou simple journalisation |
| Résultat de tests | Prouver détection attendue et absence de régression connue |
| Date d’expiration ou de revue | Éviter la dette de règles anciennes |

> **Piège :** Une règle qui contient `drop` dans le fichier n’est pas nécessairement en train de bloquer en production. Il faut vérifier le mode d’exécution, l’interface, l’intégration inline, le chargement effectif de la règle, les compteurs et les journaux du moteur.

### 3.3 Exemple pédagogique de règles Suricata

Les règles suivantes montrent la forme et les précautions de validation. Elles sont destinées à un fichier de laboratoire, pas à une installation de production sans test. Les adresses, ports et contenus sont factices ou génériques ; une règle de détection ne doit pas être interprétée comme un exploit opérationnel.

```text
# Alerter sur une chaîne de test dans un trafic HTTP de laboratoire.
alert http any any -> $HOME_NET any (msg:"LAB HTTP chaîne de test"; flow:established,to_server; http.uri; content:"/lab-marker"; startswith; sid:9900001; rev:1;)

# Journaliser un DNS de test vers un domaine réservé au laboratoire.
alert dns any any -> $HOME_NET any (msg:"LAB DNS suffixe de test"; dns.query; content:"training.invalid"; endswith; sid:9900002; rev:1;)
```

Les noms exacts de mots-clés, le support des buffers applicatifs et la manière de lancer le moteur varient selon la version. Vérifie la règle avec la commande de test de configuration de la version utilisée, puis rejoue un PCAP de laboratoire. Vérifie qu’un paquet répondant au motif déclenche exactement la règle et qu’un trafic proche mais légitime ne la déclenche pas. Pour un IPS inline, commence avec l’action `alert`, observe le comportement, puis ne convertis en blocage qu’après revue explicite.

Exemple de validation statique, à adapter au chemin d’installation :

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml
sudo suricata -r ./laboratoire-http.pcap -c /etc/suricata/suricata.yaml -l ./sortie-test
```

Les noms `laboratoire-http.pcap` et `sortie-test` représentent des fichiers du laboratoire. N’exécute pas le mode inline sur une interface de production pour simplement tester une règle.

### 3.4 Mesurer la qualité d’une détection

La qualité de détection ne se réduit pas au nombre d’alertes. Une règle peut produire beaucoup d’événements en trouvant très peu de véritables incidents ; une règle silencieuse peut être exacte, inutile ou aveugle. Évalue les règles sur un corpus étiqueté avec une classe attendue, des fenêtres temporelles définies et des données suffisamment représentatives. Mesure précision, rappel, volume d’événements, délai de détection, faux positifs, faux négatifs et coût de traitement.

| Mesure | Formule conceptuelle | Question opérationnelle |
|---|---|---|
| Précision | vrais positifs / alertes positives | Quelle part des alertes mérite réellement une investigation ? |
| Rappel | vrais positifs / menaces réellement présentes | Quelle part des événements menaçants connus a été détectée ? |
| Taux de faux positifs | faux positifs / événements légitimes | Quel bruit la règle ajoute-t-elle à l’équipe ? |
| Délai de détection | temps de première détection − début observé | L’alerte arrive-t-elle assez tôt pour agir ? |
| Coût de traitement | CPU, mémoire, débit, stockage et temps analyste | La détection reste-t-elle soutenable à charge réelle ? |

Ces chiffres dépendent de la qualité du corpus. L’absence de cas négatifs variés donne une mesure de précision trompeuse ; une capture trop courte ne permet pas d’évaluer le comportement temporel. Décris donc la population testée, la période et les limites des résultats.

---

## 4. DPI, chiffrement TLS et limites de visibilité

### 4.1 Ce qu’un capteur peut observer sous TLS

Lorsque TLS est utilisé correctement, le contenu applicatif est chiffré sur le lien où la capture est effectuée. Selon la version, la négociation et les extensions employées, certains éléments de métadonnées peuvent rester visibles, être partiellement visibles ou être protégés. Les adresses IP, ports, tailles et temporalités des paquets restent souvent observables ; cela ne signifie pas que le capteur peut lire l’URI, le corps HTTP ou les identifiants transmis dans la session.

Pour inspecter le contenu, il faut un point où le trafic est légitimement déchiffré : proxy d’entreprise, reverse proxy, terminaison TLS, télémétrie de l’application ou mécanisme approuvé qui fournit les éléments nécessaires à l’analyse. Une interception TLS doit respecter les exigences juridiques, la vie privée, les politiques internes, l’épinglage de certificats éventuel, les applications sensibles et la gestion des clés. Le déchiffrement accroît la surface de risque : les clés, secrets et flux en clair deviennent des actifs à protéger.

### Schéma 4 — Visibilité TLS selon le point d’observation

<div class="ids-expert-diagram">
<svg viewBox="0 0 1120 390" role="img" aria-label="Le capteur hors chemin voit les métadonnées et le contenu chiffré ; une terminaison TLS autorisée produit un segment en clair visible par un capteur interne soumis à une politique de sécurité.">
  <text x="24" y="28" fill="#93c5fd" font-size="14" font-weight="700">TLS : LE POINT DE CAPTURE DÉTERMINE LA VISIBILITÉ</text>
  <rect class="node-blue" x="28" y="86" width="155" height="70" rx="12"/><text class="label" x="105" y="114">Client</text><text class="sub" x="105" y="136">Navigateur / API</text>
  <rect class="node" x="268" y="86" width="200" height="70" rx="12"/><text class="label" x="368" y="114">Lien TLS chiffré</text><text class="sub" x="368" y="136">Payload non lisible ici</text>
  <rect class="node-amber" x="556" y="86" width="200" height="70" rx="12"/><text class="label" x="656" y="114">Terminaison TLS</text><text class="sub" x="656" y="136">Proxy / reverse proxy</text>
  <rect class="node-green" x="845" y="86" width="225" height="70" rx="12"/><text class="label" x="957" y="114">Application</text><text class="sub" x="957" y="136">HTTP déchiffré à ce point</text>
  <path class="route" d="M183 121 H268 M468 121 H556 M756 121 H845"/><path class="flow flow-blue" d="M185 121 H266 M470 121 H554"/><path class="flow flow-green" d="M758 121 H843"/>
  <rect class="node-blue" x="236" y="238" width="270" height="72" rx="12"/><text class="label" x="371" y="265">Sonde réseau externe</text><text class="sub" x="371" y="287">IP, port, tailles, timing, métadonnées</text>
  <rect class="node-green" x="675" y="238" width="300" height="72" rx="12"/><text class="label" x="825" y="265">Inspection autorisée interne</text><text class="sub" x="825" y="287">URI, en-têtes et corps selon le point</text>
  <path class="route" d="M368 156 V211 H371 V238 M656 156 V211 H825 V238"/><path class="flow flow-blue" d="M368 156 V211 H371 V236"/><path class="flow flow-green" d="M656 156 V211 H825 V236"/>
  <text class="muted" x="560" y="348">Chiffré ne signifie pas invisible ; visible ne signifie pas déchiffré.</text><text class="muted" x="560" y="368">Documenter les champs disponibles, le droit d’inspection et les secrets manipulés.</text>
  <circle class="pulse" cx="218" cy="121" r="6" fill="#60a5fa"/><circle class="pulse d1" cx="514" cy="121" r="6" fill="#60a5fa"/><circle class="pulse d2" cx="790" cy="121" r="6" fill="#4ade80"/>
</svg>
</div>

### 4.2 Trois stratégies réalistes

**Métadonnées seulement.** Le capteur corrèle IP, port, durée, tailles, direction, certificat disponible, DNS et caractéristiques temporelles. Cette approche conserve le chiffrement de bout en bout mais ne fournit pas le contenu de l’application. Des règles fondées uniquement sur le nom de domaine ou l’adresse IP doivent tenir compte des CDN, des services partagés, du DNS chiffré et des infrastructures mutualisées.

**Inspection à la terminaison.** Le reverse proxy, le WAF ou l’application voit le contenu en clair lorsqu’il termine la session. L’avantage est une connaissance applicative précise. La limite est que la session entre le proxy et le serveur peut être différente de celle du client, et que les journaux doivent être corrélés avec les identifiants de requête, l’heure et les adresses après NAT.

**Déchiffrement intermédiaire contrôlé.** Un dispositif d’inspection déchiffre puis rechiffre le trafic selon une politique. Il faut évaluer la confiance dans l’autorité de certification, le stockage des clés, l’authentification mutuelle, les applications épinglant leur certificat, les données sensibles, les exclusions documentées et la façon dont les secrets et contenus en clair sont exposés au personnel et aux outils.

> **Danger :** Ne désactive pas la validation TLS pour « faire fonctionner » l’inspection. Une dégradation silencieuse de la validation des certificats peut transformer le capteur en point d’interception vulnérable. Teste la chaîne de confiance, les certificats, les suites prises en charge et les exclusions approuvées.

### 4.3 HTTP/2, HTTP/3 et protocoles évolutifs

La détection doit connaître les protocoles réellement observés. Un parseur HTTP/1.1 ne permet pas d’inférer automatiquement le contenu de HTTP/2 ou HTTP/3. La compression des en-têtes, le multiplexage, QUIC, les versions TLS récentes et les mécanismes de chiffrement des métadonnées modifient l’emplacement et le degré de visibilité. Le support varie selon le produit et la version ; vérifie dans la documentation la manière dont le moteur détecte, journalise ou limite l’inspection des protocoles concernés.

Une stratégie durable distingue les fonctions de contrôle du canal (pare-feu, flux, identité, destination), les fonctions applicatives (proxy/WAF), l’analyse des hôtes et la télémétrie de session. Le DPI doit être présenté comme une capacité bornée par les protocoles et les points de déchiffrement réellement en place.

---

## 5. Performance, files d’attente et intégrité de capture

### 5.1 Du débit théorique à la charge réelle

Le débit en bit/s ne suffit pas pour dimensionner un IDS/IPS. Un trafic avec beaucoup de petits paquets peut épuiser le traitement par paquet avant de saturer la bande passante. Des sessions longues ou multiplexées peuvent accroître l’état conservé. Des règles coûteuses, des expressions régulières complexes, un grand nombre de buffers applicatifs ou l’inspection de fichiers peuvent solliciter CPU, mémoire et stockage. La performance doit être testée avec un profil proche du trafic réel, pas seulement avec un débit synthétique moyen.

Surveille au minimum : paquets reçus, paquets abandonnés, taux de capture, paquets traités, files d’attente, saturation des files NIC, débit de sessions, nombre de flux actifs, utilisation mémoire, pression sur les tables d’état, temps de traitement, latence introduite en inline, débit d’alertes et délai d’ingestion SIEM. Un zéro dans le compteur des alertes peut correspondre à une absence de menace ou à une sonde qui ne voit plus les paquets.

### Schéma 5 — Le goulot d’étranglement et les pertes de capture

<div class="ids-expert-diagram">
<svg viewBox="0 0 1120 390" role="img" aria-label="La NIC reçoit les paquets, une file alimente plusieurs workers d’inspection, puis un exporteur envoie les événements au SIEM. Les compteurs de perte sont surveillés à chaque étape.">
  <text x="24" y="28" fill="#93c5fd" font-size="14" font-weight="700">CHAÎNE DE PERFORMANCE — COMPTER LES PERTES À CHAQUE ÉTAPE</text>
  <rect class="node-blue" x="26" y="97" width="152" height="76" rx="10"/><text class="label" x="102" y="125">NIC / capture</text><text class="sub" x="102" y="147">reçus / drops</text>
  <rect class="node-amber" x="235" y="97" width="160" height="76" rx="10"/><text class="label" x="315" y="125">Ring / queue</text><text class="sub" x="315" y="147">backlog / overflow</text>
  <rect class="node-green" x="452" y="54" width="170" height="62" rx="10"/><text class="label" x="537" y="80">Worker A</text><text class="sub" x="537" y="100">flux hashés</text>
  <rect class="node-green" x="452" y="137" width="170" height="62" rx="10"/><text class="label" x="537" y="163">Worker B</text><text class="sub" x="537" y="183">parseurs / signatures</text>
  <rect class="node-green" x="452" y="220" width="170" height="62" rx="10"/><text class="label" x="537" y="246">Worker N</text><text class="sub" x="537" y="266">sessions / mémoire</text>
  <rect class="node-blue" x="687" y="137" width="175" height="76" rx="10"/><text class="label" x="774" y="165">Événements</text><text class="sub" x="774" y="187">EVE / buffer export</text>
  <rect class="node-amber" x="926" y="137" width="164" height="76" rx="10"/><text class="label" x="1008" y="165">SIEM</text><text class="sub" x="1008" y="187">ingestion / index</text>
  <path class="route" d="M178 135 H235 M395 135 H425 V85 H452 M425 135 H452 M425 135 V251 H452 M622 85 H650 V175 H687 M622 168 H687 M622 251 H650 V175 M862 175 H926"/>
  <path class="flow flow-blue" d="M180 135 H233 M397 135 H423 V85 H450 M624 168 H685 M864 175 H924"/>
  <text class="sub" x="206" y="118">PPS</text><text class="sub" x="408" y="305">distribution équilibrée par session</text><text class="sub" x="777" y="238">backlog export</text><text class="sub" x="1008" y="238">retard d’ingestion</text>
  <rect x="235" y="330" width="160" height="32" rx="7" fill="#450a0a" stroke="#f87171"/><text class="sub" x="315" y="351" fill="#fecaca">Alarme : drops en hausse</text>
  <rect x="687" y="330" width="403" height="32" rx="7" fill="#172554" stroke="#60a5fa"/><text class="sub" x="888" y="351">Sonde saine ≠ chaîne d’alertes saine</text>
  <circle class="pulse" cx="205" cy="135" r="6" fill="#60a5fa"/><circle class="pulse d1" cx="431" cy="135" r="6" fill="#fbbf24"/><circle class="pulse d2" cx="653" cy="175" r="6" fill="#4ade80"/><circle class="pulse d3" cx="892" cy="175" r="6" fill="#fbbf24"/>
</svg>
</div>

### 5.2 Distribution du trafic et affinité de flux

Les architectures multi-cœurs et clusters répartissent souvent le trafic entre workers. La stratégie doit préserver l’affinité d’une session : si les paquets d’une même connexion sont dispatchés à des workers indépendants sans partage d’état suffisant, chacun peut ne voir qu’une partie du flux. Le load balancing par hash de flux, les files NIC, les RSS, les mécanismes de capture et les limites de synchronisation influencent la qualité de l’analyse.

Le scaling horizontal apporte de la capacité mais augmente la complexité : configuration cohérente, versions homogènes, distribution uniforme, état de session, règles identiques, horloges alignées et agrégation des alertes. Une distribution déséquilibrée peut laisser un worker saturé alors que la moyenne CPU du cluster semble faible. Examine les percentiles et les compteurs par queue/worker, pas seulement une moyenne globale.

### 5.3 Choix fail-open ou fail-closed

Un dispositif inline peut, selon l’équipement, laisser passer le trafic en cas de panne (fail-open), le bloquer (fail-closed), ou utiliser un bypass matériel. Le choix n’est pas seulement technique. Fail-open favorise souvent la disponibilité mais réduit temporairement la prévention ; fail-closed maintient le principe de blocage mais peut couper un service critique. Certaines architectures utilisent un mode dégradé où les règles les plus sûres restent appliquées tandis que l’inspection profonde est contournée, mais ce comportement doit être confirmé et testé.

### Schéma 6 — Réaction en cas de panne d’une sonde inline

<div class="ids-expert-diagram">
<svg viewBox="0 0 1120 350" role="img" aria-label="Deux chemins de secours : le mode fail-open contourne la fonction d’inspection pour préserver la disponibilité ; le mode fail-closed arrête ou bloque les flux. Le choix dépend de l’analyse des risques.">
  <text x="24" y="28" fill="#93c5fd" font-size="14" font-weight="700">PANNES INLINE : LE COMPORTEMENT DOIT ÊTRE EXPLICITE</text>
  <rect class="node-blue" x="25" y="105" width="145" height="70" rx="10"/><text class="label" x="97" y="132">Réseau amont</text><text class="sub" x="97" y="154">trafic entrant</text>
  <rect class="node-amber" x="255" y="105" width="190" height="70" rx="10"/><text class="label" x="350" y="132">IPS en panne</text><text class="sub" x="350" y="154">état / alimentation</text>
  <path class="route" d="M170 140 H255"/><path class="flow flow-blue" d="M172 140 H253"/>
  <rect class="node-green" x="540" y="64" width="235" height="76" rx="10"/><text class="label" x="657" y="94">FAIL-OPEN</text><text class="sub" x="657" y="116">bypass / disponibilité</text>
  <rect x="540" y="196" width="235" height="76" rx="10" fill="#450a0a" stroke="#f87171" stroke-width="1.6"/><text class="label" x="657" y="226">FAIL-CLOSED</text><text class="sub" x="657" y="248">blocage / prévention</text>
  <path class="flow flow-green" d="M445 125 H492 V102 H540"/><path class="flow flow-amber" d="M445 155 H492 V234 H540"/>
  <rect class="node" x="863" y="64" width="224" height="76" rx="10"/><text class="label" x="975" y="94">Service maintenu</text><text class="sub" x="975" y="116">visibilité réduite</text>
  <rect class="node" x="863" y="196" width="224" height="76" rx="10"/><text class="label" x="975" y="226">Service interrompu</text><text class="sub" x="975" y="248">jusqu’au rétablissement</text>
  <path class="flow flow-green" d="M775 102 H861"/><path class="flow flow-amber" d="M775 234 H861"/>
  <text class="muted" x="560" y="315">Tester perte électrique, perte de lien, crash du processus, surcharge</text><text class="muted" x="560" y="333">et panne du collecteur ; documenter le comportement réel, pas seulement prévu.</text>
  <circle class="pulse" cx="212" cy="140" r="6" fill="#60a5fa"/><circle class="pulse d1" cx="511" cy="102" r="6" fill="#4ade80"/><circle class="pulse d2" cx="817" cy="234" r="6" fill="#fbbf24"/>
</svg>
</div>

> **Danger :** Ne change pas à distance le mode fail-open/fail-closed d’un équipement qui porte des flux critiques sans fenêtre de maintenance, test de perte de gestion et plan de restauration. Confirme aussi l’effet des sessions déjà établies pendant le basculement.

---

## 6. Capteurs distribués, NDR et corrélation SIEM

### 6.1 Moteur d’inspection et analyse de réseau sont complémentaires

Un moteur de signatures comme Suricata peut rechercher des motifs, analyser les protocoles et produire des alertes. Zeek se concentre sur des événements réseau structurés et des analyses stateful ; son moteur produit des événements neutres que les scripts et les politiques peuvent interpréter. Ces systèmes peuvent se compléter : un moteur repère une signature précise, tandis que l’analyse de réseau fournit un historique de connexions, de DNS, de certificats, de fichiers ou de transactions, selon la visibilité et la configuration. [1][2]

Ne force pas tous les cas d’usage dans un seul moteur. Le besoin peut être couvert par des signatures précises, du protocole, du comportement, les journaux de proxy, les logs d’identité, de l’EDR et des métadonnées de flux. Le SIEM corrèle les événements et organise les workflows ; il ne remplace pas un capteur qui a perdu ses paquets.

### 6.2 Horodatage, identité, NAT et qualité des données

La corrélation a besoin de temps cohérent et de champs stables. Configure une source horaire fiable pour les capteurs, collecteurs et équipements réseau. Mesure le décalage et l’état de synchronisation. Garde les horodatages d’origine ainsi que l’heure d’ingestion, car un buffer ou un backlog peut ajouter un retard important.

Le NAT complique l’attribution d’une adresse à un hôte. Pour corréler un événement capturé avant un firewall NAT avec un journal capturé après celui-ci, il faut des informations de translation horodatées et suffisamment précises, ainsi qu’un protocole de gestion des identifiants. Évite d’associer une alerte à un utilisateur sur la seule base d’une IP partagée. Les VPN, proxy, NAT opérateur, DHCP et adresses temporaires rendent l’identité réseau contextuelle.

### Schéma 7 — Corrélation entre réseau, identité, hôte et SIEM

<div class="ids-expert-diagram">
<svg viewBox="0 0 1120 400" role="img" aria-label="Les capteurs réseau, les journaux DNS/proxy, les événements d’identité et les alertes de l’hôte alimentent un collecteur qui normalise les horodatages, enrichit l’identité et construit une chronologie d’incident dans le SIEM.">
  <text x="24" y="28" fill="#93c5fd" font-size="14" font-weight="700">CORRÉLATION MULTI-SOURCE ET CHRONOLOGIE D’INCIDENT</text>
  <rect class="node-blue" x="25" y="75" width="200" height="58" rx="10"/><text class="label" x="125" y="100">Capteur réseau</text><text class="sub" x="125" y="119">Suricata / Zeek / flow</text>
  <rect class="node-green" x="25" y="150" width="200" height="58" rx="10"/><text class="label" x="125" y="175">DNS / Proxy</text><text class="sub" x="125" y="194">nom / requête / réponse</text>
  <rect class="node-amber" x="25" y="225" width="200" height="58" rx="10"/><text class="label" x="125" y="250">Identité</text><text class="sub" x="125" y="269">VPN / IAM / AAA</text>
  <rect class="node" x="25" y="300" width="200" height="58" rx="10"/><text class="label" x="125" y="325">Hôte / EDR</text><text class="sub" x="125" y="344">processus / fichiers</text>
  <rect class="node-blue" x="385" y="144" width="240" height="133" rx="12"/><text class="label" x="505" y="174">Collecteur / normalisation</text><text class="sub" x="505" y="199">horodatages source + ingestion</text><text class="sub" x="505" y="220">zone / NAT / hôte / utilisateur</text><text class="sub" x="505" y="241">qualité / doublons / pertes</text>
  <rect class="node-green" x="785" y="144" width="285" height="133" rx="12"/><text class="label" x="927" y="174">SIEM / chronologie</text><text class="sub" x="927" y="199">événements liés</text><text class="sub" x="927" y="220">hypothèse et preuves</text><text class="sub" x="927" y="241">assignation / réponse</text>
  <path class="flow flow-blue" d="M225 104 H305 V180 H385"/><path class="flow flow-green" d="M225 179 H385"/><path class="flow flow-amber" d="M225 254 H305 V240 H385"/><path class="flow flow-blue" d="M225 329 H305 V260 H385"/><path class="flow flow-green" d="M625 210 H785"/>
  <text class="muted" x="560" y="324">Conserver la provenance des données et les identifiants qui ont servi à la corrélation.</text><text class="muted" x="560" y="344">Une association probable doit rester différenciée d’une preuve directe.</text>
  <circle class="pulse" cx="270" cy="104" r="5" fill="#60a5fa"/><circle class="pulse d1" cx="340" cy="179" r="5" fill="#4ade80"/><circle class="pulse d2" cx="720" cy="210" r="5" fill="#fbbf24"/>
</svg>
</div>

### 6.3 Construire une détection multi-étape sans surcorréler

Une règle de corrélation doit définir sa fenêtre temporelle, ses clés de regroupement, son ordre, ses exceptions, son seuil, sa gravité et les preuves obligatoires. Par exemple, une résolution DNS inhabituelle, suivie d’une connexion nouvelle puis d’un transfert important peut justifier une investigation. Elle ne prouve pas nécessairement une exfiltration : sauvegarde, synchronisation, mise à jour ou tâche d’administration peuvent produire une séquence similaire.

Le but n’est pas de multiplier les alertes, mais de réduire le travail de l’analyste sans cacher l’incertitude. Conserve les événements composants, l’ordre chronologique et le score qui a déterminé la priorité. En cas d’action automatique, ajoute une limite de portée, une expiration, une liste d’exclusions approuvée et un mécanisme de validation humaine pour les actifs critiques.

---

## 7. Tuning, bruit, dérive et cycle de vie

### 7.1 Un processus de tuning contrôlé

Le tuning commence par une mesure, pas par la désactivation d’une règle. Regroupe les événements par signature, zone, service, version, hôte, source et heure. Compare la distribution avant et après le changement de règle. Identifie les applications légitimes qui déclenchent l’alerte, les chemins de réseau spécifiques et les modifications récentes de l’infrastructure. Ensuite, choisis une action minimale : préciser le protocole ou le service, ajouter un contexte négatif maîtrisé, ajuster un seuil, créer une exception très ciblée, passer provisoirement en alerte seule ou retirer la règle si elle n’apporte plus de valeur.

Toute exception doit posséder un responsable, une justification, une portée et une date de révision. Les exceptions fondées uniquement sur une adresse IP peuvent devenir obsolètes à la suite d’un renouvellement DHCP, d’un déplacement de service, d’un CDN ou d’un changement de NAT. Privilégie un identifiant de service stable, un contexte de protocole ou une règle d’actif lorsque c’est approprié.

### Schéma 8 — Boucle de tuning et prévention des régressions

<div class="ids-expert-diagram">
<svg viewBox="0 0 1120 385" role="img" aria-label="Boucle de gouvernance de règles : collecte des alertes, triage, hypothèse, test sur captures, revue de l’exception, déploiement progressif et mesure de la dérive.">
  <text x="24" y="28" fill="#93c5fd" font-size="14" font-weight="700">TUNING CONTRÔLÉ — UNE EXCEPTION DOIT RESTER AUDITABLE</text>
  <rect class="node-blue" x="32" y="82" width="180" height="66" rx="10"/><text class="label" x="122" y="108">1. Mesurer</text><text class="sub" x="122" y="129">volume / actifs / impact</text>
  <rect class="node" x="270" y="82" width="180" height="66" rx="10"/><text class="label" x="360" y="108">2. Qualifier</text><text class="sub" x="360" y="129">vrai / faux / ambigu</text>
  <rect class="node-green" x="508" y="82" width="180" height="66" rx="10"/><text class="label" x="598" y="108">3. Tester</text><text class="sub" x="598" y="129">PCAP + régression</text>
  <rect class="node-amber" x="746" y="82" width="180" height="66" rx="10"/><text class="label" x="836" y="108">4. Revoir</text><text class="sub" x="836" y="129">portée / expiration</text>
  <rect class="node-blue" x="746" y="225" width="180" height="66" rx="10"/><text class="label" x="836" y="251">5. Déployer</text><text class="sub" x="836" y="272">canary / alerte seule</text>
  <rect class="node-green" x="508" y="225" width="180" height="66" rx="10"/><text class="label" x="598" y="251">6. Vérifier</text><text class="sub" x="598" y="272">bruit / détection / CPU</text>
  <rect class="node" x="270" y="225" width="180" height="66" rx="10"/><text class="label" x="360" y="251">7. Documenter</text><text class="sub" x="360" y="272">version / responsable</text>
  <path class="flow flow-blue" d="M212 115 H268 M450 115 H506 M688 115 H744 M836 148 V223 M746 258 H690 M508 258 H452 M270 258 H122 V150"/>
  <text class="muted" x="560" y="333">Chaque changement doit être réversible et associé à des preuves.</text><text class="muted" x="560" y="352">Réévalue les exceptions après migration, changement d’application et mise à jour de règles.</text>
  <circle class="pulse" cx="239" cy="115" r="5" fill="#60a5fa"/><circle class="pulse d1" cx="479" cy="115" r="5" fill="#4ade80"/><circle class="pulse d2" cx="836" cy="185" r="5" fill="#fbbf24"/><circle class="pulse d3" cx="478" cy="258" r="5" fill="#4ade80"/>
</svg>
</div>

### 7.2 Détecter la dérive d’un profil

Une règle qui était précise peut devenir bruyante après un déploiement applicatif, une migration cloud, un changement de CDN, l’activation de HTTP/3 ou une modification des habitudes d’usage. Définis des seuils de dérive : augmentation du volume d’alertes, changement du ratio alertes confirmées, hausse du taux d’exception, baisse inattendue des événements ou hausse des pertes de capture. Le seuil doit tenir compte de la saisonnalité et de l’importance de l’actif.

L’absence soudaine d’événement sur un capteur essentiel doit être une alerte de santé si l’activité observée est habituellement régulière. Un moteur peut continuer à tourner alors qu’un filtre BPF exclut désormais un VLAN, qu’un port SPAN a été déplacé ou que le pipeline de logs est en échec. Un test synthétique autorisé et non intrusif peut vérifier que le capteur, l’export et le SIEM fonctionnent de bout en bout.

> **Astuce :** Établis deux types de tests : des tests de fonction du moteur (une trace de laboratoire doit déclencher la règle attendue) et des tests de santé du pipeline (l’événement doit arriver jusqu’au SIEM dans un délai mesuré). Ils répondent à deux questions différentes.

---

## 8. Réponse à incident et automatisation défensive

### 8.1 Séparer détection, qualification et action

Une alerte doit être évaluée selon la confiance, l’impact et l’urgence. Les événements à faible confiance peuvent simplement enrichir les journaux. Une suspicion crédible peut ouvrir un ticket, préserver des preuves ou demander l’avis d’un analyste. Le blocage automatique doit être réservé aux règles validées et aux actions réversibles avec un impact maîtrisé.

Un playbook d’automatisation doit vérifier l’actif visé, l’environnement, le propriétaire, l’état actuel, la réputation et la durée de la mesure. Il doit limiter le nombre d’objets qu’il peut affecter, consigner une justification, expirer automatiquement et prévoir un retour arrière. Un mécanisme qui bloque sans limite toutes les adresses associées à un événement peut provoquer un déni de service sur un service partagé ou un CDN. Les actions sur les identités, les routeurs et les pare-feu doivent être séparées par des permissions dédiées.

### Schéma 9 — Réponse graduée et retour arrière

<div class="ids-expert-diagram">
<svg viewBox="0 0 1120 380" role="img" aria-label="Chemin d’une alerte : validation des preuves, évaluation confiance et impact, actions graduées, puis mesure de l’effet avec expiration ou retour arrière obligatoire.">
  <text x="24" y="28" fill="#93c5fd" font-size="14" font-weight="700">RÉPONSE AUTOMATISÉE AVEC GARDE-FOUS</text>
  <rect class="node-blue" x="25" y="135" width="180" height="76" rx="10"/><text class="label" x="115" y="163">Alerte reçue</text><text class="sub" x="115" y="185">preuves / heure / zone</text>
  <rect class="node" x="270" y="135" width="195" height="76" rx="10"/><text class="label" x="367" y="163">Validation</text><text class="sub" x="367" y="185">actif / confiance / impact</text>
  <rect class="node-green" x="535" y="60" width="220" height="66" rx="10"/><text class="label" x="645" y="86">Collecter / enrichir</text><text class="sub" x="645" y="107">action à faible risque</text>
  <rect class="node-amber" x="535" y="150" width="220" height="66" rx="10"/><text class="label" x="645" y="176">Demander validation</text><text class="sub" x="645" y="197">analyste / propriétaire</text>
  <rect x="535" y="240" width="220" height="66" rx="10" fill="#450a0a" stroke="#f87171" stroke-width="1.6"/><text class="label" x="645" y="266">Mesure bornée</text><text class="sub" x="645" y="287">blocage ciblé / TTL</text>
  <rect class="node-blue" x="835" y="135" width="250" height="76" rx="10"/><text class="label" x="960" y="163">Mesurer et clôturer</text><text class="sub" x="960" y="185">effet / logs / expiration</text>
  <path class="flow flow-blue" d="M205 173 H268 M465 173 H505 V93 H535 M505 173 H533 M505 173 V273 H533 M755 93 H795 V173 H835 M755 183 H835 M755 273 H795 V173 H835"/>
  <text class="muted" x="560" y="340">Toute action automatique doit avoir une portée limitée, une durée, une trace</text><text class="muted" x="560" y="359">et une procédure de révocation testée avant l’incident.</text>
  <circle class="pulse" cx="239" cy="173" r="6" fill="#60a5fa"/><circle class="pulse d1" cx="520" cy="173" r="6" fill="#4ade80"/><circle class="pulse d2" cx="790" cy="173" r="6" fill="#fbbf24"/>
</svg>
</div>

### 8.2 Preuves, chaîne de conservation et confidentialité

La capture réseau peut contenir des identifiants, du contenu métier, des données personnelles et des secrets. Définis qui peut la lire, où elle est stockée, comment elle est chiffrée, combien de temps elle est conservée et comment sa suppression est prouvée. Lorsque les preuves doivent être utilisées dans une procédure d’incident ou un audit, documente qui a collecté le fichier, quand, sur quel capteur, selon quel filtre et avec quel hash d’intégrité. Le hash garantit qu’un fichier donné n’a pas changé depuis le calcul ; il ne prouve pas à lui seul que la capture était complète ou correctement collectée.

Exemple de copie et de calcul d’intégrité dans un environnement de réponse autorisé :

```bash
sha256sum incident-2026-10-22.pcap > incident-2026-10-22.pcap.sha256
sha256sum -c incident-2026-10-22.pcap.sha256
```

Le nom du fichier est un exemple. Stocke la capture et son empreinte dans un emplacement à accès contrôlé, distinct du poste de collecte lorsque c’est possible. Ne téléverse pas de PCAP de production dans un service externe sans autorisation et sans examen de la confidentialité.

### 8.3 Après l’incident

Le post-mortem doit expliquer ce qui s’est passé, comment la détection a fonctionné, quelles preuves ont été disponibles, pourquoi les contrôles ont réussi ou échoué, et quelles améliorations sont prioritaires. Il ne doit pas se limiter à une chronologie d’alertes. Prends en compte la couverture du capteur, les limites de visibilité TLS, les pertes de capture, la qualité des règles, la latence de l’ingestion, l’escalade, les décisions et les effets de la mitigation.

---

## 9. Configuration et pratique en laboratoire

Les exemples suivants doivent être exécutés dans un laboratoire ou sur un système que tu es autorisé à administrer. Les chemins et paramètres dépendent de la distribution et de la version. Le but est d’apprendre à vérifier le moteur et la chaîne de données, pas d’activer automatiquement une politique de blocage sur un lien critique.

### 9.1 Vérifier la configuration Suricata

```bash
suricata --build-info
sudo suricata -T -c /etc/suricata/suricata.yaml
sudo systemctl status suricata --no-pager
sudo journalctl -u suricata --since "30 minutes ago" --no-pager
```

Interprète les résultats : la commande de test valide la configuration reconnue par cette invocation ; elle ne prouve pas que l’interface attendue transporte le trafic, ni que le processus opérationnel emploie exactement le fichier testé. Vérifie le service, sa ligne de commande, les journaux de démarrage, la liste des règles chargées et les compteurs de capture.

Examine le journal EVE JSON dans une installation qui l’utilise :

```bash
sudo tail -n 20 /var/log/suricata/eve.json
jq 'select(.event_type == "alert") | {timestamp, src_ip, dest_ip, proto, alert}' /var/log/suricata/eve.json | head -n 40
```

Le chemin du journal et les champs exacts dépendent de la configuration. Évite d’afficher ou de transmettre des événements contenant des données sensibles hors du périmètre autorisé. Dans une chaîne SIEM, vérifie le nombre d’événements lus, rejetés, indexés et retardés.

### 9.2 Vérifier les compteurs de l’interface et du système

```bash
ip -s link show dev eno1
ethtool -S eno1
sar -n DEV 1 10
vmstat 1 10
```

Remplace `eno1` par la vraie interface. Tous les pilotes ne publient pas les mêmes compteurs dans `ethtool -S`. Recherche les erreurs, les drops et la progression des compteurs sur une fenêtre définie ; une valeur cumulative depuis le démarrage n’est pas équivalente à un taux de perte courant. Corrèle la mesure avec le débit offert et le nombre de paquets par seconde.

### 9.3 Rejouer une capture sans action de blocage

```bash
mkdir -p ./sortie-laboratoire
sudo suricata -r ./trafic-laboratoire.pcap \
  -c /etc/suricata/suricata.yaml \
  -l ./sortie-laboratoire
```

Le fichier PCAP doit être autorisé et préparé pour l’exercice. Compare les événements aux hypothèses attendues : nombre de détections, horodatages, règles, flux reconnus, erreurs de décodage et éventuelles différences entre les versions. Si une règle doit être évaluée, utilise un corpus contenant des exemples positifs et négatifs, y compris du trafic légitime ressemblant au motif recherché.

### 9.4 Valider une règle sans l’activer en prévention

Crée une règle de test dans un fichier dédié plutôt que de modifier directement le jeu de production. Utilise un identifiant local réservé à ton équipe selon la convention du moteur. Vérifie la syntaxe, lance la capture en mode analyse, observe l’alerte et mesure le coût. Ensuite, documente le résultat, le jeu de règles, la configuration, le PCAP source et l’empreinte du fichier de test si la reproductibilité est importante.

**Critères d’acceptation du laboratoire :**

1. Le moteur démarre avec la configuration voulue et indique la version vérifiée.
2. Le trafic de laboratoire est effectivement reçu ; les compteurs ne montrent pas de perte non expliquée.
3. Les événements attendus apparaissent et pointent vers une règle reproductible.
4. Les cas négatifs légitimes ne déclenchent pas la règle sans raison documentée.
5. Le pipeline SIEM reçoit les événements dans le délai défini.
6. Le laboratoire n’a pas modifié le trafic de production et peut être nettoyé sans effet secondaire.

---

## 10. Dépannage expert : symptômes, hypothèses et tests discriminants

### 10.1 La sonde ne déclenche plus aucune alerte

Ne commence pas par changer toutes les signatures. Vérifie dans l’ordre : arrivée des paquets sur l’interface, absence de drops, filtres d’acquisition, état du moteur, chargement du jeu de règles, version et expiration des règles, sortie EVE, puis réception SIEM. Utilise un jeu de traces connu. Si le PCAP de contrôle déclenche la règle mais pas le trafic opérationnel, suspecte la visibilité, la topologie, le protocole observé ou une différence du trafic. Si aucun des deux ne déclenche, examine la configuration, le buffer de détection et l’activation de la règle.

### 10.2 Une alerte est présente, mais l’application n’a rien vu

Valide d’abord si l’action était alert, drop ou reject ; une simple alerte n’interrompt pas le trafic. Examine le point de capture et le sens : une copie SPAN peut montrer des paquets que l’application n’a finalement pas reçus, ou une capture peut être prise avant qu’un pare-feu en aval ne bloque. Compare les horodatages, identifiants de flux, états TCP, NAT et journaux de l’hôte. Une alerte sur le contenu retransmis, une session tronquée ou un flux destiné à un autre service peut également expliquer la différence.

### 10.3 Faux positifs après une migration

Une migration peut changer les IP, le TLS, le CDN, les méthodes HTTP, le volume ou la structure d’une requête. Compare les événements avant/après, les versions de l’application et les journaux de terminaison. Ne crée pas d’exception globale pour un sous-réseau entier si seuls un endpoint ou une séquence précise posent problème. Reproduis l’événement avec un test non destructif et documente la nouvelle condition de détection.

### 10.4 Le CPU est bas, mais il y a des pertes

Le goulot peut se situer dans la NIC, une queue d’acquisition, une file déséquilibrée, le ring buffer, le stockage, l’exporteur ou l’ingestion SIEM. Observe les compteurs par composant et par cœur, le nombre de petits paquets par seconde, le backlog des journaux et les interruptions. Un CPU moyen faible masque un cœur saturé ou une file unique débordée. Un cluster a besoin de mesures par worker et de preuve que chaque flux reste cohérent.

### 10.5 Le blocage IPS casse une application légitime

Confirme la signature, le contexte, le chemin de session et l’action effective. Si le service est critique, applique le plan de mitigation approuvé : revenir à l’alerte seule ou désactiver uniquement la règle/portée responsable, selon la procédure de changement. Capture les preuves avant de modifier la règle. Après restauration du service, reproduis le cas, crée des tests positifs et négatifs, puis prépare une règle plus étroite et un déploiement progressif.

### 10.6 Le SIEM reçoit les événements avec retard

Sépare le temps de génération du capteur, le temps d’écriture du fichier, l’heure d’ingestion et l’heure d’indexation. Contrôle la taille des files, la pression disque, les erreurs du shipper, les limites réseau et les rejets du collecteur. L’alerte visible à 10:30 peut concerner un événement survenu à 10:20. Les playbooks automatiques doivent utiliser l’horodatage de l’événement et la qualité de sa synchronisation plutôt que de supposer que toutes les données sont en temps réel.

### Schéma 10 — Arbre de dépannage d’une détection manquante

<div class="ids-expert-diagram">
<svg viewBox="0 0 1120 390" role="img" aria-label="Arbre de dépannage : vérifier la capture, puis les drops, le moteur et les règles ; enfin vérifier l’export SIEM. Chaque branche mène à un test précis plutôt qu’à un changement global des règles.">
  <text x="24" y="28" fill="#93c5fd" font-size="14" font-weight="700">DIAGNOSTIC D’UNE ALERTE ABSENTE</text>
  <rect class="node-blue" x="25" y="74" width="210" height="58" rx="10"/><text class="label" x="130" y="99">Trafic reçu ?</text><text class="sub" x="130" y="118">capture / miroir / interface</text>
  <rect class="node-green" x="306" y="65" width="220" height="58" rx="10"/><text class="label" x="416" y="90">Oui : drops ?</text><text class="sub" x="416" y="109">compteurs par étape</text>
  <rect class="node-amber" x="306" y="157" width="220" height="58" rx="10"/><text class="label" x="416" y="182">Non : corriger capture</text><text class="sub" x="416" y="201">VLAN / filtre / chemin</text>
  <rect class="node-amber" x="592" y="65" width="220" height="58" rx="10"/><text class="label" x="702" y="90">Drops élevés ?</text><text class="sub" x="702" y="109">NIC / queue / worker</text>
  <rect class="node-blue" x="592" y="157" width="220" height="58" rx="10"/><text class="label" x="702" y="182">Moteur + règle ?</text><text class="sub" x="702" y="201">test config / PCAP connu</text>
  <rect class="node-green" x="875" y="65" width="210" height="58" rx="10"/><text class="label" x="980" y="90">Corriger capacité</text><text class="sub" x="980" y="109">affinité / queues / filtrage</text>
  <rect class="node-amber" x="875" y="157" width="210" height="58" rx="10"/><text class="label" x="980" y="182">Export SIEM ?</text><text class="sub" x="980" y="201">fichier / shipper / index</text>
  <path class="flow flow-blue" d="M235 103 H304 M416 123 V155 M526 94 H590 M702 123 V155 M812 94 H873 M812 186 H873"/>
  <text class="sub" x="269" y="91">Oui</text><text class="sub" x="435" y="144">Non</text><text class="sub" x="548" y="82">Oui</text><text class="sub" x="723" y="144">Non</text>
  <text class="muted" x="560" y="280">Traite une hypothèse à la fois et conserve les compteurs avant/après.</text><text class="muted" x="560" y="300">Une absence d’alerte peut venir de la capture, de la détection ou du transport des événements.</text>
  <rect class="node" x="310" y="324" width="500" height="42" rx="8"/><text class="label" x="560" y="350">Ne désactive pas toutes les règles pour masquer le symptôme.</text>
  <circle class="pulse" cx="270" cy="103" r="5" fill="#60a5fa"/><circle class="pulse d1" cx="555" cy="94" r="5" fill="#4ade80"/><circle class="pulse d2" cx="840" cy="186" r="5" fill="#fbbf24"/>
</svg>
</div>

---

## 11. Études de cas expert

### Cas A — Un scan latéral n’est détecté que sur un sens

**Symptôme.** Les journaux du pare-feu montrent des tentatives de connexion entre plusieurs VLAN, mais la sonde ne présente que des événements incomplets. Les signatures applicatives attendues ne déclenchent pas.

**Hypothèses.** Capture sur un seul lien ECMP ; SPAN saturé ; asymétrie de routage ; capteur situé avant un point de NAT ; filtre d’acquisition trop étroit ; déséquilibre du cluster ; règles qui exigent un état TCP complet.

**Tests.** Compare les compteurs de ports source et de destination, vérifie le sens du flux sur les captures et corrèle avec les tables NAT et les journaux du firewall. Rejoue une trace autorisée qui contient les deux sens. Mesure les pertes pendant le pic et vérifie que les sessions sont assignées au même worker.

**Résolution.** Corrige le point d’observation ou la distribution avant d’élargir les signatures. Documente les flux non couverts, établis un test de santé permanent et rejoue le test après tout changement de topologie.

### Cas B — Une règle HTTP produit soudainement des milliers d’alertes

**Symptôme.** Une nouvelle version de l’application provoque un pic d’alertes sur un motif HTTP.

**Hypothèses.** Changement de chemin ou de paramètre légitime, déploiement d’un nouveau client, changement de parser, règle trop large, duplication des événements ou trafic réellement malveillant.

**Tests.** Regroupe par URI, méthode, application, version de règle et hôte. Compare la chronologie avec le déploiement applicatif et inspecte des exemples positifs et négatifs. Vérifie que les événements ne sont pas dupliqués par deux capteurs ou le SIEM.

**Résolution.** Si le motif est légitime, réduis la portée avec une condition de protocole ou de ressource précise et ajoute des tests de régression. Si la cause est une duplication de pipeline, corrige l’ingestion plutôt que la règle. Si la menace est confirmée, conserve les échantillons et adapte la réponse.

### Cas C — Le débit paraît normal, mais l’IPS augmente la latence

**Symptôme.** Le débit en bit/s reste sous la capacité nominale, mais les applications connaissent des pics de latence.

**Hypothèses.** Taux de petits paquets élevé, coût de signatures, réassemblage de sessions volumineuses, contention mémoire, déséquilibre de workers, inspection de fichiers, file inline et retransmissions provoquées par la perte.

**Tests.** Mesure bit/s et paquets/s séparément. Compare le temps de traitement, les drops, la latence avant/après l’IPS et les percentiles par worker. Rejoue un profil de trafic représentatif, puis désactive une catégorie de détection dans une copie de laboratoire pour quantifier sa contribution.

**Résolution.** Ajuste le dimensionnement, le placement, les files et les règles coûteuses. Ne réduis pas globalement la qualité de la détection sans évaluer l’augmentation du risque. Toute modification doit avoir des critères de performance, de couverture et de sécurité.

### Cas D — L’alerte est correcte, mais le blocage automatique vise le mauvais actif

**Symptôme.** Un playbook bloque une adresse IP associée à un utilisateur alors que l’adresse est partagée par un NAT ou un proxy.

**Hypothèses.** Attribution d’identité insuffisante, traduction NAT non corrélée, données DHCP anciennes, clé SIEM incorrecte ou confusion entre IP de capteur et IP d’origine.

**Tests.** Vérifie la source de chaque champ, la chronologie de translation et les informations de session. Rejoue la corrélation sur un jeu d’événements connu. Mesure la possibilité d’affecter des utilisateurs légitimes qui partagent la même IP.

**Résolution.** Limite l’automatisation à une identité plus forte ou à une session ciblée ; sinon, transforme l’action en validation humaine. Ajoute une expiration, un journal d’action et une procédure de révocation.

---

## 12. Sécurité et gouvernance opérationnelle

Un IDS/IPS est lui-même un actif de sécurité. Protège l’accès administratif, sépare les comptes d’exploitation des comptes d’analyse, applique des mises à jour contrôlées, surveille les changements de configuration et centralise les journaux. Les interfaces de capture et d’administration ne doivent pas être exposées sans contrôle. Les secrets d’export, certificats et clés d’inspection doivent être stockés et renouvelés selon une politique définie.

La confidentialité des contenus inspectés exige un périmètre clair. Réduis la collecte au nécessaire, masque les données qui ne sont pas nécessaires à l’analyse, restreins l’accès, limite les exports et fixe une durée de conservation. Si une inspection TLS est déployée, documente les catégories d’applications exclues, les responsables, les certificats employés, les risques et les modalités d’audit.

Les procédures de changement doivent contenir : objectif, périmètre, risque, prérequis, mesures avant changement, fenêtre, étapes, résultat attendu, critères d’arrêt, validation après changement et rollback. Dans un IPS en ligne, le test de perte de lien et de redémarrage est aussi important que le test de déclenchement d’une signature.

### Contrôles périodiques minimaux

- Valider la visibilité des interfaces et l’absence de pertes inexpliquées.
- Confirmer l’heure, la version du moteur, la version des règles et la dernière mise à jour réussie.
- Rejouer les corpus positifs et négatifs des règles critiques.
- Mesurer la latence inline sous un profil de charge réel et représentatif.
- Tester le mode fail-open/fail-closed et les mécanismes de bypass en fenêtre autorisée.
- Comparer les compteurs du capteur, des exporteurs et du SIEM.
- Revoir les exclusions et exceptions expirantes avec les propriétaires des actifs.
- Vérifier les droits, les journaux d’administration et les sauvegardes de configuration.
- Tester un playbook en environnement de simulation, y compris sa révocation.
- Documenter un cas où la détection ne peut pas voir le contenu, notamment sous chiffrement.

---

## Points à retenir

- L’architecture d’inspection commence par les objectifs et les preuves attendues, pas par le choix d’un produit.
- La couverture doit être prouvée : placement, sens, pertes, asymétrie, filtres, horloges et export.
- Le réassemblage et la normalisation servent à réduire les ambiguïtés entre le trafic observé et le trafic reçu par l’application.
- Les signatures, les analyses protocolaires et les détections comportementales sont complémentaires ; aucune ne remplace seule les autres.
- Une règle est un artefact versionné qui requiert des tests positifs, négatifs, un déploiement progressif et un retour arrière.
- Le DPI est limité par les points où le trafic est visible et déchiffré ; TLS ne doit pas être « contourné » en désactivant la validation des certificats.
- La capacité doit être mesurée en bit/s, paquets/s, sessions, mémoire, coût des règles, latence et pertes, à chaque étape du pipeline.
- Fail-open et fail-closed représentent des choix de risque métier ; ils doivent être explicitement testés et documentés.
- Le SIEM corrèle des données, mais ne répare pas la perte de paquets sur le capteur. Les heures de génération et d’ingestion doivent être différenciées.
- Une action automatique doit être bornée, réversible, journalisée, expirante et adaptée à la certitude disponible.
- La qualité de détection se mesure sur un corpus représentatif, avec précision, rappel, délai, coût et limites déclarées.

---

## Références techniques

1. Open Information Security Foundation, **Suricata User Guide** — modes IDS/IPS, règles, configuration, capture, inspection et journalisation : https://docs.suricata.io/
2. The Zeek Project, **Book of Zeek** — architecture, événements de connexion, analyse protocolaires et déploiements distribués : https://docs.zeek.org/en/current/
3. NIST, Karen Scarfone et Peter Mell, **SP 800-94 — Guide to Intrusion Detection and Prevention Systems (IDPS)**, février 2007. Cette référence historique demeure utile pour les principes de déploiement et d’exploitation, mais elle doit être complétée par les documentations modernes des moteurs et protocoles : https://doi.org/10.6028/NIST.SP.800-94
4. MITRE ATT&CK — base de connaissances des tactiques et techniques adverses, utile pour cartographier une hypothèse de détection : https://attack.mitre.org/
5. Wireshark Documentation — capture, affichage, réassemblage des protocoles et interprétation des traces : https://www.wireshark.org/docs/
6. IETF RFC 8446, **The Transport Layer Security (TLS) Protocol Version 1.3** : https://www.rfc-editor.org/rfc/rfc8446
7. IETF RFC 9000, **QUIC: A UDP-Based Multiplexed and Secure Transport** : https://www.rfc-editor.org/rfc/rfc9000
8. IETF RFC 9114, **HTTP/3** : https://www.rfc-editor.org/rfc/rfc9114

Les syntaxes de règles, noms de compteurs et comportements inline évoluent entre versions. Utilise la documentation correspondant à la version déployée et consigne cette version dans les rapports de laboratoire.
