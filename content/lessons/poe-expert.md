# PoE — Expert
## Architecture, ingénierie de puissance, résilience et observabilité

**Niveau :** Expert  
**Prérequis :** maîtriser les standards PoE, les mécanismes de classification, le calcul du budget et le diagnostic des ports.  
**Objectif général :** concevoir et exploiter une infrastructure PoE fiable, explicable, dimensionnée et vérifiable.


# 1. Le PoE comme ressource critique d'infrastructure

À grande échelle, le PoE doit être géré comme une ressource d'infrastructure à part entière. Il ne s'agit pas simplement d'activer une fonction sur quelques ports.

Un réseau peut alimenter des centaines de téléphones, caméras, points d'accès et équipements industriels. Une erreur de dimensionnement peut provoquer des refus d'admission, limiter la croissance du réseau ou entraîner une perte de service.

La conception doit intégrer :
- les capacités du matériel ;
- la puissance nécessaire aux PD ;
- les réservations et les règles d'admission ;
- les pertes du câblage ;
- les besoins de redondance ;
- le comportement lors d'un incident ;
- la supervision et l'audit.

La question de conception n'est pas uniquement « combien de watts consomment les appareils ? ». Il faut aussi savoir quelle capacité doit rester disponible pour garantir un comportement déterminé dans les conditions prévues.


# 2. Les quatre niveaux de capacité

Pour dimensionner un système PoE, il faut considérer plusieurs niveaux de contrainte.

## 2.1 Capacité du port

Chaque port peut avoir une limite de puissance. Le budget global du switch ne permet pas de dépasser cette limite individuelle.

Un PD demandant un niveau de puissance supérieur à la capacité du port peut être refusé ou ne pas fonctionner conformément aux exigences prévues.

## 2.2 Capacité électrique du PSE

La capacité électrique utilisable dépend de l'alimentation du châssis, de son architecture et de son état opérationnel.

Un switch possédant plusieurs alimentations peut disposer d'une capacité différente selon qu'il fonctionne en état nominal ou après la perte d'une source.

## 2.3 Budget et politique du contrôleur

Le contrôleur PoE gère les réservations et l'admission des ports. Le budget utilisé pour l'admission peut être différent de la consommation instantanée mesurée.

L'admission dépend notamment de la capacité utilisable, des allocations existantes, des limites du port et de la politique du matériel.

## 2.4 Capacité du PD et de la liaison

Le PD doit être conçu pour le standard et la puissance prévus. Le câblage doit respecter les exigences électriques et Ethernet de l'application.

Une installation ne peut être déclarée conforme à partir du seul fait que le voyant de lien s'allume.


# 3. Construire un modèle de charge réaliste

Le dimensionnement commence par un inventaire documenté.

Pour chaque modèle de PD, il faut connaître :
- le standard et les niveaux de puissance supportés ;
- les besoins électriques prévus ;
- les fonctions qui augmentent la consommation ;
- la puissance nécessaire au démarrage ou dans les états importants ;
- le comportement en cas de puissance insuffisante ;
- le câble et la portée prévus ;
- les exigences de disponibilité ;
- les informations de télémétrie disponibles.

La fiche technique du matériel réel doit rester la référence. Une valeur générique associée à une famille d'appareils n'est pas suffisante.

## 3.1 États opérationnels

Un PD peut présenter plusieurs profils de consommation :
- faible consommation ;
- fonctionnement nominal ;
- activité intensive ;
- démarrage ;
- activation de fonctions supplémentaires ;
- fonctionnement limité lorsqu'une capacité réduite est prise en charge par le fabricant.

Le dimensionnement doit déterminer quels états sont pertinents pour le service.

Une consommation moyenne observée dans un scénario calme peut sous-estimer les besoins dans un scénario de forte activité. À l'inverse, additionner systématiquement les maximums annoncés peut surdimensionner un projet si une autre méthode d'allocation validée est prévue.

Le choix doit être cohérent avec les garanties recherchées. Un profil mesuré peut aider à comprendre le comportement, mais il ne justifie jamais une alimentation dépassant les limites du matériel.

## 3.2 Ce qu'apporte une campagne de mesure

Une campagne de mesure permet d'observer les comportements réels :
- différences entre modèles ;
- variations temporelles ;
- écarts entre réservation et consommation ;
- profils au démarrage ;
- événements inhabituels ;
- effets d'une modification de configuration.

Les mesures complètent les fiches techniques, sans les remplacer. Il faut enregistrer l'heure, le contexte, la fréquence de mesure et les limites du compteur pour pouvoir interpréter correctement les résultats.


# 4. Type, classe, négociation et admission

Le type et la classe PoE fournissent des repères sur les capacités et les besoins électriques. Ils ne doivent pas être confondus avec la mesure instantanée ou l'allocation effective.

**Type PoE :** niveau de capacité défini par le standard concerné.

**Classe :** niveau de puissance déterminé par le mécanisme de classification applicable.

**Négociation :** échange éventuel permettant de préciser des besoins entre appareils compatibles.

**Allocation :** quantité de puissance que le contrôleur accepte de réserver ou de fournir, dans les limites du système.

**Consommation mesurée :** puissance observée au cours d'une mesure réelle, si le matériel permet cette collecte.

## 4.1 LLDP

LLDP est un protocole de découverte de voisins de couche 2. Certaines implémentations PoE exploitent LLDP pour échanger des informations complémentaires sur les besoins de puissance.

Le comportement varie suivant le standard, le PSE, le PD et les capacités du logiciel. Il faut donc vérifier quelles informations sont effectivement échangées par le matériel.

LLDP ne remplace pas automatiquement la détection électrique et ne permet pas d'ignorer les limites du port ou du système.

## 4.2 AutoClass et fonctionnalités avancées

IEEE 802.3bt a introduit des fonctions supplémentaires, dont AutoClass lorsqu'elle est prise en charge. Dans les conditions prévues, cette fonction permet au PSE d'utiliser des informations de mesure obtenues avec le PD placé dans un état de consommation connu pour ajuster l'allocation.

Il ne faut pas supposer que chaque switch et chaque PD prennent en charge toutes les fonctionnalités de 802.3bt. Avant d'en tenir compte pour le dimensionnement, vérifier la documentation et le comportement du matériel concerné.


# 5. Schéma animé — Architecture de décision d'admission

Ce schéma sépare les contrôles. La décision ne repose pas exclusivement sur le budget global : la compatibilité et les limites individuelles doivent également être satisfaites.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 375" role="img" aria-labelledby="poee1-title">
  <title id="poee1-title">Architecture de décision d'admission PoE avec branche de refus</title>
  <defs>
    <marker id="poee1-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0 0 L6 3 L0 6 Z" fill="#65c9d8"/>
    </marker>
    <style>
      .poee1-bg{fill:#0d1524}
      .poee1-card{fill:#192a42;stroke:#4c6587;stroke-width:1.5}
      .poee1-head{fill:#f8fafc;font:700 14px Arial,sans-serif}
      .poee1-txt{fill:#ccdae9;font:12px Arial,sans-serif}
      .poee1-note{fill:#9fb2ca;font:11px Arial,sans-serif}
      .poee1-flow{fill:none;stroke:#65c9d8;stroke-width:2.6;stroke-dasharray:7 7;marker-end:url(#poee1-arrow);animation:poee1-dash 1s linear infinite}
      .poee1-good{fill:#153a35;stroke:#46c9a4;stroke-width:1.6}
      .poee1-bad{fill:#392b20;stroke:#edb866;stroke-width:1.6}
      .poee1-dot{fill:#46c9a4;animation:poee1-pulse 1.6s ease-in-out infinite}
      @keyframes poee1-dash{to{stroke-dashoffset:-28}}
      @keyframes poee1-pulse{0%,100%{opacity:.4}50%{opacity:1}}
      @media(prefers-reduced-motion:reduce){.poee1-flow,.poee1-dot{animation:none}}
    </style>
  </defs>
  <rect class="poee1-bg" width="940" height="375" rx="16"/>
  <text class="poee1-head" x="30" y="32" font-size="19">Admission contrôlée d'un nouvel équipement PoE</text>
  <text class="poee1-note" x="30" y="52">Chaque contrôle vérifie une contrainte différente : réussir une étape ne garantit pas les suivantes.</text>
  <g>
    <rect class="poee1-card" x="25" y="76" width="205" height="105" rx="10"/>
    <text class="poee1-head" x="127" y="102" text-anchor="middle">1 · Identifier le PD</text>
    <text class="poee1-txt" x="127" y="126" text-anchor="middle">Détection et capacité</text>
    <text class="poee1-txt" x="127" y="144" text-anchor="middle">PoE reconnue</text>
    <text class="poee1-note" x="127" y="164" text-anchor="middle">Profil et classe applicables</text>
    <rect class="poee1-card" x="250" y="76" width="205" height="105" rx="10"/>
    <text class="poee1-head" x="352" y="102" text-anchor="middle">2 · Vérifier le port</text>
    <text class="poee1-txt" x="352" y="126" text-anchor="middle">Limite électrique</text>
    <text class="poee1-txt" x="352" y="144" text-anchor="middle">et compatibilité du lien</text>
    <text class="poee1-note" x="352" y="164" text-anchor="middle">PSE, PD et câblage</text>
    <rect class="poee1-card" x="475" y="76" width="205" height="105" rx="10"/>
    <text class="poee1-head" x="577" y="102" text-anchor="middle">3 · Évaluer la capacité</text>
    <text class="poee1-txt" x="577" y="126" text-anchor="middle">Budget utilisable</text>
    <text class="poee1-txt" x="577" y="144" text-anchor="middle">et réservations existantes</text>
    <text class="poee1-note" x="577" y="164" text-anchor="middle">État normal ou dégradé</text>
    <rect class="poee1-card" x="700" y="76" width="215" height="105" rx="10"/>
    <text class="poee1-head" x="807" y="102" text-anchor="middle">4 · Appliquer la politique</text>
    <text class="poee1-txt" x="807" y="126" text-anchor="middle">Priorité et règles de service</text>
    <text class="poee1-txt" x="807" y="144" text-anchor="middle">Autorisation de l'allocation</text>
    <text class="poee1-note" x="807" y="164" text-anchor="middle">Décision du contrôleur PSE</text>
  </g>
  <path class="poee1-flow" d="M230 128 H250"/>
  <path class="poee1-flow" d="M455 128 H475"/>
  <path class="poee1-flow" d="M680 128 H700"/>
  <path class="poee1-flow" d="M807 181 V218 H600 V255"/>
  <path class="poee1-flow" d="M807 218 V255"/>
  <text x="600" y="242" text-anchor="middle" fill="#8fe4c7" font-size="11" font-weight="700">ADMISSION ACCEPTÉE</text>
  <text x="807" y="242" text-anchor="middle" fill="#ffd28a" font-size="11" font-weight="700">REFUS OU ATTENTE</text>
  <rect class="poee1-good" x="490" y="255" width="220" height="64" rx="10"/>
  <text class="poee1-head" x="600" y="280" text-anchor="middle">Réserver et alimenter</text>
  <text class="poee1-txt" x="600" y="301" text-anchor="middle">Contrôler le fonctionnement</text>
  <circle class="poee1-dot" cx="694" cy="270" r="4"/>
  <rect class="poee1-bad" x="720" y="255" width="190" height="64" rx="10"/>
  <text class="poee1-head" x="815" y="280" text-anchor="middle">Ne pas alimenter</text>
  <text class="poee1-txt" x="815" y="301" text-anchor="middle">Collecter le motif du refus</text>
  <text class="poee1-note" x="30" y="350">Modèle logique générique ; l'ordre et les règles détaillés dépendent du PSE et de sa configuration.</text>
</svg>


# 6. Distinguer capacité, réservation et consommation

La conception et la supervision doivent conserver les différentes grandeurs électriques séparément.

## 6.1 Capacité utilisable

Il s'agit de la puissance que le système peut réellement consacrer au PoE dans son état actuel. Cette capacité peut dépendre des blocs d'alimentation, du mode de fonctionnement et des restrictions de la plate-forme.

## 6.2 Réservation

La puissance réservée est retenue par le contrôleur selon les règles d'allocation. Elle n'est pas nécessairement égale à la consommation instantanée du PD.

## 6.3 Consommation mesurée

La consommation mesurée est une observation temporelle. Elle peut varier selon les fonctions du PD et la méthode de mesure.

Une différence entre réservation et consommation ne constitue pas nécessairement un défaut. Elle peut être parfaitement normale si le système réserve la capacité nécessaire au fonctionnement prévu du PD.

## 6.4 Exemple de télémétrie

Supposons :
- budget utilisable : 400 W ;
- réservations : 240 W ;
- consommation mesurée : 160 W.

La différence entre réservation et consommation est de 80 W.

Il ne faut pas conclure automatiquement que 80 W peuvent être réaffectés. Le contrôleur peut continuer à retenir la réservation selon la classe, les capacités et la politique d'admission. La capacité disponible pour un nouveau PD doit être évaluée selon le fonctionnement réel du système.


# 7. Schéma animé — Réservations et mesures

Les barres utilisent une échelle commune de 0 à 400 W. L'animation remplit progressivement les valeurs prévues pour faciliter la comparaison visuelle.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 355" role="img" aria-labelledby="poee2-title">
  <title id="poee2-title">Comparaison de la capacité PoE, des réservations et de la consommation mesurée</title>
  <defs>
    <style>
      .poee2-bg{fill:#0d1524}
      .poee2-head{fill:#f8fafc;font:700 18px Arial,sans-serif}
      .poee2-label{fill:#e2ebf7;font:700 13px Arial,sans-serif}
      .poee2-txt{fill:#cfdaea;font:12px Arial,sans-serif}
      .poee2-note{fill:#9eb1c9;font:11px Arial,sans-serif}
      .poee2-track{fill:#27374e}
      .poee2-reserved{fill:#649bff}
      .poee2-observed{fill:#4bd0b1}
      .poee2-grid{stroke:#3c506c;stroke-dasharray:3 6}
    </style>
  </defs>
  <rect class="poee2-bg" width="940" height="355" rx="16"/>
  <text class="poee2-head" x="30" y="33">Distinguer l'allocation du système et la mesure réelle</text>
  <text class="poee2-note" x="30" y="53">Exemple : budget utilisable 400 W · réservation 240 W · consommation mesurée 160 W</text>
  <g>
    <line class="poee2-grid" x1="70" y1="78" x2="70" y2="235"/>
    <line class="poee2-grid" x1="270" y1="78" x2="270" y2="235"/>
    <line class="poee2-grid" x1="470" y1="78" x2="470" y2="235"/>
    <line class="poee2-grid" x1="670" y1="78" x2="670" y2="235"/>
    <line class="poee2-grid" x1="870" y1="78" x2="870" y2="235"/>
  </g>
  <text class="poee2-label" x="30" y="93">Budget total : 400 W</text>
  <rect class="poee2-track" x="70" y="105" width="800" height="31" rx="5"/>
  <rect class="poee2-reserved" x="70" y="105" width="0" height="31" rx="5">
    <animate attributeName="width" from="0" to="480" dur="1.2s" begin="0.1s" fill="freeze"/>
  </rect>
  <rect x="550" y="105" width="0" height="31" fill="#54657c">
    <animate attributeName="width" from="0" to="320" dur="1s" begin="1s" fill="freeze"/>
  </rect>
  <text x="310" y="125" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">240 W réservés</text>
  <text x="710" y="125" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">160 W non réservés</text>
  <text class="poee2-label" x="30" y="175">Consommation observée</text>
  <rect class="poee2-track" x="70" y="186" width="800" height="31" rx="5"/>
  <rect class="poee2-observed" x="70" y="186" width="0" height="31" rx="5">
    <animate attributeName="width" from="0" to="320" dur="1.3s" begin="0.5s" fill="freeze"/>
  </rect>
  <text x="230" y="206" fill="#062b24" font-size="12" font-weight="700" text-anchor="middle">160 W mesurés</text>
  <g class="poee2-note">
    <text x="70" y="238" text-anchor="middle">0 W</text>
    <text x="270" y="238" text-anchor="middle">100 W</text>
    <text x="470" y="238" text-anchor="middle">200 W</text>
    <text x="670" y="238" text-anchor="middle">300 W</text>
    <text x="870" y="238" text-anchor="middle">400 W</text>
  </g>
  <rect x="30" y="258" width="880" height="63" rx="10" fill="#192b42" stroke="#506887"/>
  <text class="poee2-label" x="50" y="282">Décision d'admission</text>
  <text class="poee2-txt" x="50" y="303">Les 160 W mesurés ne libèrent pas automatiquement 80 W de la réservation.</text>
  <text class="poee2-note" x="30" y="342">La capacité non réservée est une marge arithmétique ; les règles d'admission restent applicables.</text>
</svg>


# 8. Dimensionnement en mode nominal et en mode dégradé

Un système dont le budget est suffisant en mode nominal peut ne pas respecter ses exigences en cas de perte d'une alimentation redondante.

Il faut donc établir la capacité utilisable dans les états matériels pertinents :
- fonctionnement normal ;
- perte d'une alimentation ;
- indisponibilité d'un module ;
- configuration de puissance dégradée prévue par le constructeur.

## 8.1 Exemple

Supposons une capacité PoE utilisable de 500 W en mode nominal et de 300 W après la perte d'une source, selon les informations de conception retenues pour cet exemple.

Les réservations atteignent 340 W.

En mode nominal, le budget semble suffisant. En mode dégradé, la capacité ne suffit plus à maintenir cette allocation.

Il faut alors définir la réponse opérationnelle :
- quels PD sont essentiels ;
- quelles fonctions peuvent être arrêtées ;
- comment l'insuffisance de puissance est signalée ;
- quel service doit rester disponible ;
- comment restaurer le fonctionnement normal.

Les chiffres sont illustratifs et ne décrivent pas un modèle particulier de switch.

## 8.2 Priorité des équipements

Une politique de priorité aide à exprimer les besoins de service, lorsque le matériel prend en charge ce mécanisme.

Par exemple, les besoins d'une caméra de sécurité critique peuvent être différents de ceux d'un équipement non essentiel. Une priorité ne suffit toutefois pas : il faut vérifier que la capacité du système en mode dégradé permet de fournir l'alimentation attendue aux équipements prioritaires.

La criticité doit donc être documentée et traduite dans une configuration adaptée à la plate-forme réelle.


# 9. Résilience : redondance électrique et redondance réseau

Plusieurs notions doivent être séparées.

**Redondance des alimentations du switch :** plusieurs sources alimentent le châssis. La capacité utilisable après la perte d'une source dépend de la conception du matériel.

**Redondance des switches :** un switch de secours peut préserver une partie du service, mais les chemins d'alimentation et de réseau doivent être considérés séparément.

**Redondance du chemin réseau :** deux chemins de données ne prouvent pas que l'équipement dispose de deux chemins électriques indépendants.

**Redondance du PD :** certains équipements disposent de plusieurs entrées d'alimentation. Leur rôle dépend de la conception du produit.

La redondance doit être prouvée dans le scénario de panne pertinent. Le simple nombre de switches ou de connecteurs ne suffit pas.

## 9.1 Ne pas mettre en parallèle des sorties PoE arbitrairement

Il ne faut pas connecter deux sorties PoE pour additionner leurs puissances, sauf si la conception du matériel prend explicitement en charge le mode d'alimentation envisagé.

Si un PD possède deux entrées, vérifier si elles assurent le secours, le partage de charge ou une fonction spécifique définie par le fabricant.

## 9.2 Schéma animé — Deux chemins PoE indépendants

Le dessin représente un PD expressément conçu pour deux entrées. Il ne s'applique pas à tous les équipements PoE.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" role="img" aria-labelledby="poee3-title">
  <title id="poee3-title">Chemins d'alimentation PoE indépendants vers un appareil à deux entrées compatibles</title>
  <defs>
    <marker id="poee3-arrowA" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0 0 L6 3 L0 6 Z" fill="#65a5ff"/>
    </marker>
    <marker id="poee3-arrowB" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0 0 L6 3 L0 6 Z" fill="#f4c06c"/>
    </marker>
    <style>
      .poee3-bg{fill:#0d1524}
      .poee3-card{fill:#1a2b42;stroke:#516b8b;stroke-width:1.6}
      .poee3-head{fill:#f8fafc;font:700 15px Arial,sans-serif}
      .poee3-txt{fill:#cfdaea;font:12px Arial,sans-serif}
      .poee3-note{fill:#a0b2c9;font:11px Arial,sans-serif}
      .poee3-pathA{fill:none;stroke:#65a5ff;stroke-width:3.4;stroke-dasharray:9 8;marker-end:url(#poee3-arrowA);animation:poee3-runA 1.1s linear infinite}
      .poee3-pathB{fill:none;stroke:#f4c06c;stroke-width:3.4;stroke-dasharray:9 8;marker-end:url(#poee3-arrowB);animation:poee3-runB 1.3s linear infinite}
      @keyframes poee3-runA{to{stroke-dashoffset:-34}}
      @keyframes poee3-runB{to{stroke-dashoffset:-34}}
      @media(prefers-reduced-motion:reduce){.poee3-pathA,.poee3-pathB{animation:none}}
    </style>
  </defs>
  <rect class="poee3-bg" width="960" height="390" rx="16"/>
  <text class="poee3-head" x="30" y="32" font-size="19">Deux chemins d'alimentation indépendants</text>
  <text class="poee3-note" x="30" y="52">Le PD doit explicitement prendre en charge deux entrées d'alimentation.</text>
  <rect class="poee3-card" x="35" y="75" width="240" height="88" rx="10"/>
  <text class="poee3-head" x="155" y="103" text-anchor="middle">Switch PoE A</text>
  <text class="poee3-txt" x="155" y="126" text-anchor="middle">PSE et port validés</text>
  <text class="poee3-note" x="155" y="146" text-anchor="middle">Chemin électrique A</text>
  <rect class="poee3-card" x="35" y="220" width="240" height="88" rx="10"/>
  <text class="poee3-head" x="155" y="248" text-anchor="middle">Switch PoE B</text>
  <text class="poee3-txt" x="155" y="271" text-anchor="middle">PSE et port validés</text>
  <text class="poee3-note" x="155" y="291" text-anchor="middle">Chemin électrique B</text>
  <rect class="poee3-card" x="655" y="100" width="270" height="177" rx="12"/>
  <text class="poee3-head" x="790" y="126" text-anchor="middle">PD à double entrée</text>
  <rect x="690" y="143" width="200" height="36" rx="6" fill="#203e60" stroke="#65a5ff" stroke-width="1.4"/>
  <text class="poee3-txt" x="790" y="166" text-anchor="middle">Entrée PoE A</text>
  <rect x="690" y="195" width="200" height="36" rx="6" fill="#403321" stroke="#f4c06c" stroke-width="1.4"/>
  <text class="poee3-txt" x="790" y="218" text-anchor="middle">Entrée PoE B</text>
  <text class="poee3-note" x="790" y="253" text-anchor="middle">Secours selon le fabricant</text>
  <path class="poee3-pathA" d="M275 119 H425 V161 H655"/>
  <path class="poee3-pathB" d="M275 264 H510 V213 H655"/>
  <text x="425" y="102" fill="#9ec8ff" font-size="12" font-weight="700" text-anchor="middle">Chemin A</text>
  <text x="510" y="290" fill="#ffdaa0" font-size="12" font-weight="700" text-anchor="middle">Chemin B</text>
  <rect x="275" y="327" width="410" height="37" rx="8" fill="#39291d" stroke="#e4ad62"/>
  <text class="poee3-note" x="480" y="350" text-anchor="middle">Ne pas mettre en parallèle des sorties PoE sans prise en charge explicite.</text>
</svg>


# 10. Câblage et environnement thermique

Le PoE à puissance élevée nécessite une attention particulière au câblage.

La résistance électrique dissipe une partie de l'énergie sous forme de chaleur. Dans une installation comportant de nombreux câbles groupés, l'environnement thermique et la méthode de pose influencent les conditions de fonctionnement.

Les éléments à vérifier sont :
- la catégorie et le type du câble ;
- la longueur et la configuration du canal ;
- la qualité des conducteurs et des terminaisons ;
- l'absence de dommages ;
- les faisceaux de câbles et leurs conditions de pose ;
- la température ambiante ;
- les recommandations du fabricant du câblage et du matériel.

Il ne faut pas définir de limite thermique universelle sans se référer à l'installation concernée. La conformité dépend des standards, des matériaux et des pratiques de pose applicables.

Un lien Ethernet qui fonctionne ne suffit pas pour confirmer toutes les exigences électriques du PoE.


# 11. Observabilité : suivre l'état, les allocations et les incidents

Une supervision PoE fiable doit permettre de comprendre ce qui se passe sur chaque port et à l'échelle du système.

Elle doit distinguer quatre familles de données.

## 11.1 Santé opérationnelle

- état administratif du port ;
- état du lien Ethernet ;
- état de l'alimentation PoE ;
- détection ou présence du PD lorsque cette information est exposée ;
- événements d'activation, de coupure ou de refus.

## 11.2 Capacité et allocation

- budget total utilisable ;
- somme des réservations ;
- classe ou allocation par port ;
- marge calculée ;
- capacité disponible dans les états dégradés pertinents.

## 11.3 Mesures électriques

- consommation mesurée ;
- tension et courant si disponibles ;
- évolution des mesures ;
- résolution et fréquence de rafraîchissement.

Une mesure non disponible doit être distinguée de la valeur zéro. Il faut conserver les informations de capacité de la plate-forme afin d'éviter les interprétations erronées.

## 11.4 Contexte et historique

- nom et modèle du switch ;
- version logicielle ;
- port concerné ;
- modèle du PD ;
- événements horodatés ;
- modifications de configuration ;
- état des alimentations ;
- fenêtre de maintenance applicable.

La corrélation temporelle est importante. Si plusieurs PD tombent en même temps, les horodatages peuvent permettre de relier les incidents à un événement commun.


# 12. Schéma animé — Cycle de traitement d'un incident

Le processus distingue la détection, la collecte, le diagnostic et la validation. La remise en service ne se résume pas à un voyant redevenu vert : le service applicatif doit également être vérifié.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="poee4-title">
  <title id="poee4-title">Cycle opérationnel de détection, diagnostic et résolution d'un incident PoE</title>
  <defs>
    <marker id="poee4-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0 0 L6 3 L0 6 Z" fill="#63cbd5"/>
    </marker>
    <style>
      .poee4-bg{fill:#0d1524}
      .poee4-card{fill:#192a41;stroke:#506987;stroke-width:1.5}
      .poee4-head{fill:#f8fafc;font:700 14px Arial,sans-serif}
      .poee4-txt{fill:#cfdaea;font:12px Arial,sans-serif}
      .poee4-note{fill:#9eb1c9;font:11px Arial,sans-serif}
      .poee4-flow{fill:none;stroke:#63cbd5;stroke-width:2.7;stroke-dasharray:7 7;marker-end:url(#poee4-arrow);animation:poee4-dash 1s linear infinite}
      .poee4-alert{fill:#f4bf69;animation:poee4-pulse 1.3s ease-in-out infinite}
      @keyframes poee4-dash{to{stroke-dashoffset:-28}}
      @keyframes poee4-pulse{0%,100%{opacity:.35}50%{opacity:1}}
      @media(prefers-reduced-motion:reduce){.poee4-flow,.poee4-alert{animation:none}}
    </style>
  </defs>
  <rect class="poee4-bg" width="960" height="350" rx="16"/>
  <text class="poee4-head" x="30" y="32" font-size="19">Cycle opérationnel de traitement d'un incident PoE</text>
  <text class="poee4-note" x="30" y="52">Chaque étape produit les informations nécessaires à la suivante et conserve une trace du résultat.</text>
  <rect class="poee4-card" x="30" y="82" width="205" height="118" rx="10"/>
  <text class="poee4-head" x="132" y="108" text-anchor="middle">1 · Détecter</text>
  <text class="poee4-txt" x="132" y="133" text-anchor="middle">État anormal du port</text>
  <text class="poee4-txt" x="132" y="151" text-anchor="middle">ou du PD</text>
  <text class="poee4-note" x="132" y="176" text-anchor="middle">Conserver l'heure</text>
  <circle class="poee4-alert" cx="211" cy="98" r="5"/>
  <rect class="poee4-card" x="265" y="82" width="205" height="118" rx="10"/>
  <text class="poee4-head" x="367" y="108" text-anchor="middle">2 · Collecter</text>
  <text class="poee4-txt" x="367" y="133" text-anchor="middle">État PoE, réservations,</text>
  <text class="poee4-txt" x="367" y="151" text-anchor="middle">mesures et événements</text>
  <text class="poee4-note" x="367" y="176" text-anchor="middle">Avant toute modification</text>
  <rect class="poee4-card" x="500" y="82" width="205" height="118" rx="10"/>
  <text class="poee4-head" x="602" y="108" text-anchor="middle">3 · Diagnostiquer</text>
  <text class="poee4-txt" x="602" y="133" text-anchor="middle">Comparer les hypothèses</text>
  <text class="poee4-txt" x="602" y="151" text-anchor="middle">aux faits disponibles</text>
  <text class="poee4-note" x="602" y="176" text-anchor="middle">Isoler la cause probable</text>
  <rect class="poee4-card" x="735" y="82" width="195" height="118" rx="10"/>
  <text class="poee4-head" x="832" y="108" text-anchor="middle">4 · Corriger et valider</text>
  <text class="poee4-txt" x="832" y="133" text-anchor="middle">Correction contrôlée</text>
  <text class="poee4-txt" x="832" y="151" text-anchor="middle">Test du service réel</text>
  <text class="poee4-note" x="832" y="176" text-anchor="middle">Clôture avec preuve</text>
  <path class="poee4-flow" d="M235 141 H265"/>
  <path class="poee4-flow" d="M470 141 H500"/>
  <path class="poee4-flow" d="M705 141 H735"/>
  <rect x="30" y="232" width="900" height="76" rx="10" fill="#17283e" stroke="#4e6788"/>
  <text class="poee4-head" x="50" y="258">Dossier d'incident</text>
  <text class="poee4-txt" x="50" y="281">Port et modèle du PD · horodatages · statut PoE · allocation · mesure disponible · journaux · correction · résultat final</text>
  <text class="poee4-note" x="30" y="330">Le retour au vert ne suffit pas : valider aussi la fonction applicative et la stabilité après remise en service.</text>
</svg>


# 13. Alarmes et supervision proactive

Les alarmes doivent signaler les événements utiles à l'exploitation. Des alertes trop nombreuses ou mal contextualisées peuvent masquer les incidents importants.

Exemples d'événements à surveiller :
- budget utilisable insuffisant pour une nouvelle demande ;
- refus d'admission d'un PD critique ;
- alimentation redondante indisponible ;
- coupures répétées d'un même port ;
- variation inhabituelle de consommation lorsqu'une mesure fiable existe ;
- perte de données de supervision ;
- changement de statut qui ne correspond pas à une maintenance prévue.

Chaque alerte doit préciser la grandeur concernée. Une alerte sur le budget, une alerte sur la consommation et une alerte sur un refus d'admission ne décrivent pas le même phénomène.

Elle doit aussi déclencher une action compréhensible : collecte de données, vérification humaine, escalade ou intervention approuvée.

Les seuils sont à définir suivant le modèle de switch, les exigences de service et le comportement attendu du parc.


# 14. Automatisation PoE

L'automatisation est utile pour :
- collecter les états des ports ;
- inventorier les PD ;
- calculer des marges à partir de données fiables ;
- rapprocher les événements de leurs horodatages ;
- produire des rapports ;
- détecter les écarts par rapport à une politique.

Une automatisation ne doit pas transformer chaque différence observée en correction automatique.

Une boucle qui réactive un port sans analyser son défaut peut produire des cycles de redémarrage ou rendre la panne difficile à expliquer. De même, un système qui augmente une limite de puissance sans vérifier la capacité réelle du PD et du PSE introduit un risque.

## 14.1 Séparer les fonctions

Un système automatisé fiable sépare les étapes suivantes :

1. **Collecte :** récupérer les informations sans modifier l'équipement.
2. **Normalisation :** convertir les sorties des plates-formes en un modèle cohérent.
3. **Évaluation :** comparer l'état observé aux règles documentées.
4. **Décision :** déterminer si une intervention est nécessaire.
5. **Autorisation :** vérifier la criticité, les droits et les risques.
6. **Exécution :** appliquer une modification contrôlée.
7. **Validation :** confirmer le retour du service et l'état PoE.
8. **Audit :** enregistrer les observations initiales, les changements et leurs résultats.

Les opérations de lecture seule doivent être privilégiées au début du développement. Les modifications de ports critiques doivent exiger des contrôles d'autorisation, une procédure de retour arrière et des preuves d'exécution.


# 15. Stratégie de validation d'un déploiement

La validation doit aller au-delà du test consistant à brancher un PD et à constater qu'il s'allume.

Le plan de tests doit couvrir :
- la détection et l'admission ;
- la vérification de la réserve de puissance ;
- les limites de port ;
- les scénarios de consommation importants ;
- la qualité du câblage ;
- la collecte des mesures disponibles ;
- le traitement des insuffisances de capacité ;
- la redondance annoncée ;
- la récupération après incident ;
- la conservation des preuves.

## 15.1 Critères de réussite

Le plan doit définir ce qui constitue un résultat acceptable. Par exemple :
- les PD prévus sont admis conformément à leur capacité ;
- aucune limite électrique n'est dépassée ;
- le budget conserve la marge exigée ;
- les refus prévus sont signalés ;
- les événements sont consultables et horodatés ;
- la récupération se déroule conformément à la documentation ;
- les résultats sont archivés.

Il faut distinguer les attentes de conception des observations réelles. Un test ne doit pas être déclaré réussi uniquement parce que son résultat semble plausible.

## 15.2 Sécurité des essais

Les tests électriques doivent suivre les procédures prévues par le fabricant et être réalisés dans un environnement adapté. Ne provoque pas de court-circuit et n'applique jamais une tension non prévue afin de vérifier la réaction du switch.

Toute intervention susceptible d'interrompre un service critique doit faire l'objet d'une évaluation de risque et d'une autorisation appropriée.


# 16. Runbook expert : incident PoE sur un équipement critique

## Étape 1 — Définir le périmètre

Identifier le service affecté, le PD, le switch, le port, l'heure de début et le nombre d'équipements touchés.

Un incident isolé sur un seul port ne nécessite pas forcément les mêmes hypothèses qu'une perte simultanée de plusieurs appareils.

## Étape 2 — Collecter les états et les mesures

Collecter les données réellement disponibles :
- statut Ethernet ;
- statut PoE ;
- classe ou allocation ;
- réservations et budget utilisable ;
- consommation mesurée ;
- événements du port ;
- état des alimentations ;
- changements de configuration récents.

La commande exacte dépend de la plate-forme. Il faut suivre la documentation de sa version logicielle.

## Étape 3 — Construire des hypothèses

Exemples :
- câble ou terminaison défectueux ;
- incompatibilité PSE/PD ;
- capacité de port insuffisante ;
- budget global ou politique d'allocation ;
- défaut du PD ;
- alimentation du châssis ;
- changement de configuration.

Associer chaque hypothèse à une vérification qui permet de l'appuyer ou de l'écarter.

## Étape 4 — Réaliser un test contrôlé

Privilégier les essais réversibles et les changements documentés. Ne pas contourner une limite de puissance tant que la cause n'est pas établie.

Sur une installation de production, évaluer le risque d'interruption avant toute remise à zéro ou réactivation d'un port critique.

## Étape 5 — Corriger et valider

Après identification d'une cause suffisamment étayée :
- appliquer la correction prévue ;
- vérifier le statut PoE ;
- vérifier le lien Ethernet ;
- confirmer la fonction applicative du PD ;
- observer la stabilité du service ;
- comparer les données avant et après.

## Étape 6 — Documenter

Le dossier doit contenir :
- le symptôme ;
- les faits observés ;
- les hypothèses testées ;
- la cause déterminée ou les incertitudes ;
- la correction ;
- les résultats de validation ;
- les actions préventives.

Un incident ne doit pas être considéré comme définitivement résolu uniquement parce qu'un voyant est revenu à son état normal.


# 17. Études de cas expertes

## Cas 1 — Budget global suffisant, port refusé

Un switch dispose d'une marge globale. Pourtant, une caméra ne s'allume pas sur le port prévu.

**Analyse :** examiner la capacité individuelle du port, le standard du PD, l'allocation, la politique de puissance et les motifs de refus. Le budget global est une condition nécessaire mais pas suffisante.

## Cas 2 — Plusieurs points d'accès tombent simultanément

Des points d'accès cessent de fonctionner à des heures proches.

**Analyse :** corréler les événements horodatés et examiner la capacité, les réservations, les alimentations et les journaux. Ne pas conclure que le trafic réseau a provoqué une panne électrique sans preuve.

## Cas 3 — Migration vers un switch de même taille

Le nouveau switch possède autant de ports que l'ancien, mais certains PD ne démarrent plus.

**Analyse :** comparer les capacités d'alimentation, les limites par port, les types pris en charge, les politiques et les paramètres. Le nombre de ports n'établit pas une équivalence électrique.

## Cas 4 — Redondance supposée, service perdu

Plusieurs switches existent, mais un équipement perd son alimentation lors d'une panne.

**Analyse :** déterminer le chemin réel de l'énergie et la configuration électrique du PD. La redondance des données et la redondance de l'alimentation doivent être évaluées séparément.


# 18. Exercices experts avec corrigés

## Exercice 1 — Calcul de capacité

Budget utilisable : 500 W. Réservations existantes : 342 W. Nouvelle demande : 65 W.

Marge initiale :

`500 − 342 = 158 W`

Marge théorique après la demande :

`158 − 65 = 93 W`

La marge semble suffisante au niveau global, mais l'admission doit encore respecter les capacités du port, la compatibilité et les politiques.

## Exercice 2 — Écart entre réservation et mesure

Un port réserve 30 W et consomme 9 W au moment de l'observation.

Peut-on attribuer automatiquement les 21 W de différence à un autre PD ?

**Corrigé :** non. La consommation mesurée ne modifie pas automatiquement l'allocation. Il faut comprendre la politique du contrôleur et le mécanisme utilisé.

## Exercice 3 — Incident commun

Quatre PD cessent de fonctionner dans la même minute.

**Corrigé :** établir la chronologie, examiner l'alimentation du châssis, les réservations et les événements PoE, puis comparer les ports affectés. Chercher une cause commune avant de traiter les ports comme des incidents indépendants.

## Exercice 4 — Test de résilience

Une infrastructure doit maintenir le service après la perte d'une alimentation redondante.

**Corrigé :** connaître la capacité nominale et dégradée, identifier les PD critiques, établir les critères de réussite, mesurer le budget et les statuts pendant le test, puis consigner la récupération. Le test doit suivre une procédure approuvée.


# 19. Liste de contrôle de conception

## Compatibilité
- [ ] Standards et types PoE des PSE documentés.
- [ ] Besoins des PD confirmés sur leurs fiches techniques.
- [ ] Limites individuelles des ports vérifiées.
- [ ] Négociations complémentaires documentées lorsqu'elles sont utilisées.

## Capacité
- [ ] Budget utilisable calculé.
- [ ] Réservations existantes inventoriées.
- [ ] Marge justifiée par le scénario.
- [ ] Capacité en mode dégradé évaluée.
- [ ] Priorités des PD critiques définies.

## Câblage
- [ ] Type de câble et longueurs conformes.
- [ ] Terminaisons et connecteurs inspectés.
- [ ] Conditions thermiques et méthodes de pose vérifiées.
- [ ] La conformité électrique n'est pas déduite du seul état Ethernet.

## Exploitation
- [ ] Statuts Ethernet et PoE surveillés séparément.
- [ ] Réservations et mesures différenciées.
- [ ] Événements et refus d'admission collectés.
- [ ] Horodatages cohérents.
- [ ] Procédure d'incident documentée.

## Validation
- [ ] Plan de tests approuvé.
- [ ] Admission des PD prévue testée.
- [ ] Scénarios de capacité évalués dans un environnement contrôlé.
- [ ] Comportement de récupération vérifié.
- [ ] Résultats archivés.


# 20. Glossaire expert

| Terme | Définition |
|---|---|
| PSE | Équipement qui fournit l'énergie PoE |
| PD | Équipement qui reçoit cette énergie |
| Type PoE | Niveau de capacité défini par le standard |
| Classe | Classification liée au niveau de puissance |
| Budget utilisable | Capacité disponible dans l'état réel du système |
| Réservation | Capacité attribuée ou retenue par le contrôleur |
| Consommation mesurée | Puissance observée à un instant ou sur une période |
| LLDP | Protocole de découverte de voisins de couche 2, pouvant participer aux échanges de puissance entre équipements compatibles |
| AutoClass | Fonction 802.3bt permettant, lorsque le matériel la prend en charge, d'affiner l'allocation à partir d'une mesure réalisée dans les conditions prévues |
| Mode dégradé | État suivant la perte ou l'indisponibilité d'une partie de la capacité |
| Observabilité | Capacité à expliquer l'état d'un système à partir des mesures, événements et contexte |
| Admission | Décision du PSE d'accorder ou de refuser une demande d'alimentation |
| Marge d'ingénierie | Capacité conservée pour répondre aux exigences de continuité et aux incertitudes du dimensionnement |


# 21. Références techniques

- [Ethernet Alliance — Vue d'ensemble d'IEEE 802.3bt](https://ethernetalliance.org/wp-content/uploads/2018/04/WP_EA_Overview8023bt_FINAL.pdf)
- [Ethernet Alliance — Types, classes et puissances disponibles au PD](https://ethernetalliance.org/wp-content/uploads/2020/02/EthernetAlliance_Gen2PoECertProgram_techbrief-FINAL-19DEC19.pdf)
- [Cisco — Dépannage du PoE](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst3750/software/troubleshooting/g_power_over_ethernet.html)
- [Cisco — Dépannage PoE sur Catalyst 9000](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9200-series-switches/215636-troubleshooting-power-over-ethernet-poe.html)

Pour un déploiement réel, la documentation du modèle exact de PSE, de PD et du logiciel utilisé reste prioritaire pour confirmer les capacités et les procédures.