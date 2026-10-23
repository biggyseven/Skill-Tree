# IDS / IPS et DPI — Intermédiaire

**Niveau : INTERMÉDIAIRE**

À ce stade, il ne suffit plus de savoir qu’un IDS détecte et qu’un IPS peut bloquer. L’objectif est de comprendre où placer un capteur, comment il reconstitue un flux, comment une signature est évaluée, pourquoi une alerte peut être fausse ou incomplète et comment confirmer une détection à partir de preuves réseau.

Ce cours prolonge les bases du niveau Débutant. Il utilise des exemples Suricata, des captures de paquets, des règles de détection et des scénarios d’exploitation. Les commandes sont conçues pour un laboratoire Linux ; adaptez les interfaces, les chemins et les versions avant de les utiliser sur un système réel.

> **Analogie** : Un IDS ressemble à une caméra et à un système d’alarme : il observe et signale ce qui paraît anormal. Un IPS placé en ligne ressemble à un contrôle d’accès : il peut arrêter un flux avant qu’il n’atteigne sa destination. Le DPI correspond au travail d’analyse du contenu et du contexte du trafic, dans les limites de ce que le capteur peut réellement voir.

---

## 1. Théorie et mécanismes d’inspection

### 1.1 Rappels opérationnels : IDS, IPS, NDR et DPI

Un **IDS** (*Intrusion Detection System*) examine des événements ou du trafic et produit des alertes. Un IDS réseau (*NIDS*) reçoit généralement une copie du trafic via un port SPAN, un TAP ou un mécanisme de capture. Sa panne ne coupe en principe pas directement le trafic de production, mais une mauvaise capture peut lui faire manquer des paquets.

Un **IPS** (*Intrusion Prevention System*) analyse le trafic et peut agir avant de le laisser continuer : abandonner des paquets, interrompre une session, appliquer une règle ou demander une mesure de mitigation. Un IPS réseau est souvent placé en ligne. Cette position permet de bloquer, mais introduit aussi des risques de disponibilité, de latence et de panne de chemin.

Le **DPI** (*Deep Packet Inspection*) n’est pas à lui seul un produit ou une politique de sécurité. Il désigne une famille de techniques qui inspectent les protocoles au-delà des seuls champs de base IP et transport. Selon le produit et la configuration, l’inspection peut reconnaître une transaction DNS, une requête HTTP, un protocole applicatif, une séquence de commandes ou un motif associé à une attaque. Le DPI ne signifie pas que tout le contenu est toujours visible : le chiffrement, la fragmentation, les pertes de paquets et les limites de ressources réduisent la visibilité.

| Technologie | Fonction principale | Action directe sur le trafic | Exemple de sortie |
|---|---|---|---|
| NIDS | Détecter un comportement à partir du trafic copié | Normalement non | Alerte, métadonnées, PCAP |
| NIPS | Détecter et prévenir sur le chemin de données | Oui, selon la politique | Drop, rejet, reset, événement |
| HIDS | Observer l’activité d’un hôte | Sur l’hôte, selon l’agent | Fichier modifié, processus suspect |
| NDR | Corréler les comportements réseau dans le temps | Souvent détection et investigation | Chronologie, graphe de communications |
| DPI | Analyser la structure et le contexte des protocoles | Pas nécessairement | Champs applicatifs et classification |
| WAF | Protéger les applications Web HTTP(S) | Généralement oui, en proxy ou filtre | Blocage d’une requête Web |

> **Piège :** Ne déduisez pas la fonction d’un produit à partir de son nom commercial. Vérifiez s’il reçoit une copie ou se trouve en ligne, quels protocoles il décode, quelles actions sont actives, et si le trafic chiffré est déchiffré ou uniquement classifié par métadonnées.

### 1.2 Architecture de déploiement : observation ou passage en ligne

Le choix entre mode passif et mode inline dépend du risque accepté, de la capacité de traitement, de la topologie et des exigences de disponibilité. En mode passif, le capteur peut comparer les paquets sans devenir un point de passage obligé. En contrepartie, il ne bloque pas nativement le paquet original. En mode inline, l’équipement peut appliquer une décision en temps réel, mais le débit, la latence, la redondance et le comportement de panne doivent être testés.

<style>
.net-diagram{margin:1.25rem 0 1.8rem;padding:.75rem;border:1px solid #3f3f46;border-radius:1rem;background:#18181b;color:#e4e4e7;overflow-x:auto;max-width:100%;}
.net-diagram svg{display:block;width:100%;min-width:760px;height:auto;font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;}
.net-diagram .node{fill:#27272a;stroke:#71717a;stroke-width:1.5;}
.net-diagram .node-blue{fill:#172554;stroke:#60a5fa;stroke-width:1.5;}
.net-diagram .node-green{fill:#052e16;stroke:#4ade80;stroke-width:1.5;}
.net-diagram .node-amber{fill:#451a03;stroke:#fbbf24;stroke-width:1.5;}
.net-diagram .label{fill:#f4f4f5;font-size:15px;font-weight:650;text-anchor:middle;}
.net-diagram .sub{fill:#d4d4d8;font-size:12px;text-anchor:middle;}
.net-diagram .line{fill:none;stroke:#a1a1aa;stroke-width:3;}
.net-diagram .flow-blue{fill:none;stroke:#60a5fa;stroke-width:3;stroke-dasharray:9 10;animation:net-flow 1.6s linear infinite;}
.net-diagram .flow-green{fill:none;stroke:#4ade80;stroke-width:3;stroke-dasharray:9 10;animation:net-flow 1.25s linear infinite;}
.net-diagram .flow-amber{fill:none;stroke:#fbbf24;stroke-width:3;stroke-dasharray:7 9;animation:net-flow 1.8s linear infinite;}
.net-diagram .pulse{transform-box:fill-box;transform-origin:center;animation:net-pulse 2s ease-in-out infinite;}
.net-diagram .delay1{animation-delay:.35s}.net-diagram .delay2{animation-delay:.7s}.net-diagram .delay3{animation-delay:1.05s}
@keyframes net-flow{to{stroke-dashoffset:-38}}
@keyframes net-pulse{0%,100%{opacity:.45;transform:scale(.96)}50%{opacity:1;transform:scale(1.04)}}
@media(prefers-reduced-motion:reduce){.net-diagram *{animation:none!important;scroll-behavior:auto!important;}}
</style>

<div class="net-diagram">
<svg viewBox="0 0 1000 290" role="img" aria-label="Comparaison de deux modes : en haut, le trafic traverse un IPS en ligne qui peut autoriser ou bloquer ; en bas, un TAP envoie une copie vers un IDS passif, sans remplacer le chemin original.">
  <text x="22" y="26" fill="#93c5fd" font-size="14" font-weight="700">A — IPS EN LIGNE</text>
  <rect class="node-blue" x="24" y="48" width="170" height="62" rx="10"/>
  <text class="label" x="109" y="73">Client</text><text class="sub" x="109" y="92">trafic entrant</text>
  <path class="flow-blue" d="M194 79 H310"/><path d="M300 71 L313 79 L300 87" fill="none" stroke="#60a5fa" stroke-width="3"/>
  <rect class="node-amber" x="315" y="48" width="190" height="62" rx="10"/>
  <text class="label" x="410" y="73">IPS inline</text><text class="sub" x="410" y="92">inspecte et décide</text>
  <path class="flow-green" d="M505 79 H625"/><path d="M615 71 L628 79 L615 87" fill="none" stroke="#4ade80" stroke-width="3"/>
  <rect class="node-green" x="630" y="48" width="170" height="62" rx="10"/>
  <text class="label" x="715" y="73">Serveur</text><text class="sub" x="715" y="92">si autorisé</text>
  <path d="M410 110 V127 H858" stroke="#f87171" stroke-width="2" fill="none" stroke-dasharray="5 5"/>
  <rect x="805" y="116" width="150" height="29" rx="8" fill="#450a0a" stroke="#f87171"/>
  <text x="880" y="135" fill="#fecaca" font-size="12" font-weight="650" text-anchor="middle">Drop possible</text>
  <line x1="20" y1="158" x2="978" y2="158" stroke="#3f3f46"/>
  <text x="22" y="183" fill="#86efac" font-size="14" font-weight="700">B — IDS PASSIF AVEC TAP / SPAN</text>
  <rect class="node-blue" x="24" y="202" width="170" height="62" rx="10"/>
  <text class="label" x="109" y="227">Client</text><text class="sub" x="109" y="246">trafic original</text>
  <path class="flow-blue" d="M194 233 H430"/><path d="M420 225 L433 233 L420 241" fill="none" stroke="#60a5fa" stroke-width="3"/>
  <rect class="node" x="435" y="202" width="150" height="62" rx="10"/>
  <text class="label" x="510" y="227">Switch / TAP</text><text class="sub" x="510" y="246">copie des paquets</text>
  <path class="flow-green" d="M585 233 H800"/><path d="M790 225 L803 233 L790 241" fill="none" stroke="#4ade80" stroke-width="3"/>
  <rect class="node-green" x="805" y="202" width="150" height="62" rx="10"/>
  <text class="label" x="880" y="227">Serveur</text><text class="sub" x="880" y="246">chemin original</text>
  <path class="flow-amber" d="M510 202 V190 H700 V202"/>
  <rect class="node-amber" x="615" y="168" width="170" height="37" rx="8"/>
  <text class="label" x="700" y="191" font-size="13">IDS observe la copie</text>
</svg>
</div>

En production, une copie SPAN n’est pas forcément identique au trafic reçu par l’application : le switch peut perdre des copies lorsque le port miroir est saturé, certains VLAN ou sens de trafic peuvent être absents et l’ordre des paquets peut différer. Un TAP matériel correctement dimensionné offre parfois une meilleure fidélité, mais doit également être conçu et supervisé.

Le mode **fail-open** peut laisser passer le trafic si le moteur de prévention tombe en panne, au prix d’une perte temporaire de prévention. Le mode **fail-closed** bloque si le moteur ne fonctionne plus, au risque de provoquer une indisponibilité. Le choix doit être documenté par service et validé avec les propriétaires métier ; il ne se résume pas à une préférence universelle.

### 1.3 Cycle d’inspection DPI

Un moteur d’inspection ne recherche pas seulement une chaîne de caractères sur chaque paquet. Il peut suivre un flux, réassembler les segments TCP, décoder un protocole, extraire des champs normalisés, puis évaluer une ou plusieurs signatures. Le résultat dépend de l’état du flux, de la politique activée, des délais, de la mémoire et de la version du moteur.

<div class="net-diagram">
<svg viewBox="0 0 1000 260" role="img" aria-label="Cycle DPI composé de six étapes distinctes : capture, suivi de flux, réassemblage, décodage applicatif, évaluation des signatures et action selon la politique.">
  <path class="flow-blue" d="M145 110 H185 M300 110 H340 M455 110 H495 M610 110 H650 M765 110 H805"/>
  <path d="M175 103 L187 110 L175 117 M330 103 L342 110 L330 117 M485 103 L497 110 L485 117 M640 103 L652 110 L640 117 M795 103 L807 110 L795 117" fill="none" stroke="#60a5fa" stroke-width="2.5"/>
  <rect class="node-blue" x="20" y="63" width="125" height="94" rx="10"/>
  <text class="label" x="82.5" y="92">1. Capture</text><text class="sub" x="82.5" y="114">paquets</text><text class="sub" x="82.5" y="132">et métadonnées</text>
  <rect class="node" x="190" y="63" width="110" height="94" rx="10"/>
  <text class="label" x="245" y="92">2. Flux</text><text class="sub" x="245" y="114">5-tuple</text><text class="sub" x="245" y="132">et état TCP</text>
  <rect class="node" x="345" y="63" width="110" height="94" rx="10"/>
  <text class="label" x="400" y="92">3. Reconstituer</text><text class="sub" x="400" y="114">ordre, segments</text><text class="sub" x="400" y="132">et fragments</text>
  <rect class="node" x="500" y="63" width="110" height="94" rx="10"/>
  <text class="label" x="555" y="92">4. Décoder</text><text class="sub" x="555" y="114">HTTP, DNS…</text><text class="sub" x="555" y="132">si visible</text>
  <rect class="node-amber" x="655" y="63" width="110" height="94" rx="10"/>
  <text class="label" x="710" y="92">5. Détecter</text><text class="sub" x="710" y="114">signature /</text><text class="sub" x="710" y="132">anomalie</text>
  <rect class="node-green" x="810" y="63" width="170" height="94" rx="10"/>
  <text class="label" x="895" y="92">6. Décision</text><text class="sub" x="895" y="114">alerte, drop,</text><text class="sub" x="895" y="132">pass ou log</text>
  <path d="M895 157 V195 H245 V157" fill="none" stroke="#a1a1aa" stroke-width="2" stroke-dasharray="5 6"/>
  <text x="565" y="220" fill="#d4d4d8" font-size="13" text-anchor="middle">L’état du flux et les résultats précédents alimentent l’inspection suivante</text>
</svg>
</div>

Chaque étape ajoute un coût. Le suivi de milliers ou de millions de flux consomme de la mémoire. Le réassemblage nécessite des tampons et des temporisations. Le décodage applicatif varie selon le protocole. L’évaluation des règles dépend de leur nombre, des conditions de recherche et des options utilisées. Une signature particulièrement coûteuse peut dégrader le débit global, même si la bande passante semble suffisante.

> **Astuce :** Pour investiguer une détection, demandez-vous à quelle étape l’évidence existe : simple en-tête réseau, état de session, protocole décodé, contenu visible, ou corrélation avec d’autres événements. Cette question aide à choisir un filtre de capture et à ne pas attribuer au DPI une visibilité qu’il n’a pas.

### 1.4 Signatures, anomalies et réputation

Une détection **par signature** vérifie des conditions précises : protocole, ports, direction, champs du paquet, motif dans une transaction ou combinaison de conditions. Elle peut être efficace contre des comportements connus, mais dépend de la qualité, de la fraîcheur et du contexte des règles.

Une détection **comportementale ou statistique** compare les événements à une référence : volume inhabituel de requêtes DNS, augmentation soudaine d’échecs, scans horizontaux, nombre de connexions par hôte ou changement de rythme. Elle peut identifier des comportements inconnus, mais les pics de trafic légitimes, les sauvegardes, les déploiements ou les migrations peuvent ressembler à des anomalies.

La réputation et les listes de renseignement sur les menaces apportent du contexte sur une adresse, un certificat, un domaine ou une infrastructure déjà associée à une activité malveillante. Elles ne constituent pas une preuve suffisante à elles seules : une adresse peut être partagée, réattribuée ou utilisée par un service légitime. Le renseignement doit être assorti d’une source, d’une date, d’un niveau de confiance et d’une date d’expiration.

| Méthode | Point fort | Limite typique | Bon usage |
|---|---|---|---|
| Signature | Explicable, répétable, précise sur un motif connu | Peut manquer une variante ou s’activer dans un contexte légitime | Exploit et protocole connus |
| Anomalie | Repère une dérive par rapport à la référence | Dépend de la qualité de la baseline et génère des faux positifs | Dérive de volume ou de comportement |
| Réputation | Ajoute rapidement du contexte | Donnée parfois périmée ou partagée | Priorisation et enrichissement |
| Corrélation | Combine plusieurs preuves faibles | Dépend du temps, de la normalisation et de la qualité des données | Incident multi-étapes |

> **Piège :** Une détection inhabituelle n’est pas automatiquement une attaque. Une signature négative ne prouve pas non plus l’absence de menace : le trafic peut être chiffré, tronqué, mal capturé, mal réassemblé ou non couvert par les règles activées.

### 1.5 Anatomie d’une règle Suricata

Suricata utilise des règles pour associer un comportement réseau à une alerte ou à une action. Une règle standard suit la forme générale suivante :

```text
action protocole source port -> destination port (options)
```

- **Action** : `alert` signale le match ; d’autres actions dépendent du mode d’exécution et de la configuration IPS.
- **Protocole** : `tcp`, `udp`, `icmp`, `ip` ou un protocole applicatif reconnu selon la règle.
- **Source et destination** : adresses et ports, avec variables telles que `$HOME_NET` et `$EXTERNAL_NET`.
- **Direction** : `->` représente un sens précis ; les règles bidirectionnelles s’expriment avec `<>`.
- **Options** : message, classification, identifiant de règle, conditions de contenu, contexte de flux, seuils ou champs applicatifs.

Exemple d’une règle de laboratoire qui alerte sur une requête HTTP contenant un marqueur inoffensif précis :

```text
alert http $HOME_NET any -> $EXTERNAL_NET any (
  msg:"LAB HTTP marqueur pedagogique";
  flow:established,to_server;
  http.uri;
  content:"/training-check";
  startswith;
  sid:1001001;
  rev:1;
)
```

Cette règle suppose que le moteur reconnaît HTTP et qu’une requête visible arrive au capteur. Dans un laboratoire, envoyez une requête vers un serveur contrôlé qui contient `/training-check` et vérifiez la sortie d’alerte. Ne supposez pas que `http.uri` sera disponible si le trafic est HTTPS chiffré au point de capture.

Exemple de règle de journalisation pour un trafic ICMP d’un banc d’essai :

```text
alert icmp $EXTERNAL_NET any -> $HOME_NET any (
  msg:"LAB ICMP vers reseau interne";
  itype:8;
  sid:1001002;
  rev:1;
)
```

L’ICMP echo request ne constitue pas en soi une attaque. La règle ci-dessus sert à montrer la structure d’une signature et peut signaler du trafic légitime. En production, une règle utile doit intégrer le contexte, les seuils nécessaires et une réponse appropriée au risque.

> **Danger :** Ne copiez pas des règles génériques de blocage dans un IPS de production sans tests. Une règle trop large peut couper des services, et un changement de mode ou de politique peut transformer des alertes en actions bloquantes. Validez les règles sur un jeu de trafic représentatif et préparez une procédure de retour arrière.

### 1.6 Faux positifs, faux négatifs et qualité du signal

Un **faux positif** se produit lorsqu’un comportement légitime est classé comme malveillant. Un **faux négatif** survient lorsque le système manque une activité réellement malveillante. Réduire l’un sans tenir compte de l’autre peut empirer la sécurité : une règle très permissive déclenche trop d’alertes, alors qu’une règle excessivement restreinte peut masquer un incident.

Les mesures classiques sont :

| Mesure | Signification |
|---|---|
| Vrais positifs (TP) | Menaces présentes et correctement détectées |
| Faux positifs (FP) | Activités légitimes incorrectement signalées |
| Vrais négatifs (TN) | Activités légitimes correctement non signalées |
| Faux négatifs (FN) | Menaces non détectées |
| Précision | TP / (TP + FP), proportion d’alertes positives qui sont correctes |
| Rappel | TP / (TP + FN), part des menaces connues qui sont détectées |

Un jeu de test doit représenter les usages normaux, les pics planifiés, les erreurs d’application et les attaques simulées autorisées. Une signature testée seulement contre le trafic malveillant peut sembler parfaite tout en bloquant à tort un flux métier important.

### 1.7 Inspection de TLS et visibilité limitée

Lorsqu’un capteur voit du TLS chiffré, il peut souvent observer l’adresse source/destination, les ports, la durée, le volume, le rythme des paquets et certaines métadonnées de négociation selon la version TLS, les extensions et la configuration. Il ne peut pas simplement rechercher une URI HTTP dans le contenu chiffré comme si celui-ci était en clair.

Les options dépendent de l’architecture :

1. Inspecter les métadonnées et le comportement sans déchiffrer.
2. Déplacer la détection au point de terminaison TLS, par exemple sur le reverse proxy ou le serveur qui voit la requête en clair.
3. Utiliser une fonction de déchiffrement contrôlée et autorisée lorsque la politique, le droit applicable, la gestion des certificats et les risques de confidentialité le permettent.
4. Corréler les événements du WAF, du proxy, des serveurs, des DNS et de l’EDR afin de compenser les limites d’un seul point de visibilité.

Le déchiffrement TLS n’est pas gratuit : il consomme des ressources, introduit une clé de confiance dans l’architecture et peut rendre sensibles les données collectées. Il faut définir des exclusions justifiées, limiter l’accès aux traces, protéger les clés, gérer les certificats et évaluer l’impact sur les applications utilisant du pinning ou des protocoles particuliers.

<div class="net-diagram">
<svg viewBox="0 0 1000 250" role="img" aria-label="Schéma de la visibilité TLS : en amont, le capteur réseau voit les adresses, les ports, le volume et le rythme ; au niveau du proxy ou du serveur qui termine TLS, le trafic peut être visible en clair et inspecté conformément à la politique.">
  <rect class="node-blue" x="25" y="47" width="205" height="78" rx="11"/>
  <text class="label" x="127.5" y="75">Client TLS</text><text class="sub" x="127.5" y="98">requête chiffrée</text>
  <path class="flow-blue" d="M230 86 H390"/><path d="M380 78 L393 86 L380 94" fill="none" stroke="#60a5fa" stroke-width="3"/>
  <rect class="node-amber" x="395" y="47" width="215" height="78" rx="11"/>
  <text class="label" x="502.5" y="75">Capteur réseau</text><text class="sub" x="502.5" y="98">métadonnées / flux</text>
  <path class="flow-green" d="M610 86 H770"/><path d="M760 78 L773 86 L760 94" fill="none" stroke="#4ade80" stroke-width="3"/>
  <rect class="node-green" x="775" y="47" width="200" height="78" rx="11"/>
  <text class="label" x="875" y="75">Proxy / serveur</text><text class="sub" x="875" y="98">terminaison TLS</text>
  <rect class="node" x="395" y="160" width="215" height="62" rx="10"/>
  <text class="label" x="502.5" y="185">Visibilité réduite</text><text class="sub" x="502.5" y="205">pas d’URI en clair ici</text>
  <path d="M502 125 V155" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="5 5"/>
  <rect class="node-green" x="775" y="160" width="200" height="62" rx="10"/>
  <text class="label" x="875" y="185">Inspection applicative</text><text class="sub" x="875" y="205">après terminaison autorisée</text>
  <path class="flow-green" d="M875 125 V155"/>
</svg>
</div>

> **Analogie** : Observer un échange TLS depuis l’extérieur ressemble à regarder un colis fermé : on peut souvent relever son poids, sa destination et son rythme d’arrivée, mais pas lire le contenu. Le serveur qui termine TLS ressemble au point autorisé où le colis est ouvert ; il faut alors protéger les données que ce point révèle.

### 1.8 Détection sur trafic fragmenté, asymétrique ou incomplet

L’inspection devient plus difficile lorsqu’un flux est distribué entre plusieurs capteurs, qu’un routage asymétrique envoie chaque sens par un chemin différent ou que des paquets sont perdus. Les moteurs stateful ont besoin d’un contexte suffisamment cohérent pour réassembler les échanges. Un capteur ne voyant qu’une direction peut avoir des difficultés à interpréter les états TCP ou à reconstituer les transactions applicatives.

Les fragments IP peuvent également séparer les données qui portent le contenu pertinent. Le moteur doit appliquer une politique de réassemblage cohérente avec les hôtes de destination. Les ambiguïtés de normalisation entre le capteur et la pile réseau de la cible peuvent créer des écarts : si deux composants interprètent différemment une séquence de segments, une règle peut manquer un motif ou signaler à tort une anomalie.

Bonnes pratiques :

- Documenter les points de capture, les VLAN, les directions et les pertes constatées.
- Mesurer les compteurs du port miroir, du NIC, du moteur et du pipeline de journalisation.
- Conserver le contexte TCP et les horodatages pour les investigations autorisées.
- Comparer une capture côté capteur à une capture côté cible lorsque la question porte sur ce que l’application a réellement reçu.
- Ne pas désactiver la normalisation ou le réassemblage pour « faire disparaître » une alerte sans comprendre l’effet sur la détection.

### 1.9 Débit, paquets par seconde et coût des règles

Un capteur peut être limité par le débit en bit/s, mais aussi par le nombre de paquets par seconde, le nombre de flux simultanés, la taille des tables d’état, le coût des décodeurs ou la rapidité du stockage des journaux. Un trafic de petits paquets peut épuiser le budget de traitement tout en laissant la bande passante assez basse. À l’inverse, un débit élevé avec des paquets plus gros peut saturer le lien avant le moteur.

Pour une première estimation, si un capteur reçoit 800 000 paquets/s et traite en moyenne 1 microseconde de CPU par paquet, cela représente théoriquement 0,8 seconde de CPU par seconde sur un seul cœur. En pratique, les coûts varient selon les règles, les accès mémoire, le parallélisme, les interruptions et les copies de buffers ; ce calcul n’est qu’un ordre de grandeur.

Surveiller au minimum :

- les paquets reçus et perdus à l’interface ;
- les compteurs du moteur (capture, décodage, détection, drops) ;
- la profondeur et le taux de remplissage des files ;
- le nombre de flux et d’événements par seconde ;
- l’utilisation CPU, mémoire et débit disque ;
- le délai entre l’événement réseau, l’alerte et son ingestion dans le SIEM.

> **Piège :** Un moteur qui ne signale rien alors qu’il perd des paquets n’est pas nécessairement un réseau sain. La supervision de la santé du capteur fait partie de la chaîne de détection : collectez les compteurs de perte et déclenchez une alerte quand la visibilité n’est plus suffisante.

### 1.10 Chaîne de traitement d’une alerte

Une alerte passe rarement directement de « règle déclenchée » à « incident confirmé ». Il faut vérifier l’actif concerné, le sens du flux, le contexte métier, l’évidence de protocole, la réputation des interlocuteurs, les événements voisins et l’effet éventuel d’une action de prévention.

<div class="net-diagram">
<svg viewBox="0 0 1000 270" role="img" aria-label="Cycle de traitement d'une alerte en six étapes : alerte brute, enrichissement, validation par preuves, qualification, réponse proportionnée, puis retour d'expérience et ajustement.">
  <path class="flow-blue" d="M150 98 H185 M310 98 H345 M470 98 H505 M630 98 H665 M790 98 H825"/>
  <path d="M175 91 L187 98 L175 105 M330 91 L342 98 L330 105 M495 91 L507 98 L495 105 M650 91 L662 98 L650 105 M815 91 L827 98 L815 105" fill="none" stroke="#60a5fa" stroke-width="2.5"/>
  <rect class="node-blue" x="20" y="52" width="130" height="90" rx="10"/><text class="label" x="85" y="80">1. Alerte</text><text class="sub" x="85" y="101">signature ou</text><text class="sub" x="85" y="119">anomalie</text>
  <rect class="node" x="190" y="52" width="120" height="90" rx="10"/><text class="label" x="250" y="80">2. Enrichir</text><text class="sub" x="250" y="101">actif, user,</text><text class="sub" x="250" y="119">criticité</text>
  <rect class="node" x="350" y="52" width="120" height="90" rx="10"/><text class="label" x="410" y="80">3. Vérifier</text><text class="sub" x="410" y="101">PCAP, logs,</text><text class="sub" x="410" y="119">contexte</text>
  <rect class="node-amber" x="510" y="52" width="120" height="90" rx="10"/><text class="label" x="570" y="80">4. Qualifier</text><text class="sub" x="570" y="101">FP, TP,</text><text class="sub" x="570" y="119">incertain</text>
  <rect class="node-green" x="670" y="52" width="120" height="90" rx="10"/><text class="label" x="730" y="80">5. Répondre</text><text class="sub" x="730" y="101">surveiller,</text><text class="sub" x="730" y="119">bloquer, isoler</text>
  <rect class="node" x="830" y="52" width="150" height="90" rx="10"/><text class="label" x="905" y="80">6. Améliorer</text><text class="sub" x="905" y="101">règle, seuil,</text><text class="sub" x="905" y="119">procédure</text>
  <path class="flow-green" d="M905 142 V188 H85 V142"/>
  <text x="495" y="215" text-anchor="middle" fill="#86efac" font-size="14" font-weight="650">La clôture doit alimenter la qualité des règles et la supervision</text>
  <text x="495" y="239" text-anchor="middle" fill="#a1a1aa" font-size="12">Conserver les preuves, la chronologie, les décisions et les raisons du blocage</text>
</svg>
</div>

---

## 2. Configuration et pratique

### 2.1 Préparer le laboratoire Suricata

Effectuez ces étapes dans une VM Linux ou un conteneur isolé avec des paquets autorisés. Les noms des interfaces et des fichiers de configuration peuvent varier selon la distribution et la version.

```bash
suricata --build-info
suricata --list-runmodes
ip -br link
ip -br addr
```

Vérifiez la version, les capacités de capture disponibles et le nom de l’interface du laboratoire. En mode passif, une interface peut écouter un port miroir ; dans un laboratoire simple, une capture PCAP peut éviter de dépendre d’un switch configuré pour SPAN.

Pour vérifier syntaxiquement la configuration, selon la distribution :

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml
```

La commande de test de configuration ne remplace pas un test de capture réel. Elle ne prouve pas non plus que les paquets arriveront sur l’interface attendue ni que toutes les règles seront pertinentes pour le trafic de l’organisation.

> **Astuce :** Gardez une copie de la configuration et des règles avant chaque changement ; notez la version de Suricata, la date de mise à jour des règles, l’interface de capture, la valeur de `HOME_NET` et les commandes de validation utilisées. Sans ces informations, comparer deux résultats devient difficile.

### 2.2 Définir les réseaux et vérifier la configuration

Dans un fichier de configuration Suricata, `HOME_NET` doit représenter les réseaux réellement protégés. Un réseau mal défini peut transformer une règle de flux interne/externe en détection inversée ou produire un volume d’alertes inutiles.

Exemple conceptuel de valeurs à vérifier dans `suricata.yaml` (la syntaxe environnante dépend du fichier complet) :

```yaml
vars:
  address-groups:
    HOME_NET: "[192.0.2.0/24,198.51.100.0/24]"
    EXTERNAL_NET: "!$HOME_NET"
```

Les plages `192.0.2.0/24` et `198.51.100.0/24` sont réservées à la documentation ; remplacez-les par les préfixes de votre laboratoire ou de votre environnement autorisé. N’utilisez pas cet exemple sans vérifier l’indentation et la structure de la configuration réellement installée.

### 2.3 Ajouter une règle locale de laboratoire

Conservez les règles locales dans le fichier prévu par la configuration de votre installation, souvent `local.rules`, et confirmez que ce fichier est référencé dans la liste des fichiers de règles. Ajoutez une règle de test avec un `sid` réservé au laboratoire et unique dans votre jeu de règles.

```text
alert http $HOME_NET any -> $EXTERNAL_NET any (
  msg:"LAB HTTP marqueur pedagogique";
  flow:established,to_server;
  http.uri;
  content:"/training-check";
  startswith;
  sid:1001001;
  rev:1;
)
```

Après avoir enregistré la règle :

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml
```

Si la validation échoue, lisez le numéro de ligne et les options signalées. Vérifiez en particulier les points-virgules, parenthèses, options du protocole, identifiant `sid` et inclusion du fichier dans la configuration. Une syntaxe valide ne garantit pas qu’une règle se déclenche : il faut ensuite générer le trafic de laboratoire et lire l’événement JSON ou le journal d’alerte configuré.

### 2.4 Observer les alertes EVE JSON

Sur de nombreuses installations, les événements sont écrits dans `eve.json`. Vérifiez d’abord le chemin exact dans la configuration, puis inspectez les nouveaux événements pendant le test :

```bash
sudo tail -f /var/log/suricata/eve.json
```

Pour extraire uniquement les événements d’alerte lorsque `jq` est installé :

```bash
sudo jq 'select(.event_type == "alert") | {timestamp,src_ip,dest_ip,proto,alert}' \
  /var/log/suricata/eve.json
```

Selon la configuration, le fichier peut être ailleurs, être rotaté ou contenir des événements en plus des alertes. N’ajoutez pas de sorties excessives sans surveiller le débit disque. La journalisation riche peut être coûteuse en volume et contenir des informations sensibles.

Pour une alerte, recueillez au minimum : timestamp avec fuseau, source et destination, ports, protocole, identifiant et révision de règle, action, interface/capteur, flux ou identifiant de corrélation disponible, et contexte de l’actif cible. Stockez les preuves conformément à la politique de conservation.

### 2.5 Capturer et reproduire un cas

Dans un laboratoire contrôlé, vous pouvez inspecter un PCAP sans écouter une interface en direct :

```bash
sudo suricata -r lab-traffic.pcap -c /etc/suricata/suricata.yaml -l ./suricata-output
```

Examinez ensuite le répertoire de sortie. Cette méthode est utile pour rejouer un cas reproductible après une mise à jour de règles. Notez toutefois que le traitement hors ligne n’est pas équivalent à l’exploitation en direct : il ne reproduit pas nécessairement les pertes NIC, les contraintes de temps réel, la concurrence de flux ni les conditions exactes de production.

Pour construire un cas bénin, utilisez un serveur et un client de test que vous contrôlez, puis envoyez une requête avec le chemin `/training-check`. Comparez trois éléments :

1. la requête observée dans une capture indépendante ;
2. l’événement que le moteur a décodé ;
3. la règle qui a provoqué l’alerte.

Si un élément manque, identifiez à quelle étape le signal s’est perdu. Une règle peut être valide mais non chargée ; le trafic peut ne pas passer par l’interface ; le flux peut être chiffré ; ou l’événement peut être écrit dans un autre fichier.

### 2.6 Utiliser les statistiques et les compteurs

Les compteurs sont essentiels pour différencier « aucune menace détectée » de « visibilité insuffisante ». Suricata expose des statistiques périodiques dont le contenu dépend de la version et du mode de capture. Vérifiez le fichier configuré (`stats.log`, EVE ou autre) et suivez les compteurs de paquets, pertes, erreurs de capture, files et événements.

Une méthode d’observation reproductible :

- relever les compteurs avant le test ;
- lancer un flux connu et bénin ;
- vérifier l’incrémentation des compteurs de capture et de décodage ;
- vérifier qu’une signature connue du laboratoire déclenche l’événement prévu ;
- observer CPU, mémoire et stockage pendant le test ;
- revenir à l’état initial et noter les différences.

### 2.7 Laboratoire : mesurer un faux positif

Imaginons une règle qui signale chaque requête DNS vers un domaine classé suspect par une liste externe. Dans le banc d’essai, un service interne utilise ce domaine comme nom de test. La règle déclenche : le moteur fonctionne, mais sa classification est incorrecte dans ce contexte.

Procédure :

1. Copier l’événement de test dans un dossier de travail protégé, en masquant les données inutiles.
2. Vérifier la source et la date de la liste de réputation.
3. Résoudre le nom et identifier l’actif qui a émis la requête, sans cliquer sur un lien ni exécuter de fichier inconnu.
4. Corréler les journaux DNS, proxy et application.
5. Déterminer si le trafic est effectivement légitime ou si l’utilisation du domaine est inattendue.
6. Ajuster une exception aussi ciblée que possible : hôte, service, contexte ou durée ; éviter une exclusion globale.
7. Rejouer un PCAP autorisé contenant le cas légitime et un cas malveillant de test afin de vérifier que la règle garde une valeur de détection.

> **Piège :** Une exception par adresse IP peut devenir dangereuse si l’adresse est partagée, réattribuée ou héberge de nombreux services. Préférez une exception contextualisée, documentée, révisable et limitée dans le temps lorsque c’est possible.

### 2.8 Distinguer alerte, drop et session interrompue

Un moteur en mode détection peut produire une alerte sans agir sur le trafic. Un mode prévention peut laisser passer ou bloquer selon l’action de règle, le mode de capture, l’intégration du système d’exploitation et les paramètres de la politique. La présence d’un message d’alerte ne prouve donc pas que le paquet a été abandonné.

Pour confirmer une action :

- lire le champ action de l’événement lorsqu’il est renseigné ;
- contrôler les statistiques et journaux du mode IPS ;
- vérifier la progression du flux et la réponse observée au point de terminaison ;
- comparer une capture côté entrée et côté sortie, si l’architecture permet cette observation ;
- tester le comportement avec une règle contrôlée dans un environnement isolé ;
- confirmer que l’équipement est réellement en ligne et que le mode de prévention est actif.

Une règle peut être configurée en blocage sans que le chemin matériel ou logiciel applique ce blocage comme attendu. À l’inverse, un flux peut être coupé par un pare-feu voisin et donner l’impression que l’IPS l’a bloqué. La preuve doit relier l’événement à l’action réellement observée.

---

## 3. Dépannage et sécurité

### 3.1 Méthode d’investigation reproductible

Lorsqu’une alerte apparaît, évitez de modifier immédiatement les règles. Suivez un ordre stable :

1. **Préserver le contexte** : horodatage, capteur, identifiant de règle, révision, 5-tuple et action observée.
2. **Vérifier la visibilité** : compteurs de perte, sens de capture, réassemblage, TLS et état du moteur.
3. **Reconstituer le flux** : déterminer quel équipement a initié la communication et quel service était visé.
4. **Examiner l’évidence** : données de protocole, contenu visible, séquence temporelle et journaux adjacents.
5. **Qualifier le risque** : actif exposé, privilèges, criticité, caractère reproductible et impact potentiel.
6. **Choisir une réponse proportionnée** : surveiller, bloquer temporairement, isoler, limiter ou escalader.
7. **Valider et documenter** : preuve avant/après, faux positifs recherchés, retour arrière et propriétaire de l’exception.

Les règles d’escalade doivent être définies à l’avance. Une alerte sur un serveur critique exposé à Internet peut nécessiter une qualification urgente ; un scan connu d’un scanner d’entreprise peut être consigné et rapproché de son planning. Une étiquette de sévérité seule ne remplace pas le contexte.

### 3.2 Scénarios de dépannage

#### Cas A — Le moteur ne génère aucune alerte

Hypothèses possibles : interface incorrecte, SPAN configuré dans le mauvais sens, trafic absent, règles non chargées, variable `HOME_NET` incohérente, port applicatif non décodé, contenu chiffré, règle qui ne correspond pas au flux, perte de capture ou sortie de journal déplacée.

Plan de vérification :

```bash
ip -br addr
sudo suricata -T -c /etc/suricata/suricata.yaml
sudo tail -n 100 /var/log/suricata/suricata.log
sudo tail -n 30 /var/log/suricata/eve.json
```

Vérifiez aussi le nom et l’état de l’interface, les compteurs reçus/perdus et la présence de la règle dans la configuration. Le chemin d’alerte peut dépendre du fichier et de la distribution. Ne modifiez pas la politique réseau avant d’avoir confirmé que le capteur observe réellement le flux.

#### Cas B — Trop de faux positifs après mise à jour

Comparez la date et la révision du jeu de règles, le volume d’alertes par `sid`, les actifs concernés et les changements récents d’application. Identifiez si le problème touche une règle particulière, un réseau entier ou un type de trafic. Rejouez les PCAP autorisés pertinents si possible. Réduisez ou désactivez temporairement une règle seulement avec un ticket, un propriétaire, une échéance et une vérification du risque résiduel.

#### Cas C — Le capteur détecte les premières connexions, mais manque la suite

Vérifiez l’asymétrie du routage, les expirations de flux, les pertes et les limites de ressources. Comparez les captures d’entrée/sortie et contrôlez si le capteur voit les deux directions de la session. Examinez la capacité de capture et le débit des journaux. Si les événements disparaissent sous charge, la priorité est d’améliorer la visibilité et la capacité avant de conclure que l’activité s’est arrêtée.

#### Cas D — Une règle apparaît en alerte, mais le client se connecte toujours

L’alerte ne prouve pas un blocage. Confirmez l’action configurée, le mode IDS/IPS, la position inline, les capacités de capture et la prise en compte des actions `drop`. Testez avec une règle de laboratoire bénigne et un client/serveur contrôlés. Si plusieurs équipements peuvent bloquer, identifiez lequel a réellement interrompu le flux par des journaux et des captures corrélées.

#### Cas E — Une signature HTTP ne s’active plus après migration vers HTTPS

Vérifiez où TLS se termine. Si le capteur ne reçoit que les paquets chiffrés, le chemin URI n’est pas disponible dans ce point de capture. Déplacez la détection vers le proxy qui termine TLS, utilisez les journaux du WAF ou examinez les métadonnées TLS si cela répond au besoin. Ne concluez pas que la signature est cassée sans reconnaître le changement de visibilité.

### 3.3 Sécuriser la chaîne d’inspection

Le capteur et ses journaux font eux-mêmes partie de la surface d’attaque. Un adversaire peut tenter de saturer le traitement, d’inonder le SIEM, de produire des chaînes très volumineuses ou de déclencher des règles coûteuses. Les journaux peuvent contenir des informations personnelles, des URI sensibles, des adresses internes ou des fragments de contenu.

Contrôles recommandés :

- limiter les privilèges du compte de service et protéger les fichiers de règles ;
- mettre à jour le moteur et ses règles depuis des sources vérifiées ;
- tester les mises à jour dans un environnement de préproduction ;
- surveiller les pertes de paquets, la mémoire, le CPU et le stockage ;
- protéger l’accès au PCAP et les exporter uniquement via des canaux autorisés ;
- appliquer une politique de conservation, de masquage et de suppression des données ;
- synchroniser l’horloge des capteurs et des systèmes corrélés ;
- conserver les changements de règles dans un système versionné avec approbation ;
- prévoir un plan de fonctionnement dégradé et de retour arrière.

> **Danger :** N’activez pas le déchiffrement TLS de manière improvisée et ne copiez pas les clés privées dans les journaux ou les dépôts de code. L’inspection chiffrée exige une autorisation explicite, une gestion stricte des clés, des contrôles d’accès et une analyse des conséquences sur la confidentialité et la disponibilité.

### 3.4 Journalisation, horodatage et preuves

Une enquête corrélée n’est fiable que si les horodatages sont cohérents. Synchronisez les équipements de capture, les serveurs, les proxys et la plateforme SIEM via une source de temps approuvée. Conservez le fuseau ou l’offset, la précision de l’horloge et l’origine de chaque événement. Lorsque les horodatages dérivent, l’ordre des événements peut paraître impossible et conduire à une mauvaise hypothèse.

Pour préserver une preuve, enregistrez le fichier original, sa provenance, le moment de collecte, l’opérateur, les commandes utilisées et une empreinte cryptographique. Travaillez sur des copies lorsque le format le permet. Évitez de transmettre des captures contenant des données sensibles via des canaux non approuvés.

### 3.5 Plan de changement d’une règle

Un changement de signature ou de politique de prévention doit comporter :

- objectif et menace couverte ;
- actif, flux et direction visés ;
- source de la règle, version et propriétaire ;
- résultats de tests positifs et négatifs ;
- effet anticipé sur la latence et le débit ;
- mode d’observation initial ou durée limitée en alerte seule, si adapté ;
- seuils de succès et d’échec ;
- procédure de retour arrière ;
- personne qui approuve le passage en prévention ;
- suivi après déploiement et date de révision.

Une règle devrait être supprimée ou révisée si elle n’est plus utile, si son contenu dépend d’un service disparu, si elle cause trop de faux positifs ou si elle consomme des ressources disproportionnées. Une politique de détection qui accumule indéfiniment des règles non utilisées se dégrade et devient difficile à exploiter.

### 3.6 Exercice guidé : analyser une alerte

**Situation :** un NIDS remonte une alerte sur une requête HTTP vers un serveur de préproduction. Le serveur répond normalement. L’équipe doit décider si l’événement est malveillant ou attendu.

**Étape 1 — Vérifier la règle.** Notez `sid`, révision, message, protocole et conditions du match. Déterminez si la règle s’appuie sur un chemin, un en-tête, un motif de contenu ou un comportement agrégé.

**Étape 2 — Confirmer le flux.** Vérifiez les adresses et ports, l’état TCP, la direction, l’interface de capture et l’heure. Assurez-vous que l’adresse correspond bien au serveur concerné et non à un proxy ou à une traduction NAT.

**Étape 3 — Collecter l’évidence.** À partir d’une capture autorisée et des journaux du serveur, déterminez si l’URI ou le champ suspect était réellement présent et si la transaction a été complète. Les journaux côté serveur constituent un élément complémentaire : ils ne remplacent pas la preuve du contenu vu par le capteur.

**Étape 4 — Qualifier.** Comparez l’événement au test, au déploiement ou au scanner de sécurité planifié. Le simple fait qu’un environnement soit de préproduction ne signifie pas que toute activité y est permise.

**Étape 5 — Répondre.** Si le test est autorisé, documentez le faux positif et ajoutez une exception précise si elle est nécessaire. Si le trafic est inattendu, conservez les preuves, vérifiez les systèmes adjacents et escaladez.

**Étape 6 — Valider.** Rejouez un cas positif contrôlé et un cas négatif représentatif. Documentez le résultat ainsi que le risque qui subsiste.

### 3.7 Checklist opérationnelle

Avant mise en service :

- [ ] Les réseaux internes/externe et les interfaces de capture sont exacts.
- [ ] Le moteur et les règles sont à une version connue et sauvegardée.
- [ ] Les alertes de laboratoire produisent les événements attendus.
- [ ] Les compteurs de perte de capture sont surveillés.
- [ ] Le volume de journalisation est dimensionné et les accès sont limités.
- [ ] Les seuils de faux positifs et les propriétaires de règles sont définis.
- [ ] Le mode IDS, IPS, fail-open ou fail-closed est documenté.
- [ ] Le retour arrière a été testé et les rôles de décision sont connus.
- [ ] Les horaires des capteurs et des systèmes corrélés sont synchronisés.
- [ ] Le traitement du trafic TLS et des données sensibles est explicite.

Après une alerte importante :

- [ ] Préserver l’horodatage, les champs de flux et la version de règle.
- [ ] Vérifier la santé du capteur et les pertes avant de conclure.
- [ ] Corréler aux journaux DNS, proxy, WAF, endpoint et application appropriés.
- [ ] Qualifier le niveau de confiance et l’impact métier.
- [ ] Documenter toute action de blocage et son résultat réel.
- [ ] Fermer ou réviser la règle avec une preuve de test.

---

## Points à retenir

- IDS signifie détection ; IPS peut prévenir lorsque le moteur se trouve dans le chemin de données et que la politique autorise l’action.
- Le DPI dépend du suivi de flux, du réassemblage, du décodage de protocole et de la visibilité disponible.
- Une règle valide syntaxiquement peut ne jamais correspondre au trafic réel ; une alerte n’implique pas automatiquement un blocage.
- Les signatures, l’analyse comportementale, la réputation et la corrélation apportent des signaux différents qu’il faut combiner avec prudence.
- TLS limite l’inspection du contenu depuis un capteur externe ; les métadonnées et le point de terminaison chiffré peuvent fournir des perspectives complémentaires.
- Les faux positifs doivent être traités par des exceptions ciblées, testées, documentées et révisables.
- Les pertes de capture, la saturation CPU/mémoire et le retard de journalisation peuvent créer des angles morts.
- Toute règle active de prévention doit être testée, versionnée, mesurée et accompagnée d’un retour arrière.

### Références et lectures complémentaires

- Suricata User Guide — règles et moteur de détection : https://docs.suricata.io/en/latest/
- Suricata — configuration EVE JSON : https://docs.suricata.io/en/latest/output/eve/index.html
- Suricata — gestion des règles : https://docs.suricata.io/en/latest/rules/index.html
- Snort 3 Documentation : https://docs.snort.org/
- IETF RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3 : https://www.rfc-editor.org/rfc/rfc8446
- IETF RFC 9293 — Transmission Control Protocol (TCP) : https://www.rfc-editor.org/rfc/rfc9293
- NIST SP 800-94 — Guide to Intrusion Detection and Prevention Systems (IDPS) : https://csrc.nist.gov/pubs/sp/800/94/final
- MITRE ATT&CK — Network Service Discovery et techniques de détection : https://attack.mitre.org/

