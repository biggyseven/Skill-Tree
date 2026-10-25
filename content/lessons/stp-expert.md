# Spanning Tree Protocol (STP) — Niveau Expert

**Niveau :** Expert  
**Durée indicative :** 4 à 6 heures, selon les laboratoires  
**Prérequis :** maîtriser les cours Débutant et Intermédiaire : boucles de couche 2, BPDU, Bridge ID, Root Bridge, critères de sélection d'un port, RSTP, Rapid-PVST+, PVST+, MSTP, protections STP et commandes de diagnostic.  
**Environnement recommandé :** Packet Tracer pour les scénarios compatibles ; idéalement des commutateurs Cisco IOS/IOS XE ou une maquette virtuelle pour les sorties de commandes avancées ; Wireshark et captures de ports SPAN/TAP pour l'analyse des BPDU.

Ce cours poursuit `stp-debutant.md` et `stp-intermediaire.md`. Il évite de reprendre pas à pas les bases et met l'accent sur la conception déterministe, les frontières de région MST, les mécanismes de convergence, les protections de topologie, la recherche de preuves lors d'un incident et la gestion du risque en production. Les commandes sont des exemples Cisco IOS/IOS XE : leur prise en charge et leur syntaxe doivent être confirmées sur le modèle et la version réels.

> **Règle d'exploitation :** ne désactive pas STP pour faire disparaître une boucle apparente. Capture l'état initial, établis une hypothèse, modifie un seul paramètre à la fois et démontre le rétablissement avec des contrôles avant/après.

## Objectifs pédagogiques

À la fin de ce cours, tu dois pouvoir :

- concevoir une stratégie de racine primaire et secondaire prévisible pour chaque instance STP ;
- expliquer comment RSTP utilise les rôles de ports, les BPDU et les échanges proposal/agreement pour accélérer certaines transitions ;
- construire et vérifier une région MST cohérente, notamment le nom, la révision et le mappage VLAN-instance ;
- anticiper les effets des frontières MST/PVST+ et d'une migration de mode STP ;
- choisir Root Guard, Loop Guard, BPDU Guard, BPDU Filter, UDLD ou storm control selon le défaut visé, sans les confondre ;
- diagnostiquer des changements de topologie répétés, des MAC flaps, un port inconsistent, une racine inattendue ou une convergence dégradée ;
- établir une procédure de changement et de retour arrière qui limite le domaine d'impact ;
- produire un rapport d'incident fondé sur des observations et des preuves, et non sur des suppositions.

## Comment utiliser ce cours

Lis d'abord les parties de conception et de sélection de racine. Utilise les SVG comme modèles de lecture de topologie, pas comme représentation chronométrée exacte de chaque implémentation. Ensuite, réalise les laboratoires dans l'ordre : choix de racine, protections, MST puis incident multi-cause. Les commandes qui modifient la topologie sont réservées à un laboratoire isolé ou à une fenêtre de changement approuvée.


## 1. Concevoir STP comme une politique de disponibilité

### 1.1. La question experte n'est pas seulement « quelle liaison est bloquée ? »

Un déploiement STP fiable répond à quatre questions explicites :

1. **Qui doit être la racine ?** Le Root Bridge doit être choisi par conception, en fonction des passerelles, des liaisons montantes et du chemin attendu du trafic.
2. **Quel chemin doit être préféré ?** Les coûts, les rôles et les critères de départage doivent produire une topologie active conforme au schéma d'architecture.
3. **Quel défaut doit être contenu ?** Une BPDU reçue sur un port de bordure, une perte de BPDU sur un trunk et l'annonce d'une racine non autorisée sont trois événements différents.
4. **Quelle preuve démontre que le changement est sûr ?** La présence d'un état `forwarding` ne suffit pas : il faut aussi vérifier la racine, le chemin, les VLAN impactés, les trunks, les agrégats et les services.

Une topologie peut être sans boucle tout en étant mal conçue : la racine est placée sur un commutateur d'accès, les liens actifs sont asymétriques, les chemins redondants ne sont pas ceux prévus, ou une instance traverse un lien surchargé. STP garantit une topologie sans boucle selon le protocole ; il ne garantit pas, à lui seul, le meilleur trajet applicatif.

### 1.2. Définir les invariants du réseau

Avant de modifier des priorités ou des protections, rédige les invariants à préserver :

- les commutateurs de distribution ou de cœur désignés portent la racine des instances prévues ;
- un second commutateur est prêt à prendre la racine en cas de panne, sans gagner dans le fonctionnement normal ;
- les ports vers les terminaux sont traités comme ports de bordure uniquement lorsqu'aucun pont n'est attendu derrière eux ;
- chaque trunk transporte seulement les VLAN requis par l'architecture ;
- les membres d'un EtherChannel utilisent des paramètres compatibles et sont traités par STP comme un lien logique ;
- les régions MST ont des paramètres strictement cohérents sur les commutateurs censés appartenir à la même région ;
- aucune protection n'est placée sans définir l'événement attendu, l'état résultant et la procédure de rétablissement.

### 1.3. Schéma : racine contrôlée et chemin de secours

<div class="lesson-figure">
<svg viewBox="0 0 860 360" role="img" aria-label="Topologie STP avec racine principale, racine secondaire et chemin alternatif bloqué" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs><marker id="expert-root-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#38bdf8"/></marker></defs>
  <rect x="8" y="8" width="844" height="344" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="430" y="35" fill="#e2e8f0" font-size="17" font-weight="700" text-anchor="middle">Instance VLAN 10 — topologie attendue</text>
  <path d="M170 144 L380 144" stroke="#38bdf8" stroke-width="5" fill="none"/>
  <path d="M480 144 L690 144" stroke="#38bdf8" stroke-width="5" fill="none"/>
  <path d="M170 170 L380 270 L690 170" stroke="#f59e0b" stroke-width="4" stroke-dasharray="9 7" fill="none"/>
  <rect x="85" y="105" width="170" height="78" rx="12" fill="#0f3b48" stroke="#22d3ee" stroke-width="2"/>
  <text x="170" y="133" fill="#cffafe" text-anchor="middle" font-size="14" font-weight="700">SW-DIST-1</text><text x="170" y="154" fill="#67e8f9" text-anchor="middle" font-size="12">Racine préférée</text>
  <rect x="345" y="105" width="170" height="78" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/>
  <text x="430" y="133" fill="#dbeafe" text-anchor="middle" font-size="14" font-weight="700">SW-DIST-2</text><text x="430" y="154" fill="#93c5fd" text-anchor="middle" font-size="12">Racine secondaire</text>
  <rect x="605" y="105" width="170" height="78" rx="12" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/>
  <text x="690" y="133" fill="#f1f5f9" text-anchor="middle" font-size="14" font-weight="700">SW-ACCESS-1</text><text x="690" y="154" fill="#cbd5e1" text-anchor="middle" font-size="12">Accès utilisateurs</text>
  <circle r="6" fill="#f8fafc" stroke="#38bdf8" stroke-width="3"><animateMotion dur="1.7s" repeatCount="indefinite" path="M255 144 L345 144"/></circle>
  <circle r="6" fill="#f8fafc" stroke="#38bdf8" stroke-width="3"><animateMotion dur="1.7s" begin="0.85s" repeatCount="indefinite" path="M515 144 L605 144"/></circle>
  <rect x="330" y="246" width="200" height="48" rx="10" fill="#422006" stroke="#f59e0b"/>
  <text x="430" y="266" fill="#fde68a" text-anchor="middle" font-size="12" font-weight="700">Chemin alternatif</text><text x="430" y="282" fill="#fcd34d" text-anchor="middle" font-size="11">non transférant dans l'état stable</text>
  <text x="430" y="326" fill="#cbd5e1" text-anchor="middle" font-size="12">La racine et le chemin actif sont définis par la conception, puis vérifiés en CLI.</text>
</svg>
</div>

Le schéma montre une intention d'architecture, pas une topologie exhaustive : dans une vraie conception, les rôles et états se calculent séparément pour chaque instance. Le commutateur nommé « racine secondaire » n'est pas automatiquement la racine ; il doit recevoir une priorité moins favorable que la racine principale, mais plus favorable que les autres ponts attendus.

### 1.4. Priorités : éviter une racine gagnante par accident

Dans les implémentations Cisco classiques, les valeurs de priorité STP sont configurées par pas de 4096 afin de laisser une place à l'Extended System ID. La priorité effective du Bridge ID tient compte du VLAN dans les modes par VLAN. La valeur affichée et les commandes acceptées doivent être contrôlées sur l'équipement.

Exemple de stratégie pour Rapid-PVST+ :

```cisco
! Exemple de laboratoire — VLAN 10
SW-DIST-1(config)# spanning-tree vlan 10 priority 24576
SW-DIST-2(config)# spanning-tree vlan 10 priority 28672
```

La valeur la plus basse gagne, à condition que les autres composants du Bridge ID et les priorités effectives conduisent bien à ce résultat. Il est souvent plus simple d'utiliser `spanning-tree vlan 10 root primary` et `root secondary` sur les plateformes qui prennent ces macros en charge, mais il faut lire la priorité effectivement appliquée et éviter de considérer la macro comme une preuve suffisante.

Vérifications :

```cisco
show spanning-tree vlan 10
show spanning-tree root
show spanning-tree summary
```

Consigne experte : documente les priorités attendues pour chaque VLAN ou instance. N'applique pas une priorité uniforme sur tous les commutateurs en espérant obtenir la bonne topologie.

### 1.5. Coûts et critères de départage

Le choix du Root Port résulte d'une comparaison d'informations de chemin vers la racine. Le coût total n'est qu'un des critères : si plusieurs chemins partagent le même coût, les identifiants de pont et de port annoncés participent au départage. Le détail des valeurs de coût par débit et la méthode de calcul peuvent varier avec le mode historique ou le coût étendu ; ne déduis pas un rôle à partir de la seule vitesse physique.

Pour prouver le chemin choisi, relève au minimum :

- le Root ID et le Bridge ID local ;
- le coût de chemin vers la racine ;
- le rôle et l'état de chaque port concerné ;
- le coût configuré et l'identifiant du port local ;
- les informations du voisin quand elles sont disponibles.

Une correction doit viser la cause : coût incorrect, priorité d'un port, racine mal placée, lien logique mal formé ou design non équilibré. Modifier plusieurs coûts au hasard rend la topologie plus difficile à expliquer et peut déplacer des chemins d'autres VLAN.


## 2. RSTP en profondeur : convergence et synchronisation

### 2.1. Une convergence rapide repose sur des conditions, pas sur un simple temporisateur

RSTP ajoute des mécanismes qui accélèrent la transition des ports dans les topologies compatibles. Les liens point-à-point full-duplex et les ports de bordure se prêtent à des transitions rapides ; un segment partagé ou une interconnexion mal catégorisée ne présente pas les mêmes conditions. Le comportement dépend du voisin, du mode STP négocié ou configuré, des protections et de la stabilité physique.

Les rôles RSTP incluent notamment Root, Designated, Alternate et Backup. Un rôle décrit la fonction du port dans l'arbre actif, tandis qu'un état décrit son comportement de transfert. Un port Alternate peut rester physiquement up tout en ne transférant pas les trames utilisateur : c'est souvent précisément ce qui empêche une boucle.

### 2.2. Proposal/agreement : transition contrôlée

Dans RSTP, un pont désigné sur un lien point-à-point peut proposer une nouvelle information de topologie. Le pont voisin synchronise les ports concernés avant d'accepter la transition et de renvoyer l'accord. Ce mécanisme évite de supposer qu'un port peut passer en transfert rapidement sans s'assurer que les chemins contradictoires sont maîtrisés.

<div class="lesson-figure">
<svg viewBox="0 0 860 320" role="img" aria-label="Échange proposal et agreement RSTP sur un lien point-à-point" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <rect x="8" y="8" width="844" height="304" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="430" y="34" text-anchor="middle" font-size="17" fill="#e2e8f0" font-weight="700">RSTP — échange de contrôle sur un lien point-à-point</text>
  <rect x="70" y="70" width="190" height="62" rx="12" fill="#123047" stroke="#38bdf8" stroke-width="2"/><text x="165" y="96" text-anchor="middle" fill="#e0f2fe" font-size="14" font-weight="700">Pont A</text><text x="165" y="115" text-anchor="middle" fill="#7dd3fc" font-size="12">port désigné</text>
  <rect x="600" y="70" width="190" height="62" rx="12" fill="#123047" stroke="#38bdf8" stroke-width="2"/><text x="695" y="96" text-anchor="middle" fill="#e0f2fe" font-size="14" font-weight="700">Pont B</text><text x="695" y="115" text-anchor="middle" fill="#7dd3fc" font-size="12">voisin RSTP</text>
  <path d="M260 92 H600" stroke="#38bdf8" stroke-width="3" fill="none"/><path d="M590 86 L600 92 L590 98" stroke="#38bdf8" stroke-width="3" fill="none"/>
  <circle r="6" fill="#f8fafc" stroke="#38bdf8" stroke-width="2"><animateMotion dur="2.6s" repeatCount="indefinite" path="M260 92 H600"/></circle>
  <text x="430" y="80" text-anchor="middle" fill="#bae6fd" font-size="12" font-weight="700">PROPOSAL</text>
  <path d="M600 120 H260" stroke="#34d399" stroke-width="3" fill="none"/><path d="M270 114 L260 120 L270 126" stroke="#34d399" stroke-width="3" fill="none"/>
  <circle r="6" fill="#f8fafc" stroke="#34d399" stroke-width="2"><animateMotion dur="2.6s" begin="1.3s" repeatCount="indefinite" path="M600 120 H260"/></circle>
  <text x="430" y="141" text-anchor="middle" fill="#a7f3d0" font-size="12" font-weight="700">AGREEMENT après synchronisation</text>
  <rect x="100" y="184" width="660" height="82" rx="12" fill="#111827" stroke="#475569"/>
  <text x="430" y="207" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">Séquence conceptuelle</text>
  <text x="430" y="229" text-anchor="middle" fill="#cbd5e1" font-size="12">Proposer → synchroniser les ports concernés → accepter la transition → confirmer</text>
  <text x="430" y="249" text-anchor="middle" fill="#94a3b8" font-size="11">Ne garantit pas une transition rapide sur tous les types de segments ou toutes les topologies.</text>
</svg>
</div>

Le diagramme simplifie la chronologie : il illustre le sens des messages et la synchronisation, mais ne remplace pas l'analyse des BPDUs réellement capturées. En dépannage, vérifie si l'interface fonctionne en point-à-point, si le voisin utilise un mode compatible et si des protections ou des incompatibilités empêchent la transition attendue.

### 2.3. Edge ports et ports de commutation

Un port de bordure est un port sur lequel on ne s'attend pas à découvrir un autre pont. PortFast est couramment utilisé pour accélérer l'activation d'un port terminal. BPDU Guard peut faire passer le port dans un état de protection ou err-disabled lorsqu'une BPDU inattendue est reçue, selon la configuration et la plateforme.

Un port relié à un téléphone IP avec un PC en aval, à un point d'accès, à un hyperviseur ou à un équipement qui réalise du pontage doit être évalué selon la topologie réelle. Le simple fait qu'un câble termine sur un équipement appelé « serveur » ne prouve pas qu'il s'agit d'un port de bordure : un hyperviseur peut relayer des trames entre plusieurs interfaces ou machines virtuelles.

### 2.4. TCN et effets sur les tables MAC

Un changement de topologie peut modifier la manière dont les adresses MAC dynamiques sont vieillies ou supprimées. Une vague de changements de topologie répétée peut contribuer à une instabilité perceptible, en particulier lorsqu'elle est combinée à des liens qui montent et descendent ou à des boucles.

Ne conclus pas qu'un TCN est la cause racine parce qu'il apparaît dans les journaux. C'est souvent un symptôme. Corrèle le port source, l'heure, les événements de couche physique, les changements de rôle STP, les messages MACFLAP et les journaux des équipements voisins.

Commandes usuelles :

```cisco
show spanning-tree detail
show spanning-tree vlan 10 detail
show logging
show interfaces status
show interfaces counters errors
show mac address-table dynamic vlan 10
```

Les filtres de sortie comme `| include` sont utiles mais la syntaxe varie. Conserve si possible les sorties complètes avant de réduire le diagnostic à un mot-clé.


## 3. Choisir la protection adaptée à la menace

Les protections STP ne sont pas interchangeables. Chacune répond à un type d'écart et peut interrompre un chemin utile si elle est placée au mauvais endroit.

| Mécanisme | Événement visé | Réaction typique | Placement usuel à valider |
|---|---|---|---|
| PortFast / edge | Transition d'un port terminal | Accélère le passage à l'état de transfert | Port où aucun pont n'est attendu |
| BPDU Guard | BPDU reçue sur un port de bordure protégé | Protège en désactivant/isolant le port selon la plateforme | Port terminal avec edge/PortFast |
| Root Guard | BPDU supérieure qui pourrait faire gagner une racine non souhaitée | Met le port dans un état root-inconsistent jusqu'à disparition de la condition | Port où le voisin ne doit jamais annoncer une meilleure racine |
| Loop Guard | Absence inattendue de BPDU sur un port normalement dépendant de ces messages | Empêche une transition qui pourrait créer une boucle, avec état inconsistent selon le cas | Liens de commutation appropriés, selon le design |
| BPDU Filter | Suppression ou ignorance des BPDU | Peut neutraliser la protection STP sur le port si mal utilisé | Cas étroitement contrôlés et documentés seulement |
| UDLD | Lien unidirectionnel sur supports compatibles | Détecte certaines défaillances d'émission/réception, avec réaction qui dépend du mode | Liens fibre/cuivre pris en charge et politique d'exploitation |
| Storm Control | Volume excessif de certaines classes de trames | Limite ou bloque le trafic selon les seuils | Selon profil, notamment certains ports d'accès |

### 3.1. Root Guard : empêcher une racine non autorisée

Root Guard sert à préserver la position de racine attendue sur un port. Lorsqu'un port protégé reçoit des informations qui indiqueraient un pont racine supérieur, l'équipement peut le placer en état `root-inconsistent`. Le port reprend normalement son fonctionnement une fois la condition disparue, selon le comportement de la plateforme.

Exemple de laboratoire :

```cisco
interface GigabitEthernet1/0/24
 description VERS_COMMUTATEUR_D_ACCES_NON_AUTORISE_A_DEVENIR_ROOT
 spanning-tree guard root
```

N'applique pas Root Guard sur une liaison qui doit légitimement fournir le meilleur chemin vers la racine. Le risque n'est pas d'empêcher un attaquant abstrait, mais d'empêcher un chemin prévu si le contrôle est posé sans analyse.

<div class="lesson-figure">
<svg viewBox="0 0 860 300" role="img" aria-label="Root Guard détecte une BPDU supérieure provenant d'un commutateur non autorisé" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <rect x="8" y="8" width="844" height="284" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="430" y="34" text-anchor="middle" font-size="17" font-weight="700" fill="#e2e8f0">Root Guard — contenir une racine inattendue</text>
  <rect x="55" y="96" width="200" height="78" rx="12" fill="#0f3b48" stroke="#22d3ee" stroke-width="2"/><text x="155" y="124" text-anchor="middle" fill="#cffafe" font-weight="700" font-size="14">SW-DIST</text><text x="155" y="146" text-anchor="middle" fill="#67e8f9" font-size="12">racine prévue</text>
  <rect x="605" y="96" width="200" height="78" rx="12" fill="#3f1d20" stroke="#fb7185" stroke-width="2"/><text x="705" y="124" text-anchor="middle" fill="#ffe4e6" font-weight="700" font-size="14">SW-INATTENDU</text><text x="705" y="146" text-anchor="middle" fill="#fda4af" font-size="12">annonce supérieure</text>
  <path d="M255 135 H605" stroke="#64748b" stroke-width="3" fill="none"/>
  <path d="M605 135 H518" stroke="#fb7185" stroke-width="4" stroke-dasharray="10 7" fill="none"/>
  <path d="M528 128 L518 135 L528 142" stroke="#fb7185" stroke-width="3" fill="none"/>
  <circle r="6" fill="#fff" stroke="#fb7185" stroke-width="3"><animateMotion dur="2.4s" repeatCount="indefinite" path="M605 135 H528"/></circle>
  <rect x="342" y="91" width="176" height="86" rx="12" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="430" y="116" text-anchor="middle" fill="#fde68a" font-weight="700" font-size="13">ROOT GUARD</text><text x="430" y="138" text-anchor="middle" fill="#fcd34d" font-size="11">root-inconsistent</text><text x="430" y="155" text-anchor="middle" fill="#fcd34d" font-size="10">port contenu</text>
  <text x="430" y="222" text-anchor="middle" fill="#e2e8f0" font-size="13" font-weight="700">Le port ne devient pas un chemin de racine valide</text>
  <text x="430" y="246" text-anchor="middle" fill="#94a3b8" font-size="12">Le trafic affecté peut être interrompu sur ce lien : valider le placement en conception.</text>
  <text x="430" y="266" text-anchor="middle" fill="#94a3b8" font-size="11">Le marqueur illustre la BPDU sur le lien, pas un paquet utilisateur.</text>
</svg>
</div>

### 3.2. Loop Guard et perte de BPDU

Loop Guard vise le scénario où un port qui devrait continuer à recevoir des informations STP cesse de recevoir les BPDUs attendues. Sans précaution, une interprétation incorrecte de l'absence d'information peut laisser le port devenir désigné et transférer des trames, dans une situation où une boucle est possible. L'implémentation peut placer le port dans un état `loop-inconsistent`.

Il faut différencier trois événements :

- **La BPDU supérieure est reçue :** elle peut influencer l'élection ou être contenue par Root Guard selon le port.
- **La BPDU attendue disparaît :** rechercher une panne unidirectionnelle, un problème de contrôle ou un comportement du voisin ; Loop Guard peut aider à contenir certains scénarios.
- **Le lien physique est défaillant :** l'interface, les compteurs, l'optique, le câble et UDLD peuvent fournir des indices complémentaires.

UDLD et Loop Guard ne remplacent pas l'un l'autre. UDLD recherche la nature unidirectionnelle d'un lien pris en charge ; Loop Guard agit dans la logique STP lorsqu'un port ne reçoit plus les informations attendues. Leur compatibilité et leur configuration doivent être vérifiées sur l'équipement.

### 3.3. BPDU Filter : une option à haut risque

BPDU Filter ne doit pas être présenté comme une protection générique. Selon l'endroit et la méthode de configuration, il peut empêcher l'émission ou le traitement des BPDUs et donc affaiblir ou neutraliser les mécanismes qui préviennent les boucles. Ne l'active pas sur des trunks ou des liaisons inter-commutateurs pour masquer des changements de topologie.

Pour sécuriser un port utilisateur, étudie d'abord PortFast/edge avec BPDU Guard, puis vérifie le comportement attendu si une BPDU est reçue. Toute utilisation de BPDU Filter doit répondre à un besoin bien délimité, faire l'objet d'une documentation et être validée selon la plateforme.

### 3.4. Storm Control : limitation, pas correction de boucle

Storm Control peut contenir le volume de certaines trames lorsque les seuils configurés sont atteints. Il ne corrige pas une topologie STP erronée et ne permet pas de déduire à lui seul la source de la boucle. Un seuil trop bas peut aussi limiter un trafic légitime, notamment lors de découvertes de service, de démarrages en masse ou de conditions inhabituelles.

Une stratégie de défense en profondeur combine une topologie STP correcte, des protections adaptées aux ports, des trunks restreints, des contrôles de tempête mesurés et de la supervision. Aucun de ces mécanismes n'est un substitut universel aux autres.


## 4. Concevoir une région MST maintenable

### 4.1. Le compromis entre instances par VLAN et instances partagées

Rapid-PVST+ calcule une instance par VLAN sur les plateformes qui le prennent en charge, ce qui permet de répartir des chemins par VLAN mais augmente le nombre d'instances à gérer. MSTP permet de mapper plusieurs VLAN vers une même instance MST, ce qui réduit le nombre d'instances de spanning tree tout en permettant des arbres logiques distincts selon le design.

Le gain en nombre d'instances s'accompagne d'une responsabilité : les commutateurs qui doivent appartenir à la même région doivent avoir une configuration compatible. Un changement involontaire du nom, de la révision ou du mappage VLAN-instance peut créer une frontière de région là où l'architecte pensait avoir une seule région.

### 4.2. Identité d'une région MST

Les paramètres structurants d'une région MST comprennent notamment :

- le nom de région ;
- le niveau de révision de configuration ;
- le mappage des VLAN vers les instances MST.

Les détails tels que l'encodage du mappage et le calcul du digest font partie de l'identité de région. Une valeur de révision identique ne suffit donc pas si le nom ou le mappage diffère. Un digest identique est un indice important de cohérence de configuration, à lire dans le contexte des commandes et des plateformes utilisées.

### 4.3. Diagramme : plusieurs VLAN, instances partagées

<div class="lesson-figure">
<svg viewBox="0 0 860 350" role="img" aria-label="Mappage de groupes de VLAN sur deux instances MST au sein d'une région commune" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <rect x="8" y="8" width="844" height="334" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="430" y="34" text-anchor="middle" fill="#e2e8f0" font-weight="700" font-size="17">MSTP — faire partager des arbres aux VLAN selon le design</text>
  <rect x="36" y="60" width="788" height="44" rx="10" fill="#172554" stroke="#60a5fa"/><text x="430" y="87" text-anchor="middle" fill="#dbeafe" font-size="13" font-weight="700">Région CAMPUS-MST · révision 7 · même mappage sur les membres</text>
  <rect x="50" y="126" width="220" height="70" rx="12" fill="#123047" stroke="#38bdf8"/><text x="160" y="151" text-anchor="middle" fill="#e0f2fe" font-weight="700" font-size="14">Groupe A</text><text x="160" y="174" text-anchor="middle" fill="#7dd3fc" font-size="12">VLAN 10, 20, 30</text>
  <path d="M270 161 H360" stroke="#38bdf8" stroke-width="4"/><circle r="6" fill="#fff" stroke="#38bdf8" stroke-width="2"><animateMotion dur="2.8s" repeatCount="indefinite" path="M270 161 H360"/></circle>
  <rect x="360" y="126" width="160" height="70" rx="12" fill="#0f3b48" stroke="#22d3ee"/><text x="440" y="151" text-anchor="middle" fill="#cffafe" font-weight="700" font-size="14">MSTI 1</text><text x="440" y="174" text-anchor="middle" fill="#67e8f9" font-size="12">arbre logique A</text>
  <rect x="590" y="126" width="220" height="70" rx="12" fill="#1e293b" stroke="#94a3b8"/><text x="700" y="151" text-anchor="middle" fill="#f1f5f9" font-weight="700" font-size="14">Chemins A</text><text x="700" y="174" text-anchor="middle" fill="#cbd5e1" font-size="12">racine / rôles de l'instance</text>
  <path d="M520 161 H590" stroke="#38bdf8" stroke-width="4"/>
  <rect x="50" y="218" width="220" height="70" rx="12" fill="#3b1f35" stroke="#f472b6"/><text x="160" y="243" text-anchor="middle" fill="#fce7f3" font-weight="700" font-size="14">Groupe B</text><text x="160" y="266" text-anchor="middle" fill="#f9a8d4" font-size="12">VLAN 40, 50</text>
  <path d="M270 253 H360" stroke="#f472b6" stroke-width="4"/><circle r="6" fill="#fff" stroke="#f472b6" stroke-width="2"><animateMotion dur="3.2s" repeatCount="indefinite" path="M270 253 H360"/></circle>
  <rect x="360" y="218" width="160" height="70" rx="12" fill="#422006" stroke="#f59e0b"/><text x="440" y="243" text-anchor="middle" fill="#fde68a" font-weight="700" font-size="14">MSTI 2</text><text x="440" y="266" text-anchor="middle" fill="#fcd34d" font-size="12">arbre logique B</text>
  <rect x="590" y="218" width="220" height="70" rx="12" fill="#1e293b" stroke="#94a3b8"/><text x="700" y="243" text-anchor="middle" fill="#f1f5f9" font-weight="700" font-size="14">Chemins B</text><text x="700" y="266" text-anchor="middle" fill="#cbd5e1" font-size="12">autre répartition planifiée</text>
  <path d="M520 253 H590" stroke="#f472b6" stroke-width="4"/>
  <text x="430" y="320" text-anchor="middle" fill="#94a3b8" font-size="11">MST réduit le nombre d'instances ; il n'abolit ni les frontières ni le besoin de cohérence.</text>
</svg>
</div>

Les VLAN 10, 20 et 30 partagent ici l'instance 1 ; les VLAN 40 et 50 partagent l'instance 2. Ce mappage est un exemple. Il doit correspondre à des exigences opérationnelles réelles et être identique dans toute la région concernée.

### 4.4. Configuration de laboratoire MST

Sur les commutateurs qui doivent appartenir à la même région :

```cisco
configure terminal
spanning-tree mode mst
spanning-tree mst configuration
 name CAMPUS-MST
 revision 7
 instance 1 vlan 10,20,30
 instance 2 vlan 40,50
 exit
end
```

Les syntaxes et les limites de révision/mappage doivent être vérifiées selon l'IOS/IOS XE. Ne copie pas ce bloc en production sans confirmer la table VLAN prévue et la compatibilité de tous les équipements de la région.

Contrôle :

```cisco
show spanning-tree mst configuration
show spanning-tree mst
show spanning-tree mst configuration digest
show spanning-tree root
show spanning-tree inconsistentports
```

La disponibilité de la dernière commande varie. Si la plateforme ne propose pas ce sous-commande, utilise les sorties de région documentées pour comparer les paramètres et le digest affichés.

### 4.5. Instance 0, IST et CIST

MST s'appuie sur une instance interne de spanning tree (IST) et sur un arbre commun qui permet de traiter les relations entre régions et équipements extérieurs. Pour le dépannage, il faut distinguer le rôle d'un port à l'intérieur d'une région MST de son comportement à une frontière. Les notions de CIST et de frontière ne peuvent pas être remplacées par une lecture de l'instance 1 seulement.

Lorsqu'un port de frontière relie une région MST à un équipement qui n'est pas dans la même région, l'interopérabilité s'appuie sur le comportement commun prévu par le protocole et l'implémentation. Les chemins vus par l'autre côté peuvent donc différer de ceux calculés à l'intérieur de la région. Observe les deux extrémités et ne tire pas de conclusion à partir d'une sortie isolée.

### 4.6. Éviter les changements de région involontaires

Avant une modification MST :

1. extraire le nom, la révision et la correspondance VLAN-instance de chaque commutateur attendu dans la région ;
2. comparer les valeurs, sans se fier uniquement à un libellé ou à une capture partielle ;
3. sauvegarder les configurations et les rôles STP actuels ;
4. modifier les membres selon une procédure cohérente, pendant une fenêtre maîtrisée ;
5. vérifier les sorties MST, les frontières, la racine de l'IST/CIST et les racines des instances ;
6. tester les VLAN représentatifs et les chemins de secours.

Une région qui se divise involontairement peut produire une topologie sans boucle mais une répartition des chemins différente, avec un chemin plus long ou une charge inattendue. L'absence de panne applicative immédiate ne signifie pas que la conception est restée conforme.


## 5. Interopérabilité et migration des modes STP

### 5.1. PVST+, Rapid-PVST+ et MSTP ne doivent pas être mélangés au hasard

Un réseau multi-constructeur ou en migration peut combiner des mécanismes STP différents, mais les limites d'interopérabilité doivent être prises en compte. PVST+/Rapid-PVST+ gèrent des instances par VLAN ; MSTP regroupe des VLAN dans des instances partagées. À la frontière, le protocole échange des informations selon les règles de compatibilité et de région.

Avant toute migration, établis une matrice :

| Commutateur | Mode actuel | Mode cible | Racine prévue | Région / VLAN concernés | Fenêtre / retour arrière |
|---|---|---|---|---|---|
| DIST-A | Rapid-PVST+ | MSTP | CIST + MSTI | VLAN 10–50 | à renseigner |
| DIST-B | Rapid-PVST+ | MSTP | CIST + MSTI | VLAN 10–50 | à renseigner |
| ACC-1 | Rapid-PVST+ | MSTP ou frontière | dépend du design | VLAN 10, 20, 30 | à renseigner |

Cette table est un gabarit, pas une recommandation de migrer immédiatement. La migration peut changer les rôles de ports et les chemins actifs ; réalise-la d'abord en environnement de test et vérifie la documentation du constructeur pour la séquence de transition prise en charge.

### 5.2. Risques aux frontières MST/PVST+

Les symptômes possibles d'une incompatibilité ou d'un mauvais design de frontière incluent :

- des ports qui adoptent des rôles inattendus ;
- des chemins actifs différents de ceux prévus pour certains VLAN ;
- une racine différente de la racine de conception ;
- des messages d'incohérence ou de compatibilité STP ;
- des changements de topologie répétés ou une charge déséquilibrée.

Ne corrige pas automatiquement ces symptômes en changeant la priorité de nombreux VLAN. Commence par déterminer quel protocole est actif sur chaque équipement, quelles instances sont échangées à la frontière et où doit se trouver la racine logique. Une modification de priorité peut masquer le problème pour un VLAN et l'aggraver pour un autre.

### 5.3. Procédure de migration contrôlée

**Avant le changement**

- inventorier les modèles, versions logicielles, modes et capacités STP ;
- relever les sorties `show spanning-tree`, `show spanning-tree root`, `show spanning-tree summary` et, si MST, la configuration et le digest de région ;
- identifier le root primaire/secondaire et les liens redondants ;
- déterminer les VLAN critiques, les passerelles et les chemins applicatifs ;
- sauvegarder les configurations et préparer les étapes de retour arrière ;
- s'assurer d'un accès hors bande si une perte de connectivité de gestion est possible.

**Pendant le changement**

- suivre l'ordre validé dans le plan de migration ;
- ne changer qu'un élément de configuration par étape autant que possible ;
- surveiller les logs et les rôles/états de ports ;
- arrêter la progression en présence d'une racine inattendue, d'un port inconsistent non prévu ou d'une perte de connectivité qui dépasse le seuil accepté.

**Après le changement**

- vérifier la racine et le chemin actif de chaque instance importante ;
- confirmer les trunks, EtherChannels, VLAN et états des ports ;
- tester les communications des terminaux vers la passerelle et les services essentiels ;
- comparer l'architecture observée à l'architecture attendue ;
- documenter les résultats et conserver les sorties CLI.


## 6. Diagnostic expert basé sur les preuves

### 6.1. Une chaîne de diagnostic reproductible

Un diagnostic STP doit séparer l'observation, l'hypothèse, le test et la correction :

1. **Observation :** la racine est inattendue, les MAC flappent ou une application perd des paquets.
2. **Périmètre :** identifier VLAN, instance, commutateurs et interfaces affectés.
3. **Hypothèse :** racine mal placée, lien unidirectionnel, boucle physique, EtherChannel incohérent, BPDU absentes, port de bordure mal défini ou conflit de région MST.
4. **Test discriminant :** choisir une commande, une capture ou une vérification physique qui pourrait confirmer ou invalider l'hypothèse.
5. **Correction minimale :** appliquer un changement réversible qui traite la cause démontrée.
6. **Validation :** vérifier les états STP, la table MAC, les compteurs et la connectivité après convergence.
7. **Prévention :** documenter le problème récurrent, les protections et les contrôles à ajouter.

### 6.2. Outils et commandes

```cisco
show spanning-tree
show spanning-tree vlan 10 detail
show spanning-tree root
show spanning-tree summary
show spanning-tree inconsistentports
show spanning-tree interface GigabitEthernet1/0/48 detail
show interfaces status
show interfaces trunk
show etherchannel summary
show logging
show mac address-table dynamic vlan 10
show interfaces counters errors
```

Toutes les variantes ne sont pas disponibles sur chaque plateforme. Utilise `?` et le guide de commande correspondant à l'IOS/IOS XE pour identifier les sous-commandes supportées. Dans un incident réel, exporte les sorties complètes, l'heure des captures et les événements horodatés avant de filtrer le contenu.

### 6.3. Lire un MAC flapping sans conclure trop tôt

Un message de type MACFLAP indique qu'une même adresse source est apprise sur des interfaces différentes dans une période rapprochée. Une boucle de couche 2 est une cause fréquente, mais pas la seule : interfaces instables, câblage incorrect, mauvaise configuration d'agrégat ou duplication d'adresse peuvent également contribuer.

Méthode :

- noter la MAC, le VLAN et les deux interfaces citées ;
- vérifier si ces ports sont trunks, ports d'accès, ports membres d'un EtherChannel ou ports de bordure ;
- examiner les voisins et la topologie physique ;
- vérifier le rôle/état STP de chaque chemin et rechercher des changements de topologie au même moment ;
- consulter les compteurs d'erreur et l'historique des transitions de lien ;
- rechercher une adresse dupliquée ou un hôte multi-attache avant d'accuser STP ;
- conserver la preuve qui permet de choisir entre les hypothèses.

Ne coupe pas simultanément plusieurs liens redondants pour « voir ce qui se passe ». Sur une topologie mal connue, cela peut isoler une zone ou déplacer le problème sans révéler la cause.

### 6.4. Les BPDU dans Wireshark

Sur un port SPAN/TAP configuré conformément aux capacités du commutateur, une capture peut aider à examiner les BPDU. Vérifie le type de capture, l'encapsulation Ethernet, l'interface observée et la présence effective du trafic de contrôle. Le comportement de mirroring dépend du modèle ; une capture qui ne montre pas de BPDU ne prouve pas à elle seule qu'aucune BPDU ne circule sur le lien.

Dans l'analyse, observe notamment :

- Bridge ID racine annoncé ;
- Bridge ID du pont émetteur ;
- Root Path Cost ;
- identifiant du port émetteur ;
- flags et informations pertinentes au protocole et à la version ;
- intervalle temporel entre les annonces et leur corrélation avec l'état de l'interface.

Compare une capture des deux côtés si possible. Une asymétrie peut aider à localiser une panne unidirectionnelle, une filtrage ou un problème de chemin, mais elle doit être corrélée aux sorties des commutateurs et à l'état physique.

### 6.5. Arbre de décision de dépannage

<div class="lesson-figure">
<svg viewBox="0 0 860 410" role="img" aria-label="Arbre de décision de diagnostic STP basé sur la racine, les protections, les trunks et les événements physiques" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <rect x="8" y="8" width="844" height="394" rx="18" fill="#0b1220" stroke="#334155"/>
  <rect x="300" y="28" width="260" height="50" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="430" y="49" fill="#dbeafe" text-anchor="middle" font-weight="700" font-size="13">Incident STP / MACFLAP</text><text x="430" y="65" fill="#93c5fd" text-anchor="middle" font-size="11">capturer l'état avant changement</text>
  <path d="M430 78 V112 H210 V136 M430 112 H650 V136" fill="none" stroke="#94a3b8" stroke-width="2"/>
  <rect x="70" y="136" width="280" height="60" rx="10" fill="#123047" stroke="#38bdf8"/><text x="210" y="159" fill="#e0f2fe" text-anchor="middle" font-weight="700" font-size="12">Racine / rôles inattendus ?</text><text x="210" y="178" fill="#7dd3fc" text-anchor="middle" font-size="11">Root ID, coût, mode, région MST</text>
  <rect x="510" y="136" width="280" height="60" rx="10" fill="#3f1d20" stroke="#fb7185"/><text x="650" y="159" fill="#ffe4e6" text-anchor="middle" font-weight="700" font-size="12">Port inconsistent ou BPDU absente ?</text><text x="650" y="178" fill="#fda4af" text-anchor="middle" font-size="11">Root/Loop/BPDU Guard, UDLD</text>
  <path d="M210 196 V220 H210 V238 M650 196 V220 H650 V238" stroke="#94a3b8" stroke-width="2" fill="none"/>
  <rect x="70" y="238" width="280" height="58" rx="10" fill="#0f3b48" stroke="#22d3ee"/><text x="210" y="261" fill="#cffafe" text-anchor="middle" font-weight="700" font-size="12">Comparer la topologie</text><text x="210" y="279" fill="#67e8f9" text-anchor="middle" font-size="11">priorités, coûts, voisins, MST digest</text>
  <rect x="510" y="238" width="280" height="58" rx="10" fill="#422006" stroke="#f59e0b"/><text x="650" y="261" fill="#fde68a" text-anchor="middle" font-weight="700" font-size="12">Comparer le lien physique</text><text x="650" y="279" fill="#fcd34d" text-anchor="middle" font-size="11">trunk, EtherChannel, erreurs, capture</text>
  <path d="M210 296 V320 H430 V337 M650 296 V320 H430" fill="none" stroke="#94a3b8" stroke-width="2"/>
  <rect x="280" y="337" width="300" height="44" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="430" y="355" fill="#dcfce7" text-anchor="middle" font-size="12" font-weight="700">Correction minimale et réversible</text><text x="430" y="371" fill="#bbf7d0" text-anchor="middle" font-size="10">re-vérifier STP + MAC + connectivité</text>
</svg>
</div>

L'arbre est volontairement court : une intervention peut avoir plusieurs causes simultanées. Il sert à organiser la collecte de preuves et non à remplacer la lecture de la topologie ni les journaux horodatés.


## 7. Laboratoires avancés

### Laboratoire 1 — Racine et racine secondaire pour deux VLAN

**Objectif :** rendre le chemin actif déterministe et démontrer comment une stratégie de racine peut influencer l'utilisation des liens.

**Topologie :** trois commutateurs (DIST-A, DIST-B, ACC-1) avec deux chemins redondants entre distribution et accès. Prévois VLAN 10 et VLAN 20, avec des liens trunk sur les chemins nécessaires.

**Étapes :**

1. Vérifie la configuration initiale avec `show spanning-tree vlan 10` et `show spanning-tree vlan 20`.
2. Note le Root ID, le coût, le rôle et l'état de chaque port concerné.
3. Définis DIST-A comme racine préférée pour VLAN 10 et DIST-B comme racine préférée pour VLAN 20, sur les plateformes qui prennent en charge l'approche par VLAN.
4. Configure des racines secondaires avec des priorités documentées et non concurrentes.
5. Vérifie les rôles/états et que le chemin obtenu correspond à la conception.
6. Simule la perte d'un lien en laboratoire et observe la bascule.
7. Restaure le lien et vérifie que la topologie revient à l'état attendu.

**Critères de réussite :** les racines correspondent au plan, les chemins de secours sont disponibles, aucun VLAN critique n'est perdu et le changement est expliqué à partir des sorties avant/après.

### Laboratoire 2 — Différencier Root Guard et Loop Guard

**Objectif :** apprendre à choisir la protection selon l'événement.

**Scénario A :** un commutateur aval envoie une BPDU supérieure sur un port où il ne doit pas devenir racine. Dans une topologie de laboratoire autorisée, applique Root Guard sur le port conçu pour ne pas accepter une racine supérieure. Observe l'état inconsistent et vérifie ce qui se passe lorsque la condition disparaît.

**Scénario B :** simule de façon contrôlée une situation où un port n'obtient plus les BPDUs attendues, uniquement si ton simulateur ou ton matériel de laboratoire le permet. Observe les mécanismes Loop Guard. Ne provoque pas de panne de BPDU sur un réseau partagé ou de production.

**Compte rendu :** pour chaque scénario, précise l'événement observé, l'état du port, la protection adaptée, les commandes de vérification et le comportement attendu après correction.

### Laboratoire 3 — Construire et vérifier une région MST

**Objectif :** configurer une région à deux instances et détecter une incohérence de région.

1. Utilise trois commutateurs compatibles MST.
2. Définis le même nom, la même révision et le même mappage VLAN-instance sur les membres voulus.
3. Place les VLAN 10/20/30 dans l'instance 1 et VLAN 40/50 dans l'instance 2.
4. Vérifie `show spanning-tree mst configuration`, `show spanning-tree mst` et le digest disponible.
5. Sur un commutateur isolé de la maquette, modifie temporairement le mappage pour créer une divergence contrôlée.
6. Observe les indices de frontière et compare les sorties de chaque côté.
7. Rétablis exactement la configuration de région et vérifie les chemins des deux instances.

Ne modifie pas le mappage MST sur une production sans plan de migration. Une différence de configuration peut avoir des effets plus larges que le VLAN qui semble être le sujet du changement.

### Laboratoire 4 — Enquête sur des MAC flaps

**Objectif :** pratiquer une enquête sans supposer que chaque MAC flap signifie automatiquement une faute STP.

**Données du scénario :**

```text
%SW_MATM-4-MACFLAP_NOTIF: Host 00aa.11bb.22cc in vlan 20 is flapping between port Gi1/0/10 and port Gi1/0/48
%SPANTREE-2-TOPO_CHANGE: topology change detected on vlan 20
%LINK-3-UPDOWN: Interface Gi1/0/48, changed state to down
```

Ces lignes sont pédagogiques et ne représentent pas une capture issue d'un équipement réel. Elles présentent au moins trois axes à vérifier : emplacement de la MAC, changement STP et état physique de l'interface.

Travail à réaliser :

1. énumérer les hypothèses possibles et leur donner un ordre de priorité ;
2. déterminer les commandes nécessaires pour distinguer boucle, lien instable, mauvais EtherChannel ou MAC dupliquée ;
3. préciser quelle donnée manque pour chaque hypothèse ;
4. proposer un test minimal et réversible ;
5. écrire la preuve qui confirmerait la correction.

### Laboratoire 5 — Plan de retour arrière d'une modification MST

Rédige une fiche de changement comprenant :

- l'objectif et les VLAN/instances concernés ;
- l'état initial de chaque membre de la région et les sorties sauvegardées ;
- le nom, la révision et le mappage prévus ;
- l'ordre des équipements et les étapes de validation ;
- les critères d'arrêt ;
- les commandes ou modifications de retour arrière adaptées à l'équipement, testées en laboratoire ;
- les tests applicatifs (passerelle, services internes, gestion des équipements) ;
- les personnes à prévenir et la durée d'observation après le changement.

Le retour arrière n'est pas simplement « remettre l'ancienne commande ». Il doit restaurer une topologie cohérente et prouver que les services sont revenus à leur état accepté.


## 8. Cas d'incident : appliquer une analyse hypothèse-preuve

### Cas A — La racine a changé au cours de la nuit

**Symptôme :** la latence des utilisateurs augmente et `show spanning-tree root` indique un autre Root ID que celui du dossier d'architecture.

**Hypothèses :** un commutateur ajouté possède une priorité plus basse ; les priorités de la racine historique ont été modifiées ; une migration ou un remplacement a changé le Bridge ID ; une instance ou un VLAN est différent de ceux attendus.

**Preuves à obtenir :** sortie complète de l'instance concernée, priorité effective et Bridge ID, logs de changement, inventaire des équipements raccordés récemment, différences entre VLAN et mode STP.

**Correction :** après identification, rétablis les priorités selon le plan, vérifie la présence d'une racine secondaire et valide le chemin attendu. Ne modifie pas les priorités de tous les commutateurs à la fois.

### Cas B — Un port est root-inconsistent

**Symptôme :** le port ne transfère plus et les journaux montrent une condition Root Guard.

**Hypothèses :** un équipement en aval a envoyé une BPDU supérieure ; la racine du réseau a changé ; Root Guard est posé sur une interface qui devrait légitimement servir de chemin vers la racine ; un changement d'architecture n'a pas été documenté.

**Preuves à obtenir :** rôle/état du port, voisin, Root ID annoncé, emplacement de la protection, changement récent de câblage/configuration.

**Correction :** détermine d'abord si l'annonce est légitime. Corrige la conception, la priorité de la racine ou le placement de la protection selon le besoin réel. Ne retire pas Root Guard juste pour rendre le port actif.

### Cas C — Plusieurs VLAN sont touchés après un changement MST

**Symptôme :** seuls certains chemins ont changé, mais les utilisateurs voient une charge inhabituelle sur un trunk.

**Hypothèses :** un mappage VLAN-instance n'est pas identique ; un commutateur est passé en frontière de région ; l'instance concernée a une racine différente de celle prévue ; une liste de VLAN autorisés sur le trunk a changé en même temps que la région.

**Preuves à obtenir :** configuration MST et digest, sorties STP par instance, état des trunks, changements appliqués, comparaison aux autres membres de la région.

**Correction :** restaure une configuration cohérente de région et valide les racines/chemins et VLAN avant d'effectuer tout changement supplémentaire sur les trunks.

### Cas D — Convergence lente malgré Rapid-PVST+

**Symptôme :** le réseau utilise Rapid-PVST+ mais certains événements entraînent encore une interruption perceptible.

**Hypothèses :** lien qui monte/descend, segment non point-à-point, incompatibilité ou interaction de modes STP, agrégat incohérent, port mal classé, CPU ou équipement voisin instable, événement de topologie répété.

**Preuves à obtenir :** journaux horodatés, sortie STP détaillée, état et erreurs des interfaces, `show etherchannel summary`, captures BPDU si disponibles, chronologie du test applicatif.

**Correction :** corrige la cause démontrée et refais le même test dans les mêmes conditions. Le terme Rapid ne garantit pas un délai constant indépendant de la topologie et de l'implémentation.


## 9. Runbook opérationnel STP

### 9.1. Avant l'intervention

- Confirmer le périmètre exact : commutateurs, VLAN, instances, trunks et services.
- Enregistrer `show spanning-tree`, les sorties de racine, le mode STP, les ports inconsistent et les états physiques.
- Sauvegarder les configurations et vérifier qu'un accès de secours est disponible.
- Définir la racine et les rôles/états attendus après changement.
- Définir le seuil qui fait arrêter l'intervention et le plan de retour arrière.

### 9.2. Pendant l'intervention

- Annoncer le début du changement et horodater les étapes.
- Appliquer la plus petite modification compatible avec l'objectif.
- Attendre que l'état de contrôle soit stable selon le critère défini ; ne pas se limiter à l'absence d'un message d'erreur.
- Vérifier les racines, les rôles/états, les trunks et les chemins de gestion.
- Ne pas cumuler un changement STP, un changement de VLAN et un changement EtherChannel si la séparation permet d'isoler les causes.

### 9.3. Après l'intervention

- Comparer la topologie observée à la topologie attendue.
- Vérifier les VLAN les plus critiques et les chemins applicatifs représentatifs.
- Examiner les nouveaux TCN, les MAC flaps et les transitions de lien.
- Conserver les sorties post-changement et les résultats de tests.
- Mettre à jour le schéma d'architecture et les procédures d'exploitation.


## 10. Évaluation — questions de niveau expert

Réponds avant de consulter le corrigé. Les situations sont génériques ; les détails d'implémentation doivent être vérifiés sur l'équipement du laboratoire.

### Questions

**1.** Deux commutateurs Rapid-PVST+ annoncent des coûts de chemin égaux vers la racine. Quelles informations supplémentaires faut-il examiner pour expliquer le choix final du port ?

**2.** Un port reçoit une BPDU supérieure alors qu'il est protégé par Root Guard et passe en `root-inconsistent`. Quelle est la première question d'architecture à résoudre avant de supprimer la protection ?

**3.** Quelle différence de problème Loop Guard et UDLD cherchent-ils à traiter ? Pourquoi peuvent-ils être complémentaires ?

**4.** Deux commutateurs MST ont le même nom de région et la même révision, mais l'un mappe VLAN 30 vers MSTI 1 et l'autre vers MSTI 2. Peuvent-ils être considérés comme membres de la même région configurée ? Justifie.

**5.** Pourquoi un état `forwarding` sur tous les ports d'une capture partielle ne prouve-t-il pas que la topologie globale est sûre ?

**6.** Une MAC flappe entre un port utilisateur et un trunk. Donne au moins quatre vérifications avant de conclure à une boucle STP.

**7.** Quel est le risque d'utiliser BPDU Filter sur un lien inter-commutateurs pour réduire les logs de changement de topologie ?

**8.** Pourquoi la présence du même Root ID ne garantit-elle pas que deux VLAN utilisent le même chemin physique ?

**9.** Quelles informations doivent être sauvegardées avant de modifier le mapping MST ?

**10.** Un réseau utilise Rapid-PVST+, mais la panne d'un lien entraîne une interruption plus longue que prévu. Cite des preuves permettant de distinguer un problème de convergence STP d'un lien physique instable.

**11.** Pourquoi faut-il considérer les BPDUs capturées dans leur contexte de port, de mode STP et de topologie, plutôt que comme une preuve isolée ?

**12.** Quels critères objectifs déterminent le retour arrière lors d'une migration STP ?

### Corrigé

**1.** Examiner le Root ID annoncé, le coût total, le Sender Bridge ID, le Sender Port ID et les identifiants de port pertinents selon l'algorithme et l'implémentation. Les sorties STP et les voisins sont plus fiables qu'une déduction fondée uniquement sur le débit du lien.

**2.** Déterminer si le voisin a légitimement le droit de devenir racine ou si l'annonce révèle un changement non autorisé. Il faut confirmer le design de racine et le rôle voulu pour le port avant de modifier Root Guard.

**3.** Loop Guard protège certains ports STP lorsque les BPDUs attendues cessent d'arriver, afin d'éviter une transition dangereuse. UDLD détecte certains défauts de lien unidirectionnel sur les interfaces prises en charge. L'un agit dans la logique STP, l'autre surveille la relation physique/logique du lien ; leurs mécanismes et limites diffèrent.

**4.** Non. Le mappage des VLAN vers les instances fait partie de la configuration de région. Une divergence de mappage peut produire une frontière de région même si le nom et la révision sont identiques.

**5.** La capture peut être incomplète ou concerner une seule instance. Certains ports de transfert peuvent exister en parallèle d'une boucle externe, d'une mauvaise frontière de région, d'un trunk non prévu ou d'un segment non observé. Il faut examiner la topologie entière et les instances affectées.

**6.** Vérifier `show spanning-tree` pour les VLAN concernés, les trunks et leur liste autorisée, l'état d'un EtherChannel, les journaux de link flap, la table MAC et les éventuelles adresses dupliquées. Inspecter également le câblage et les voisins.

**7.** Le filtrage peut empêcher l'échange ou le traitement des BPDUs et réduire la capacité du protocole à prévenir les boucles. Ce n'est pas un remède sûr aux logs ; une boucle peut provoquer une tempête de diffusion et une panne étendue.

**8.** Les modes par VLAN ou par instance peuvent calculer des coûts, des priorités et des rôles distincts. La même racine peut servir plusieurs arbres dont les ports de transfert diffèrent.

**9.** Le nom de région, la révision, le mapping VLAN-instance, la configuration actuelle, les priorités/root, les sorties STP détaillées, les états des trunks et des ports, les routes de gestion et les critères de retour arrière.

**10.** Corréler les journaux horodatés et l'état des liens avec la sortie STP détaillée, les rôles/états avant et après la panne, les erreurs d'interface, les changements EtherChannel et si possible les BPDUs capturées. Une interface qui flappe sans arrêt indique un problème physique ou de voisinage qui ne se résout pas par une priorité STP.

**11.** La capture dépend du point d'observation, des capacités SPAN/TAP, du protocole réellement actif et des messages transmis par le voisin. Une trame isolée doit être mise en corrélation avec les états locaux et distants, les horodatages et les changements de topologie.

**12.** Un état critique qui dépasse le seuil convenu, une racine inattendue, un port inconsistent non prévu, la perte d'accès de gestion, une baisse de connectivité ou un mapping MST non cohérent. Les critères doivent être écrits avant le changement et le retour doit être testé en maquette.


## 11. Points à retenir

- La qualité d'une conception STP se mesure à la prédictibilité du Root Bridge, des chemins actifs, des chemins de secours et du domaine d'impact d'une panne.
- RSTP utilise des mécanismes de synchronisation et d'échange de rôles ; le résultat dépend des liens, de la compatibilité et de la topologie.
- Root Guard, Loop Guard, BPDU Guard, BPDU Filter, UDLD et Storm Control répondent à des problèmes différents. Un placement incorrect peut interrompre un chemin utile ou supprimer une protection attendue.
- Dans MST, nom, révision et mappage VLAN-instance doivent rester cohérents pour les membres d'une même région.
- Les MAC flaps et TCN sont des indices à corréler, pas des diagnostics complets.
- Une capture BPDU aide à comprendre les annonces, mais doit être associée aux sorties STP et à l'observation des deux côtés du lien.
- Tout changement devrait avoir un état initial, des critères d'arrêt, un plan de retour arrière et une validation après convergence.

## 12. Références techniques

Sélectionne toujours la documentation correspondant au modèle et à la version de logiciel réellement utilisés.

- Cisco, **STP Configuration Guide — Cisco IOS XE 17 / Catalyst 9000** : <https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/stp/stp-configuration-guide/m-stp.html>
- Cisco, **Troubleshoot MAC Flaps/Loop on Cisco Catalyst Switches** : <https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol-stp-8021d/221722-troubleshoot-mac-flaps-loop-on-cisco-cat.html>
- Cisco, **Understand STP Loop Guard and UDLD** : <https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol-stp-8021d/218321-configure-stp-with-loop-guard-and-bpdu-s.html>
- Cisco, **Understand Spanning Tree PortFast and BPDU Guard Features** : <https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10586-65.html>
- Cisco, **Root Guard** : <https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10588-74.html>
- IEEE, **IEEE 802.1Q — Bridges and Bridged Networks** : <https://standards.ieee.org/ieee/802.1q/10323/>

Ces références servent à confirmer les mécanismes et les possibilités de configuration. Les schémas sont conceptuels ; les commandes, les valeurs de coût et les transitions doivent être vérifiées sur la plateforme de laboratoire ou de production concernée.
