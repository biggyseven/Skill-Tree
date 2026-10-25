# Spanning Tree Protocol (STP) — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Durée indicative :** 2 à 3 heures  
**Prérequis :** maîtriser les notions de base de STP : boucle de couche 2, BPDU, Bridge ID, Root Bridge, Root Port, Designated Port, Alternate Port, PortFast et BPDU Guard.

Ce cours prolonge `stp-debutant.md`. Il ne reprend pas longuement l’élection de base du pont racine ; il approfondit les critères de sélection, RSTP, les protections de topologie, le fonctionnement par VLAN et par instance, ainsi que la démarche de dépannage. Les commandes illustrées sont de style Cisco IOS/IOS XE et doivent être adaptées à la plateforme réellement utilisée.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :

- déterminer quel port gagne lorsque plusieurs chemins vers la racine ont des coûts proches ou identiques ;
- expliquer les transitions rapides de RSTP et les conditions qui les rendent possibles ;
- distinguer Root Guard, Loop Guard, BPDU Guard et UDLD selon la panne visée ;
- concevoir une répartition maîtrisée des racines STP entre plusieurs VLAN ;
- reconnaître les risques de configuration dans un environnement PVST+/Rapid-PVST+/MST ;
- diagnostiquer un changement de topologie, un MAC flapping ou un port inconsistent à partir de commandes de vérification ;
- appliquer un changement STP dans un laboratoire avec contrôle avant/après et possibilité de retour arrière.

> **Important :** une commande, une valeur par défaut ou une fonctionnalité peut varier selon le modèle, la version logicielle et le mode STP. Ne copie pas directement une configuration de laboratoire en production. Capture l’état initial, vérifie la documentation de ton équipement et modifie une seule variable à la fois.


## 1. Revoir les critères de décision STP

### 1.1. L’élection ne se limite pas à « la priorité la plus basse »

Le Root Bridge est le commutateur dont le Bridge ID (BID) est le plus faible dans l’instance STP considérée. Le BID combine une priorité effective et une adresse MAC ; sur de nombreuses plateformes modernes, la priorité effective comprend aussi l’Extended System ID, notamment le VLAN dans les modes STP par VLAN.

Pour choisir son Root Port, un commutateur compare les informations de chemin vers la racine. Les critères de départage classiques sont examinés dans l’ordre :

1. **Root Bridge ID** le plus faible annoncé ;
2. **Root Path Cost** total le plus faible ;
3. **Sender Bridge ID** le plus faible si les chemins restent à égalité ;
4. **Sender Port ID** le plus faible ;
5. si nécessaire, l’identifiant du port local pour départager des informations restantes selon l’algorithme et l’implémentation.

En pratique, ne retiens pas seulement la liste : utilise `show spanning-tree` pour lire le Root ID, le coût de chaque chemin et le rôle effectif du port.

### 1.2. Coût de chemin et vitesse des liens

Le coût STP permet de préférer un chemin. Il est associé au débit de la liaison et à la méthode de coût utilisée. Les valeurs exactes ont évolué entre la méthode courte (*short*) et la méthode longue (*long*) ; les tableaux de coût par défaut diffèrent aussi entre générations de matériel.

```text
                       Root Bridge
                           SW1
                         /     \
                coût 4  /       \  coût 19
                       /         \
                     SW2 -------- SW3
                       coût 4

SW4 voit deux chemins possibles :
  chemin A : SW4 -> SW2 -> SW1 = coût total 8
  chemin B : SW4 -> SW3 -> SW1 = coût total 23

STP préfère le chemin A, car son coût total est inférieur.
```

Le dessin est conceptuel : les coûts affichés ne représentent pas une valeur universelle pour une vitesse donnée. Calcule le coût à partir de la sortie de ton commutateur et de sa méthode configurée.

### 1.3. Schéma — départager deux chemins

<div class="lesson-figure">
<svg width="840" height="360" viewBox="0 0 840 360" role="img" aria-label="Deux chemins vers le pont racine et comparaison de leurs coûts STP" xmlns="http://www.w3.org/2000/svg" style="font-family:Arial,sans-serif">
  <defs>
    <marker id="stpi-cost-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#67e8f9"/></marker>
    <style>
      @keyframes stpiCostPulse { 0%,100%{opacity:.3} 50%{opacity:1} }
      .stpi-cost-flow { stroke-dasharray:8 8; animation:stpiCostPulse 1.8s ease-in-out infinite; }
    </style>
  </defs>
  <rect width="840" height="360" rx="18" fill="#0b1220"/>
  <text x="420" y="32" fill="#e5e7eb" font-size="20" text-anchor="middle" font-weight="700">Choisir le meilleur chemin vers la racine</text>
  <rect x="330" y="56" width="180" height="58" rx="13" fill="#12352f" stroke="#34d399" stroke-width="2"/>
  <text x="420" y="80" fill="#a7f3d0" font-size="14" text-anchor="middle" font-weight="700">SW1 · ROOT</text>
  <text x="420" y="99" fill="#d1fae5" font-size="11" text-anchor="middle">Root ID le plus faible</text>
  <path d="M365 114 L245 190 L245 235" fill="none" stroke="#67e8f9" stroke-width="3" marker-end="url(#stpi-cost-arrow)"/>
  <path d="M475 114 L595 190 L595 235" fill="none" stroke="#fbbf24" stroke-width="3"/>
  <path d="M245 235 L365 114" fill="none" stroke="#67e8f9" stroke-width="7" opacity=".2"/>
  <path d="M595 235 L475 114" fill="none" stroke="#fbbf24" stroke-width="7" opacity=".2"/>
  <path class="stpi-cost-flow" d="M365 114 L245 190 L245 235" fill="none" stroke="#67e8f9" stroke-width="4" marker-end="url(#stpi-cost-arrow)"/>
  <path d="M245 273 L595 273" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="5 6"/>
  <rect x="155" y="235" width="180" height="62" rx="13" fill="#172554" stroke="#67e8f9" stroke-width="2"/>
  <text x="245" y="260" fill="#bae6fd" font-size="14" text-anchor="middle" font-weight="700">Chemin A</text>
  <text x="245" y="281" fill="#e0f2fe" font-size="12" text-anchor="middle">coût total = 8</text>
  <rect x="505" y="235" width="180" height="62" rx="13" fill="#422006" stroke="#fbbf24" stroke-width="2"/>
  <text x="595" y="260" fill="#fde68a" font-size="14" text-anchor="middle" font-weight="700">Chemin B</text>
  <text x="595" y="281" fill="#fef3c7" font-size="12" text-anchor="middle">coût total = 23</text>
  <text x="420" y="326" fill="#a7f3d0" font-size="14" text-anchor="middle" font-weight="700">Le coût le plus faible gagne avant les critères de départage suivants.</text>
</svg>
</div>

### 1.4. Exemple de départage avec des coûts égaux

Deux liaisons peuvent proposer le même Root ID et le même coût total. STP doit alors utiliser d’autres champs d’identification pour obtenir un résultat déterministe. Un administrateur peut influencer certains départages en ajustant le coût de port ou la priorité de port, mais ces réglages doivent être documentés : ils sont plus difficiles à maintenir qu’une conception claire des racines et des liaisons.

Pour analyser le résultat, relève :

```cisco
show spanning-tree vlan 10
show spanning-tree interface GigabitEthernet1/0/1 detail
show spanning-tree interface GigabitEthernet1/0/2 detail
```

Sur de nombreuses plateformes, les détails disponibles changent avec le modèle et le mode STP. Cherche dans la sortie le Root ID, le coût du chemin, le port ID local et les informations du pont/port voisin.


## 2. Rapid Spanning Tree Protocol (RSTP) en pratique

### 2.1. Ce que RSTP cherche à améliorer

STP classique s’appuie fortement sur ses temporisateurs lorsqu’il doit activer un chemin après un changement. RSTP (IEEE 802.1w, repris dans les évolutions d’IEEE 802.1Q) ajoute des rôles et mécanismes de transition qui permettent généralement une convergence plus rapide : échanges de BPDU plus actifs, proposition/accord (*proposal/agreement*) sur les liens point-à-point et rôle Alternate prêt à servir de chemin de secours.

RSTP ne garantit pas une convergence instantanée dans toute topologie. Les liens partagés, les frontières avec des équipements anciens, les incohérences duplex, une configuration mélangée ou un mauvais câblage peuvent empêcher une transition rapide attendue.

| Élément | STP classique | RSTP |
|---|---|---|
| États utilisés | Blocking, Listening, Learning, Forwarding, Disabled (terminologie selon contexte) | Discarding, Learning, Forwarding |
| Port alternatif | généralement décrit comme port bloqué | rôle Alternate explicite, prêt à reprendre le chemin |
| Transition rapide | surtout dépendante des temporisateurs et du type de port | mécanismes proposal/agreement sur des liens compatibles |
| BPDU | générées par la racine puis relayées par les ponts | chaque commutateur compatible génère des BPDU périodiques |
| Ports terminaux | PortFast est une extension fréquente | ports edge, souvent configurés avec PortFast côté Cisco |

### 2.2. Rôle et état : deux notions différentes

Le rôle décrit la fonction du port dans la topologie ; l’état décrit son action de transfert à l’instant observé.

| Rôle | Signification courante | État fréquent en RSTP stable |
|---|---|---|
| Root | meilleur chemin du commutateur non-racine vers la racine | Forwarding |
| Designated | meilleur port désigné pour le segment | Forwarding |
| Alternate | chemin de secours vers la racine via un autre pont | Discarding |
| Backup | chemin de secours vers un même segment partagé, rare en Ethernet moderne | Discarding |
| Edge | port destiné à un terminal et non à un autre pont | Forwarding, sauf si protection déclenchée |

Un Alternate n’est pas un port défectueux : il contribue à la redondance. Son état Discarding est précisément ce qui empêche une boucle. Si le chemin actif tombe en panne, RSTP peut faire évoluer l’Alternate vers un rôle de transfert selon les conditions détectées.

### 2.3. Schéma — transition RSTP sur un lien point-à-point

<div class="lesson-figure">
<svg width="840" height="340" viewBox="0 0 840 340" role="img" aria-label="Séquence simplifiée de proposal et agreement RSTP entre deux commutateurs" xmlns="http://www.w3.org/2000/svg" style="font-family:Arial,sans-serif">
  <defs><marker id="stpi-rstp-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#67e8f9"/></marker>
  <style>@keyframes stpiLinkGlow{0%,100%{opacity:.35}50%{opacity:1}} .stpi-rstp-active{stroke-dasharray:9 8;animation:stpiLinkGlow 1.6s linear infinite}</style></defs>
  <rect width="840" height="340" rx="18" fill="#0b1220"/>
  <text x="420" y="30" fill="#e5e7eb" font-size="20" text-anchor="middle" font-weight="700">RSTP : échange simplifié sur un lien point-à-point</text>
  <rect x="50" y="63" width="190" height="65" rx="13" fill="#12352f" stroke="#34d399" stroke-width="2"/>
  <text x="145" y="89" fill="#a7f3d0" font-size="15" font-weight="700" text-anchor="middle">SW1</text><text x="145" y="108" fill="#d1fae5" font-size="12" text-anchor="middle">Root / Designated</text>
  <rect x="600" y="63" width="190" height="65" rx="13" fill="#172554" stroke="#60a5fa" stroke-width="2"/>
  <text x="695" y="89" fill="#bfdbfe" font-size="15" font-weight="700" text-anchor="middle">SW2</text><text x="695" y="108" fill="#dbeafe" font-size="12" text-anchor="middle">prochain saut vers racine</text>
  <path d="M240 85 L600 85" stroke="#475569" stroke-width="5" stroke-linecap="round"/>
  <path class="stpi-rstp-active" d="M240 85 L600 85" stroke="#67e8f9" stroke-width="3" marker-end="url(#stpi-rstp-arrow)"/>
  <rect x="285" y="61" width="270" height="45" rx="9" fill="#082f49" stroke="#0891b2"/>
  <text x="420" y="79" fill="#a5f3fc" font-size="12" font-weight="700" text-anchor="middle">1 · Proposal</text><text x="420" y="94" fill="#cffafe" font-size="10" text-anchor="middle">SW1 propose les informations de topologie</text>
  <path d="M600 145 L240 145" stroke="#fbbf24" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#stpi-rstp-arrow)"/>
  <rect x="295" y="123" width="250" height="45" rx="9" fill="#422006" stroke="#f59e0b"/>
  <text x="420" y="141" fill="#fde68a" font-size="12" font-weight="700" text-anchor="middle">2 · Agreement</text><text x="420" y="156" fill="#fef3c7" font-size="10" text-anchor="middle">SW2 confirme la réception selon les règles RSTP</text>
  <path d="M695 128 L695 205 L145 205 L145 128" fill="none" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 5"/>
  <rect x="55" y="226" width="730" height="74" rx="12" fill="#111827" stroke="#334155"/>
  <text x="420" y="249" fill="#e5e7eb" font-size="13" font-weight="700" text-anchor="middle">3 · Transition contrôlée</text>
  <text x="420" y="270" fill="#cbd5e1" font-size="12" text-anchor="middle">Sur un lien point-à-point compatible, le port peut passer rapidement en Forwarding</text>
  <text x="420" y="286" fill="#94a3b8" font-size="11" text-anchor="middle">Schéma conceptuel : l’ordre réel dépend de la topologie et des conditions d’élection.</text>
</svg>
</div>

Le dessin montre le principe logique, pas une capture paquet-par-paquet exhaustive. Ne suppose pas qu’un unique couple de messages suffit à résoudre tout changement de topologie : RSTP comporte des règles de synchronisation des ports, de propagation des informations et de traitement des chemins alternatifs.

### 2.4. Vérifier le mode réellement actif

Ne confonds pas la commande de configuration avec l’état effectif. Vérifie le résumé puis l’instance concernée :

```cisco
show spanning-tree summary
show spanning-tree vlan 10
show spanning-tree root
show spanning-tree detail
```

Si un switch voisin fonctionne en STP classique, la transition peut être influencée par l’interopérabilité. Cherche les indications de mode, les rôles, les changements de topologie et les éventuelles incohérences sur les ports.


## 3. Conception : choisir la racine et contrôler les chemins

### 3.1. Pourquoi laisser la racine au hasard est risqué

Avec les valeurs par défaut, la racine est déterminée en fonction du Bridge ID, donc généralement par la plus faible priorité effective puis l’adresse MAC. Ce résultat peut être fonctionnel mais sous-optimal : le trafic peut traverser un commutateur d’accès ou un chemin qui n’est pas le mieux placé.

Une conception déterministe définit :

- un Root Bridge primaire, généralement dans la couche distribution/cœur prévue pour le rôle ;
- un Root Bridge secondaire, capable de prendre le relais ;
- un plan explicite par VLAN ou par instance MST ;
- une procédure de vérification après remplacement, ajout de commutateur ou modification d’agrégat.

Le « primaire » et le « secondaire » sont des objectifs de conception. Les priorités doivent être choisies en tenant compte de l’Extended System ID et des priorités déjà configurées sur les équipements voisins.

### 3.2. Priorité STP et répartition de charge par VLAN

Dans PVST+/Rapid-PVST+, chaque VLAN possède une instance STP indépendante. Il est donc possible de définir SW1 comme racine de certains VLAN et SW2 comme racine d’autres VLAN, afin de mieux répartir les chemins actifs, si la topologie le justifie.

```cisco
! Exemple de laboratoire : SW1 racine préférée pour VLAN 10 et 30
spanning-tree vlan 10,30 root primary

! SW2 prend le rôle de racine de secours pour ces VLAN
spanning-tree vlan 10,30 root secondary
```

Attention : ne colle pas les deux blocs sur le même commutateur si le but est de désigner deux équipements distincts. Le premier exemple est à exécuter sur SW1 ; le second sur SW2. La macro `root primary` ajuste généralement la priorité par rapport aux racines observées ; vérifie la valeur effective dans `show spanning-tree vlan <id>`.

La répartition de racines n’équivaut pas automatiquement à une répartition équilibrée du trafic. Vérifie le routage, les chemins d’accès, la bande passante et les liens effectivement utilisés. Une modification de racine peut changer le chemin de nombreux VLAN et provoquer une convergence.

### 3.3. Schéma — racines différentes selon le VLAN

<div class="lesson-figure">
<svg width="840" height="350" viewBox="0 0 840 350" role="img" aria-label="Plan de répartition des racines STP entre deux commutateurs de distribution selon le VLAN" xmlns="http://www.w3.org/2000/svg" style="font-family:Arial,sans-serif">
 <defs><style>@keyframes stpi-vlan-path{0%,100%{opacity:.45}50%{opacity:1}} .stpi-vlan-link{animation:stpi-vlan-path 2s ease-in-out infinite;stroke-dasharray:7 7}</style></defs>
 <rect width="840" height="350" rx="18" fill="#0b1220"/><text x="420" y="31" text-anchor="middle" font-size="20" font-weight="700" fill="#e5e7eb">Plan de racine : instances par VLAN</text>
 <rect x="75" y="72" width="260" height="76" rx="14" fill="#12352f" stroke="#34d399" stroke-width="2"/><text x="205" y="98" text-anchor="middle" font-size="15" font-weight="700" fill="#a7f3d0">SW1 · Distribution A</text><text x="205" y="120" text-anchor="middle" font-size="13" fill="#d1fae5">Racine préférée : VLAN 10, 30</text>
 <rect x="505" y="72" width="260" height="76" rx="14" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="635" y="98" text-anchor="middle" font-size="15" font-weight="700" fill="#bfdbfe">SW2 · Distribution B</text><text x="635" y="120" text-anchor="middle" font-size="13" fill="#dbeafe">Racine préférée : VLAN 20, 40</text>
 <path d="M205 148 L205 194 L420 240" fill="none" stroke="#34d399" stroke-width="4"/><path d="M635 148 L635 194 L420 240" fill="none" stroke="#60a5fa" stroke-width="4"/>
 <path class="stpi-vlan-link" d="M205 148 L205 194 L420 240" fill="none" stroke="#a7f3d0" stroke-width="2"/><path class="stpi-vlan-link" d="M635 148 L635 194 L420 240" fill="none" stroke="#bfdbfe" stroke-width="2"/>
 <rect x="300" y="228" width="240" height="67" rx="13" fill="#1f2937" stroke="#64748b" stroke-width="2"/><text x="420" y="253" text-anchor="middle" font-size="15" font-weight="700" fill="#e5e7eb">Couche accès</text><text x="420" y="275" text-anchor="middle" font-size="12" fill="#cbd5e1">Liens redondants, rôles par instance</text>
 <text x="420" y="322" text-anchor="middle" font-size="12" fill="#fcd34d">Objectif : contrôler les chemins, puis mesurer la répartition réelle du trafic.</text>
</svg>
</div>

### 3.4. Configurer le coût ou la priorité de port

Une priorité ou un coût de port permet d’influencer un choix local, mais il ne faut pas corriger chaque résultat inattendu par une série de valeurs arbitraires. D’abord, confirme la racine voulue et l’ensemble de la topologie ; ensuite seulement, ajuste un paramètre de port si la conception l’exige.

```cisco
interface GigabitEthernet1/0/48
 spanning-tree vlan 10 cost 10
! Variante possible selon la plateforme : priorité de port par VLAN
 spanning-tree vlan 10 port-priority 64
```

Ces lignes sont un exemple conceptuel : les syntaxes et valeurs supportées dépendent de la version. Ne configure pas à la fois coût et priorité sans une raison documentée. Vérifie l’effet sur l’instance ciblée et sur les chemins redondants.


## 4. Protections STP : choisir le mécanisme adapté

Ces mécanismes ne sont pas interchangeables. La bonne protection dépend de la menace ou de la défaillance recherchée.

| Mécanisme | Risque principalement visé | Comportement attendu | Emplacement typique |
|---|---|---|---|
| **PortFast / edge** | délai de transition inutile pour un terminal | traite le port comme port de bordure, sous réserve de son comportement et de la plateforme | ports vers PC, imprimantes, terminaux |
| **BPDU Guard** | un pont non prévu est raccordé à un port edge | met le port en état de protection/err-disable selon la plateforme s’il reçoit une BPDU | ports d’accès aux terminaux avec PortFast |
| **Root Guard** | un équipement voisin tente d’imposer une racine supérieure sur un segment où cela n’est pas autorisé | place le port en état root-inconsistent si des BPDU supérieures sont reçues | ports où la racine ne doit pas être située en aval |
| **Loop Guard** | perte de BPDU sur un port non désigné qui pourrait passer à tort en forwarding | maintient une condition loop-inconsistent plutôt que d’activer le port | liens inter-commutateurs adaptés à la conception |
| **UDLD** | lien physique/fibre unidirectionnel | détecte certaines pannes unidirectionnelles et peut désactiver le lien selon le mode | supports et interfaces compatibles |

BPDU Guard détecte une BPDU inattendue ; Root Guard protège l’emplacement de la racine ; Loop Guard protège contre la perte de BPDUs sur des ports qui en attendent ; UDLD traite une autre dimension de défaillance de lien. Aucun n’est une solution universelle.

### 4.1. Schéma — où appliquer les protections

<div class="lesson-figure">
<svg width="840" height="390" viewBox="0 0 840 390" role="img" aria-label="Emplacements typiques de BPDU Guard, Root Guard et Loop Guard dans une topologie d'entreprise" xmlns="http://www.w3.org/2000/svg" style="font-family:Arial,sans-serif">
 <defs><style>@keyframes stpi-guard-pulse{0%,100%{opacity:.35}50%{opacity:1}} .stpi-guard-line{animation:stpi-guard-pulse 1.8s ease-in-out infinite;stroke-dasharray:7 7}</style></defs>
 <rect width="840" height="390" rx="18" fill="#0b1220"/><text x="420" y="30" text-anchor="middle" font-size="20" font-weight="700" fill="#e5e7eb">Une protection par scénario</text>
 <rect x="310" y="50" width="220" height="62" rx="12" fill="#12352f" stroke="#34d399" stroke-width="2"/><text x="420" y="75" text-anchor="middle" font-size="15" font-weight="700" fill="#a7f3d0">SW-DIST · Racine</text><text x="420" y="95" text-anchor="middle" font-size="11" fill="#d1fae5">Bridge ID attendu</text>
 <rect x="310" y="165" width="220" height="62" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="420" y="190" text-anchor="middle" font-size="15" font-weight="700" fill="#bfdbfe">SW-ACCESS</text><text x="420" y="210" text-anchor="middle" font-size="11" fill="#dbeafe">Trunks vers la distribution</text>
 <path d="M420 112 L420 165" stroke="#64748b" stroke-width="5"/><path class="stpi-guard-line" d="M420 112 L420 165" stroke="#67e8f9" stroke-width="3"/>
 <rect x="45" y="275" width="205" height="64" rx="12" fill="#422006" stroke="#fbbf24" stroke-width="2"/><text x="147" y="300" text-anchor="middle" font-size="14" font-weight="700" fill="#fde68a">Port de terminal</text><text x="147" y="320" text-anchor="middle" font-size="11" fill="#fef3c7">PortFast + BPDU Guard</text>
 <rect x="318" y="275" width="205" height="64" rx="12" fill="#312e81" stroke="#a5b4fc" stroke-width="2"/><text x="420" y="300" text-anchor="middle" font-size="14" font-weight="700" fill="#c7d2fe">Trunk en transit</text><text x="420" y="320" text-anchor="middle" font-size="11" fill="#e0e7ff">Loop Guard selon design</text>
 <rect x="595" y="275" width="205" height="64" rx="12" fill="#3f1d2e" stroke="#fb7185" stroke-width="2"/><text x="697" y="300" text-anchor="middle" font-size="14" font-weight="700" fill="#fecdd3">Frontière aval contrôlée</text><text x="697" y="320" text-anchor="middle" font-size="11" fill="#ffe4e6">Root Guard si racine interdite</text>
 <path d="M420 227 L420 250 L147 250 L147 275" fill="none" stroke="#fbbf24" stroke-width="2.5"/><path d="M420 227 L420 275" fill="none" stroke="#a5b4fc" stroke-width="2.5"/><path d="M420 250 L697 250 L697 275" fill="none" stroke="#fb7185" stroke-width="2.5"/>
 <text x="420" y="370" text-anchor="middle" font-size="12" fill="#cbd5e1">Le positionnement exact dépend du rôle prévu de chaque lien et de la topologie.</text>
</svg>
</div>

### 4.2. BPDU Guard sur les ports d’accès

Sur certains commutateurs Cisco, une configuration globale possible est :

```cisco
spanning-tree portfast default
spanning-tree portfast bpduguard default
```

Ces commandes ont une portée globale qui dépend du logiciel et de la façon dont les ports edge sont identifiés. Avant de les appliquer, vérifie les ports concernés. Sur un port individuel, on rencontre souvent :

```cisco
interface GigabitEthernet1/0/10
 switchport mode access
 spanning-tree portfast
 spanning-tree bpduguard enable
```

Ne l’applique pas mécaniquement sur les trunks ou les liens qui doivent recevoir des BPDU d’un autre commutateur. Une réception de BPDU peut placer le port en err-disabled selon la plateforme ; la récupération doit suivre la politique d’exploitation, pas une réactivation aveugle.

### 4.3. Root Guard : protéger le placement de la racine

Root Guard est utile lorsqu’un port ne doit pas recevoir d’informations indiquant qu’un pont situé plus loin doit devenir la racine. Si une BPDU supérieure apparaît, le port devient root-inconsistent et cesse de transférer selon le mécanisme.

```cisco
interface GigabitEthernet1/0/24
 spanning-tree guard root
```

Applique Root Guard là où la conception impose que la racine demeure de l’autre côté, par exemple une frontière vers une couche d’accès ou une zone administrée différemment. Ne l’active pas sur un lien qui doit naturellement conduire vers une racine de secours.

### 4.4. Loop Guard : protéger contre une absence inattendue de BPDU

Sur un port root ou alternate qui s’attend à recevoir des BPDU, une perte unidirectionnelle peut empêcher l’information STP de parvenir au commutateur. Sans protection appropriée, le port pourrait croire qu’il est désigné et passer en forwarding, créant une boucle. Loop Guard peut placer le port en état loop-inconsistent tant que les BPDU attendues ne sont pas reçues.

```cisco
interface GigabitEthernet1/0/48
 spanning-tree guard loop
```

Le comportement exact et les recommandations de portée doivent être confirmés pour la plateforme. Loop Guard ne remplace pas le diagnostic optique/physique ni UDLD ; il protège une partie de la décision STP.

### 4.5. Résoudre un état inconsistent sans supprimer la protection

Si une commande montre un port `root-inconsistent` ou `loop-inconsistent`, ne retire pas tout de suite la protection. Procède ainsi :

1. identifie le mécanisme et le VLAN/instance touché ;
2. relève les BPDUs et le rôle/état STP des deux côtés ;
3. confirme si le port reçoit des BPDUs supérieures ou a cessé d’en recevoir ;
4. contrôle l’état de la liaison, l’agrégat éventuel, les erreurs et la configuration du voisin ;
5. corrige la cause (mauvais chemin, voisin inapproprié, lien unidirectionnel ou erreur de rôle) ;
6. vérifie que le port récupère conformément à la fonction ;
7. confirme la connectivité et l’absence de nouvelle boucle.


## 5. STP par VLAN : PVST+, Rapid-PVST+ et MST

### 5.1. PVST+ et Rapid-PVST+

PVST+ maintient une instance STP par VLAN selon l’implémentation Cisco. Rapid-PVST+ conserve cette approche par VLAN mais utilise les mécanismes rapides de RSTP. Cela permet notamment de choisir des racines différentes selon les VLAN, mais le nombre d’instances et la charge de contrôle augmentent avec le nombre de VLAN.

Les termes et limites dépendent du modèle et de la version. Certaines plateformes prennent en charge un nombre maximal d’instances différent ; consulte le guide de configuration applicable plutôt que d’utiliser une valeur générique.

### 5.2. Pourquoi MST existe

MSTP (Multiple Spanning Tree Protocol) permet de mapper plusieurs VLAN à une même instance spanning tree, réduisant le nombre d’instances calculées et échangées par rapport à une instance par VLAN. Les commutateurs qui doivent partager une région MST doivent avoir une configuration cohérente : nom de région, révision de configuration et mappage VLAN-vers-instance. Une différence de ces paramètres peut créer une frontière MST au lieu d’une région commune.

Exemple pédagogique d’un plan :

| Instance MST | VLAN affectés | Objectif de conception |
|---|---|---|
| MST 0 / IST | informations de région et VLAN non mappés selon la plateforme | assurer la topologie interne commune |
| MST 1 | VLAN 10, 20, 30 | chemins préférés via Distribution A |
| MST 2 | VLAN 40, 50, 60 | chemins préférés via Distribution B |

Le plan de mappage doit être identique sur tous les commutateurs de la même région. Documente la liste VLAN de chaque instance et vérifie les sorties `show spanning-tree mst`.

### 5.3. Schéma — région MST et mappage des VLAN

<div class="lesson-figure">
<svg width="840" height="365" viewBox="0 0 840 365" role="img" aria-label="Schéma conceptuel d'une région MST regroupant plusieurs VLAN dans deux instances" xmlns="http://www.w3.org/2000/svg" style="font-family:Arial,sans-serif">
 <defs><style>@keyframes stpi-mst-pulse{0%,100%{opacity:.3}50%{opacity:1}} .stpi-mst-lane{animation:stpi-mst-pulse 2s ease-in-out infinite;stroke-dasharray:6 6}</style></defs>
 <rect width="840" height="365" rx="18" fill="#0b1220"/><text x="420" y="30" text-anchor="middle" font-size="20" font-weight="700" fill="#e5e7eb">MST : plusieurs VLAN, moins d’instances</text>
 <rect x="55" y="60" width="730" height="265" rx="18" fill="#111827" stroke="#64748b" stroke-width="2" stroke-dasharray="7 6"/><text x="420" y="83" text-anchor="middle" font-size="13" fill="#cbd5e1" font-weight="700">Région MST · même nom, révision et mappage</text>
 <rect x="90" y="108" width="280" height="75" rx="13" fill="#12352f" stroke="#34d399" stroke-width="2"/><text x="230" y="133" text-anchor="middle" font-size="15" fill="#a7f3d0" font-weight="700">Instance MST 1</text><text x="230" y="155" text-anchor="middle" font-size="13" fill="#d1fae5">VLAN 10 · 20 · 30</text><text x="230" y="172" text-anchor="middle" font-size="11" fill="#bbf7d0">chemin préféré : Distribution A</text>
 <rect x="470" y="108" width="280" height="75" rx="13" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="610" y="133" text-anchor="middle" font-size="15" fill="#bfdbfe" font-weight="700">Instance MST 2</text><text x="610" y="155" text-anchor="middle" font-size="13" fill="#dbeafe">VLAN 40 · 50 · 60</text><text x="610" y="172" text-anchor="middle" font-size="11" fill="#bfdbfe">chemin préféré : Distribution B</text>
 <path class="stpi-mst-lane" d="M230 183 L230 220 L420 252" fill="none" stroke="#34d399" stroke-width="3"/><path class="stpi-mst-lane" d="M610 183 L610 220 L420 252" fill="none" stroke="#60a5fa" stroke-width="3"/>
 <rect x="300" y="235" width="240" height="56" rx="12" fill="#292524" stroke="#a8a29e" stroke-width="2"/><text x="420" y="258" text-anchor="middle" font-size="14" fill="#e7e5e4" font-weight="700">Commutateurs de la région</text><text x="420" y="277" text-anchor="middle" font-size="11" fill="#d6d3d1">partagent la configuration MST</text>
 <text x="420" y="347" text-anchor="middle" font-size="12" fill="#fcd34d">Un mappage incohérent peut créer une frontière de région.</text>
</svg>
</div>

### 5.4. Contrôler une région MST

Commandes typiques sur les plateformes compatibles :

```cisco
show spanning-tree mst
show spanning-tree mst configuration
show spanning-tree mst 1
show spanning-tree summary
```

Compare les informations de région et le mappage VLAN-vers-instance sur plusieurs commutateurs. Une région qui semble identique dans son nom peut quand même différer par sa révision ou son mappage. En cas de frontière inattendue, capture les sorties avant de modifier la configuration.

### 5.5. Interopérabilité et frontière de protocole

Un réseau peut contenir des équipements en PVST+, Rapid-PVST+ et MSTP. L’interopérabilité est possible sous certaines conditions, mais il ne faut pas supposer que tous les rôles et toutes les instances sont identiques de part et d’autre d’une frontière. La topologie commune et la position de la racine doivent être conçues, puis vérifiées selon les règles d’interopérabilité du constructeur et du protocole.

En environnement multi-constructeur, le comportement exact dépend des implémentations et des normes prises en charge. Pour une conception de production, établis une matrice de compatibilité et réalise un test de convergence avant déploiement.


## 6. Changement de topologie, BPDUs et apprentissage MAC

### 6.1. Pourquoi les adresses MAC bougent après un changement STP

Quand un chemin de couche 2 change, un commutateur peut devoir réapprendre où se trouvent les adresses MAC dynamiques. Les changements de topologie STP peuvent donc accompagner une accélération du vieillissement ou une suppression des entrées MAC, selon le protocole et l’implémentation. Pendant la convergence, certains paquets peuvent être perdus ou temporairement acheminés par un chemin différent.

Un message de changement de topologie n’indique pas forcément un incident ; en revanche, des changements répétés, nombreux ou synchronisés avec des coupures justifient une enquête. Relie les messages STP aux événements physiques, aux modifications d’agrégats et aux journaux des ports.

### 6.2. Indices typiques d’une boucle ou d’une instabilité

| Indice | Hypothèses possibles | Premiers contrôles |
|---|---|---|
| `MACFLAP` / même MAC vue sur plusieurs ports | boucle, agrégat incohérent, équipement pontant plusieurs liens | table MAC, ports concernés, EtherChannel, STP |
| changements de topologie répétés | lien instable, port edge incorrect, équipement raccordé/débranché fréquemment | `show spanning-tree detail`, logs, état des interfaces |
| racine inattendue | priorité mal réglée, switch ajouté, mauvais périmètre de confiance | Root ID par VLAN/instance, inventaire des BID |
| port `root-inconsistent` | BPDU supérieure reçue sur un port protégé par Root Guard | BPDUs du voisin et intention de la conception |
| port `loop-inconsistent` | BPDU attendue manquante sur un port protégé par Loop Guard | liaison unidirectionnelle, optique, voisin, erreurs |
| port err-disabled après BPDU | BPDU Guard déclenché, selon configuration | cause, port attendu edge ou trunk, logs |

### 6.3. Runbook court — changement de topologie inattendu

```text
ALERTE : STP change fréquemment
       |
       v
1. Capturer show spanning-tree detail + show logging
       |
       v
2. Identifier VLAN / instance / port et Root ID
       |
       v
3. Corréler les horodatages avec l'état des liens et EtherChannel
       |
       v
4. Vérifier BPDU Guard, Root Guard, Loop Guard et les ports edge
       |
       v
5. Isoler la cause probable avec une modification minimale
       |
       v
6. Vérifier la stabilité, les rôles/états et les services utilisateurs
```

Ne neutralise pas STP pour empêcher les logs : cela risque de transformer un symptôme visible en boucle de couche 2.

### 6.4. Commandes essentielles d’investigation

```cisco
show spanning-tree summary
show spanning-tree detail
show spanning-tree vlan 10
show spanning-tree root
show spanning-tree inconsistentports
show mac address-table dynamic
show logging
show interfaces status
show interfaces counters errors
show etherchannel summary
```

Toutes ces commandes ne sont pas disponibles avec exactement la même syntaxe sur chaque plateforme. Si une commande est refusée, vérifie la variante documentée et conserve l’objectif de la mesure : arbre actif, rôle des ports, événements, compteurs physiques et état de l’agrégat.


## 7. EtherChannel et STP

### 7.1. STP voit normalement le port-channel comme un lien logique

Lorsque plusieurs liens physiques sont regroupés de manière cohérente dans un EtherChannel, STP traite habituellement le port-channel comme une interface logique, plutôt que de choisir un port STP distinct pour chaque membre. Une incohérence dans le groupe, le protocole d’agrégation ou la configuration des deux extrémités peut produire des résultats inattendus et parfois contribuer à une boucle.

Vérifie ensemble STP et l’agrégation :

```cisco
show etherchannel summary
show interfaces port-channel 1
show spanning-tree interface port-channel 1 detail
show interfaces trunk
```

N’ajoute pas ou ne retire pas un membre d’un port-channel en cours de production sans évaluer l’effet sur la bande passante, la redondance et l’arbre STP. La syntaxe et le mode d’agrégation (LACP, PAgP ou statique) dépendent de la configuration visée.

### 7.2. Diagnostic si les membres sont incohérents

Vérifie les points suivants sur les deux extrémités :

- même mode de couche 2 ou de couche 3, selon l’objectif ;
- paramètres trunk/access cohérents ;
- liste des VLAN autorisés et VLAN natif cohérents lorsqu’il s’agit d’un trunk ;
- vitesse, duplex et caractéristiques physiques compatibles ;
- protocole d’agrégation et paramètres de négociation concordants ;
- ports membres qui apparaissent dans l’état agrégé attendu.

Une agrégation saine simplifie la topologie pour STP ; une agrégation mal configurée peut compliquer fortement l’analyse. N’utilise pas la suppression de STP comme méthode de dépannage d’EtherChannel.


## 8. Laboratoires pratiques

Ces laboratoires sont conçus pour Cisco Packet Tracer lorsque les commandes y sont prises en charge, ou pour des commutateurs virtuels/physiques compatibles. Les protections et détails MST peuvent être absents ou simplifiés dans certaines versions de Packet Tracer ; dans ce cas, note cette limite au lieu de conclure que le mécanisme réel fonctionne différemment.

### Laboratoire 1 — lire une élection avec plusieurs chemins

**Objectif :** déterminer pourquoi un port est Root, Designated ou Alternate.

**Topologie :** trois commutateurs en triangle : SW1 en haut, SW2 à gauche et SW3 à droite. Chaque commutateur est relié aux deux autres. Place un poste sur SW2 et un poste sur SW3. Utilise un seul VLAN de test, par exemple VLAN 10.

**Étapes :**

1. Configure les liens inter-commutateurs en trunk si la simulation le nécessite.
2. Vérifie la présence du VLAN 10 aux emplacements nécessaires.
3. Exécute `show spanning-tree vlan 10` sur les trois commutateurs.
4. Note le Root ID, le Root Port de chaque commutateur non racine, le port désigné sur chaque segment et le port alternatif.
5. Modifie la priorité de SW3 de façon contrôlée afin de tester l’élection, puis vérifie le changement.
6. Rétablis la priorité initiale et documente les différences.

**Résultat attendu :** une seule racine pour VLAN 10, un arbre sans boucle, un chemin de secours non-forwarding et une explication du résultat basée sur les champs observés.

### Laboratoire 2 — contrôler la racine primaire et secondaire

**Objectif :** faire en sorte que SW1 soit racine préférée et SW2 soit racine de secours.

Sur SW1, dans le VLAN de test :

```cisco
spanning-tree vlan 10 root primary
```

Sur SW2 :

```cisco
spanning-tree vlan 10 root secondary
```

Puis :

```cisco
show spanning-tree vlan 10
show spanning-tree root
```

**À valider :** SW1 est la racine de VLAN 10 ; SW2 possède une priorité adaptée pour devenir racine si SW1 disparaît, en fonction de l’état des autres commutateurs. Si ce n’est pas le résultat observé, relève les priorités effectives et les Bridge ID au lieu d’ajouter des valeurs au hasard.

### Laboratoire 3 — distinguer BPDU Guard et Root Guard

**Objectif :** observer deux protections pour deux problèmes différents.

**Partie A — BPDU Guard :** configure PortFast et BPDU Guard sur un port relié à un terminal. Si la plateforme permet une simulation sûre, raccorde temporairement un commutateur de test pour voir le comportement déclenché par une BPDU. Ne réalise pas cette manipulation sur une liaison de production.

**Partie B — Root Guard :** dans une topologie de laboratoire, place Root Guard sur une frontière où un commutateur aval ne doit pas devenir racine. Ajuste la priorité de l’équipement aval pour qu’il tente de présenter une BPDU supérieure. Observe le port inconsistent et les logs.

**Résultat attendu :** expliquer pourquoi BPDU Guard protège un port de bordure, tandis que Root Guard contrôle une tentative de déplacement de la racine. Réinitialise les changements de laboratoire après l’observation.

### Laboratoire 4 — analyser une panne logique ou physique

**Objectif :** associer les symptômes aux preuves.

1. Capturer `show spanning-tree detail`, `show interfaces status` et `show logging` dans une topologie stable.
2. Désactiver un lien redondant en laboratoire.
3. Observer le rôle/état de l’Alternate et le chemin qui reprend le forwarding.
4. Réactiver le lien et mesurer le changement de topologie.
5. Comparer les horodatages des logs avec les rôles STP et l’état des interfaces.
6. Écrire une courte analyse : événement, preuve, impact, cause probable, correction et contrôle final.

**Important :** ce laboratoire mesure une convergence observée sur une topologie donnée. Ne transforme pas la durée mesurée en promesse universelle pour toutes les topologies ou versions logicielles.


## 9. Méthode d’intervention en environnement réel

### 9.1. Avant le changement

- identifier le protocole actif et le mode par VLAN/instance ;
- documenter la racine actuelle et la racine cible ;
- capturer la configuration et les sorties de vérification ;
- déterminer les VLAN, trunks, EtherChannels et services qui peuvent être affectés ;
- prévoir la fenêtre de changement, le test de connectivité et le retour arrière.

### 9.2. Pendant le changement

- effectuer un seul changement principal à la fois ;
- éviter les modifications simultanées de priorité, coût, protections et EtherChannel ;
- surveiller les journaux et les changements de topologie ;
- vérifier la stabilité de la racine et des rôles de ports avant d’engager une autre étape.

### 9.3. Après le changement

- vérifier Root ID, Root Port, Designated Ports et ports Alternate ;
- vérifier les états inconsistent ou err-disabled ;
- confirmer que les VLAN et trunks nécessaires sont actifs ;
- tester les services utilisateurs (passerelle, DHCP, DNS et communication attendue) ;
- conserver les sorties après intervention et mettre à jour le schéma réseau.

### 9.4. Exemple de plan de retour arrière

| Changement | Vérification d’acceptation | Retour arrière possible |
|---|---|---|
| priorité de racine | Root ID correspond à la cible, connectivité stable | restaurer la priorité précédente documentée |
| coût ou priorité d’un port | rôle/chemin conforme au plan, aucun service perdu | remettre la valeur précédente |
| activation d’une protection | état des ports cohérent avec l’architecture, aucune protection involontaire | retirer ou ajuster la protection seulement après analyse de la cause et suivant la procédure validée |
| migration vers MST/Rapid-PVST+ | compatibilité, région/mappage et topologie vérifiés | appliquer la procédure de migration inverse validée ; ne pas improviser en production |

Le retour arrière doit être préparé avant la fenêtre, pas inventé pendant un incident. Certaines protections doivent rester actives : si elles se déclenchent, recherche la cause plutôt que de les désactiver automatiquement.


## 10. Exercices d’évaluation avec corrigés

### Questions

**1.** Deux chemins présentent le même Root ID. Le chemin A a un coût total de 19 et le chemin B un coût total de 8. Lequel est préféré ?

**2.** Deux chemins ont le même Root ID et le même coût total. Quels champs contribuent au départage suivant ?

**3.** Pourquoi un port Alternate en état Discarding est-il utile ?

**4.** Quelle différence fondamentale existe entre BPDU Guard et Root Guard ?

**5.** Quel problème Loop Guard cherche-t-il à éviter lorsque les BPDU attendues ne sont plus reçues sur certains ports ?

**6.** Pourquoi `root primary` doit-il être suivi d’une vérification de la priorité effective ?

**7.** Quelle différence de conception principale distingue Rapid-PVST+ de MSTP ?

**8.** Cite les paramètres importants pour vérifier que deux commutateurs appartiennent à la même région MST.

**9.** Une MAC apparaît alternativement sur deux interfaces et les changements STP sont fréquents. Cite au moins trois pistes à examiner.

**10.** Pourquoi ne faut-il pas désactiver STP pour résoudre une boucle apparente ?

### Corrigés

1. Le chemin B, car son coût total vers la racine est inférieur.
2. Le Sender Bridge ID, puis le Sender Port ID et, selon les cas de départage, l’identifiant du port local. Utiliser la sortie réelle du commutateur pour confirmer l’ordre appliqué.
3. Il conserve un chemin de secours sans le laisser transférer simultanément avec un chemin actif susceptible de créer une boucle.
4. BPDU Guard protège typiquement un port de bordure contre une BPDU inattendue ; Root Guard empêche qu’une information de racine supérieure reçue sur un port protégé déplace la racine attendue.
5. Il évite qu’un port non désigné qui ne reçoit plus les BPDU attendues assume à tort le rôle désigné et passe en forwarding, ce qui pourrait créer une boucle.
6. Parce que le macro ajuste généralement la priorité relativement à l’état observé et que le résultat dépend des autres commutateurs, de l’Extended System ID et de l’instance ciblée.
7. Rapid-PVST+ maintient une instance par VLAN ; MSTP mappe plusieurs VLAN sur un nombre plus réduit d’instances.
8. Nom de région, révision de configuration et mappage VLAN-vers-instance. Il faut aussi vérifier le protocole et le comportement de frontière.
9. Boucle de couche 2, port-channel/EtherChannel incohérent, lien instable, équipement pontant plusieurs ports, mauvais rôle de port ou câblage inattendu.
10. Parce que le contrôle des boucles de couche 2 peut disparaître et une diffusion peut saturer le réseau. Il faut trouver et corriger la cause en conservant la prévention des boucles.


## 11. Points à retenir

- Le choix du Root Port repose sur le Root ID et le coût du chemin, puis sur des critères de départage précis.
- RSTP accélère généralement les transitions grâce à des mécanismes de rôle, de BPDU et de synchronisation ; l’effet dépend de la topologie et de la compatibilité.
- Root Guard, Loop Guard, BPDU Guard et UDLD ciblent des scénarios différents : leur placement doit correspondre à la conception.
- PVST+/Rapid-PVST+ permet des décisions par VLAN ; MST regroupe plusieurs VLAN dans des instances partagées, avec une configuration de région cohérente.
- Un MAC flapping ou des changements de topologie répétés doivent être corrélés aux événements physiques, aux protections, aux trunks et aux agrégats.
- Capturer l’état avant/après, appliquer une modification à la fois et préparer un retour arrière sont des exigences opérationnelles, pas de simples formalités.

## 12. Références techniques

Consulte toujours le guide correspondant au modèle et à la version logicielle.

- [Cisco — STP Configuration Guide, IOS XE 17 / Catalyst 9000](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/stp/stp-configuration-guide/m-stp.html) : modes STP, rôles de ports et commandes de configuration.
- [Cisco — Understand STP Loop Guard and UDLD](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol-stp-8021d/218321-configure-stp-with-loop-guard-and-bpdu-s.html) : comportement Loop Guard et défaillances unidirectionnelles.
- [Cisco — PortFast et BPDU Guard](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10586-65.html) : protections des ports de bordure et précautions.
- [Cisco — Root Guard](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10588-74.html) : protection du placement de la racine.
- [IEEE 802.1Q — Bridges and Bridged Networks](https://standards.ieee.org/ieee/802.1q/10323/) : cadre normalisé du pontage et des VLAN, incluant les mécanismes spanning tree modernes.

Les schémas de ce cours sont conceptuels. Pour les choix de configuration, les sorties de commande de l’équipement et la documentation de la version utilisée restent les références opérationnelles.
