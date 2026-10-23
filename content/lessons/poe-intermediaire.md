# PoE — Intermédiaire
## Standards, classification, dimensionnement et dépannage

**Niveau :** Intermédiaire  
**Prérequis :** connaître les principes PSE/PD, les principaux types PoE et le fonctionnement général d'un switch administrable.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :
- comparer les niveaux de puissance des principaux types IEEE PoE ;
- distinguer détection, classification, négociation et admission ;
- expliquer l'utilisation de LLDP dans certaines implémentations ;
- calculer une marge de budget à partir de réservations ;
- distinguer la puissance réservée de la consommation mesurée ;
- dépanner méthodiquement un refus d'alimentation ;
- établir un rapport à partir de mesures et d'événements observés.

---

# 1. Pourquoi le dimensionnement PoE exige-t-il plus qu'une simple addition ?

Au niveau débutant, le PoE se comprend comme le transport d'énergie et de données à travers une liaison Ethernet compatible. En exploitation, il faut déterminer si un ensemble de ports peut alimenter simultanément tous les PD attendus.

Un réseau d'entreprise peut comporter des téléphones IP, des caméras, des points d'accès et des équipements industriels. Leurs besoins de puissance diffèrent selon les modèles, leurs fonctions et leur état de fonctionnement.

Un switch peut avoir suffisamment de ports libres tout en manquant de puissance. Il peut aussi disposer d'un budget global suffisant, mais ne pas posséder un port capable de délivrer la puissance requise par un appareil particulier.

L'administration doit donc considérer trois dimensions :
1. la compatibilité électrique de chaque liaison ;
2. la capacité individuelle des ports ;
3. le budget global réellement utilisable.

Il faut également connaître la politique d'admission du switch : le comportement en cas de budget insuffisant varie selon les matériels et leur configuration.

---

# 2. Les standards PoE et leurs limites de puissance

Les familles IEEE couramment rencontrées sont présentées ci-dessous.

| Standard | Type | Puissance maximale de référence côté PSE | Puissance de référence disponible côté PD |
|---|---:|---:|---:|
| IEEE 802.3af | Type 1 | 15,4 W | 12,95 W |
| IEEE 802.3at | Type 2 | 30 W | 25,5 W |
| IEEE 802.3bt | Type 3 | Jusqu'à 60 W | Jusqu'à 51 W |
| IEEE 802.3bt | Type 4 | Jusqu'à 90 W | Jusqu'à 71,3 W |

Les chiffres permettent de comparer les capacités de référence. Le type et la classe exacts, la compatibilité du couple PSE/PD, le câble et les règles du matériel déterminent les conditions réelles.

## 2.1 Puissance côté PSE et côté PD

Le PSE délivre la puissance à l'origine de la liaison. La puissance disponible au PD est affectée par les pertes électriques dans le câble.

Les pertes augmentent avec la résistance du trajet électrique et dépendent de plusieurs paramètres, dont les conducteurs, les terminaisons et les conditions d'installation.

Il ne faut donc pas assimiler la puissance annoncée côté PSE à la puissance garantie à l'entrée du PD.

Pour dimensionner une installation, utilise les limites prévues par la norme, les caractéristiques des appareils et les recommandations de câblage du projet. Évite d'appliquer arbitrairement un pourcentage de perte universel à tous les liens.

## 2.2 Type et classe

Le **type PoE** décrit une famille de capacités définies par le standard. La **classe** caractérise un niveau de puissance suivant le mécanisme de classification applicable.

Ces notions ne doivent pas être confondues avec :
- la consommation instantanée du PD ;
- la réservation appliquée par le contrôleur ;
- le nom commercial utilisé par le fabricant.

Une mention commerciale telle que « PoE++ » ne remplace pas la lecture de la fiche technique. Vérifie toujours la norme, le type ou la classe, les limites par port et la capacité globale de l'appareil.

## 2.3 Alimentation sur deux paires et quatre paires

Les premières générations PoE ont utilisé deux paires pour transférer l'énergie. IEEE 802.3bt permet des niveaux de puissance plus élevés et une alimentation utilisant les quatre paires, suivant le type et la classe.

Pour une installation à puissance élevée, la qualité des conducteurs et des terminaisons, les méthodes de pose, les faisceaux de câbles et les conditions thermiques doivent être examinés.

Un câble qui permet une liaison Ethernet n'est pas automatiquement une preuve de conformité pour tous les profils PoE.

---

# 3. Schéma animé — Comparaison des puissances

L'échelle est commune aux quatre barres. La longueur de chaque barre est proportionnelle à la puissance de référence côté PSE.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 330" role="img" aria-labelledby="poei1-title">
  <title id="poei1-title">Comparaison des puissances maximales PoE côté PSE</title>
  <defs>
    <style>
      .poei1-bg{fill:#101827}
      .poei1-title{fill:#f8fafc;font:700 19px Arial,sans-serif}
      .poei1-label{fill:#e5edf8;font:700 14px Arial,sans-serif}
      .poei1-sub{fill:#a7bad2;font:12px Arial,sans-serif}
      .poei1-track{fill:#26364d}
      .poei1-b1{fill:#60a5fa}
      .poei1-b2{fill:#46c9ba}
      .poei1-b3{fill:#aa96ff}
      .poei1-b4{fill:#f5bb64}
      .poei1-grid{stroke:#40516b;stroke-width:1;stroke-dasharray:3 6}
      .poei1-tick{fill:#b3c3d8;font:11px Arial,sans-serif}
    </style>
  </defs>
  <rect class="poei1-bg" width="920" height="330" rx="16"/>
  <text class="poei1-title" x="30" y="34">Puissance maximale de référence côté PSE</text>
  <text class="poei1-sub" x="30" y="55">Une échelle commune permet de comparer les quatre niveaux.</text>
  <g>
    <line class="poei1-grid" x1="250" y1="72" x2="250" y2="264"/>
    <line class="poei1-grid" x1="433.3" y1="72" x2="433.3" y2="264"/>
    <line class="poei1-grid" x1="616.7" y1="72" x2="616.7" y2="264"/>
    <line class="poei1-grid" x1="800" y1="72" x2="800" y2="264"/>
  </g>
  <g>
    <text class="poei1-label" x="30" y="99">Type 1</text>
    <text class="poei1-sub" x="30" y="117">IEEE 802.3af</text>
    <rect class="poei1-track" x="250" y="84" width="550" height="26" rx="5"/>
    <rect class="poei1-b1" x="250" y="84" width="0" height="26" rx="5">
      <animate attributeName="width" from="0" to="94.1" dur="1.1s" begin="0.1s" fill="freeze"/>
    </rect>
    <text class="poei1-label" x="820" y="102">15,4 W</text>
    <text class="poei1-label" x="30" y="146">Type 2</text>
    <text class="poei1-sub" x="30" y="164">IEEE 802.3at</text>
    <rect class="poei1-track" x="250" y="131" width="550" height="26" rx="5"/>
    <rect class="poei1-b2" x="250" y="131" width="0" height="26" rx="5">
      <animate attributeName="width" from="0" to="183.3" dur="1.1s" begin="0.35s" fill="freeze"/>
    </rect>
    <text class="poei1-label" x="820" y="149">30 W</text>
    <text class="poei1-label" x="30" y="193">Type 3</text>
    <text class="poei1-sub" x="30" y="211">IEEE 802.3bt</text>
    <rect class="poei1-track" x="250" y="178" width="550" height="26" rx="5"/>
    <rect class="poei1-b3" x="250" y="178" width="0" height="26" rx="5">
      <animate attributeName="width" from="0" to="366.7" dur="1.1s" begin="0.6s" fill="freeze"/>
    </rect>
    <text class="poei1-label" x="820" y="196">60 W</text>
    <text class="poei1-label" x="30" y="240">Type 4</text>
    <text class="poei1-sub" x="30" y="258">IEEE 802.3bt</text>
    <rect class="poei1-track" x="250" y="225" width="550" height="26" rx="5"/>
    <rect class="poei1-b4" x="250" y="225" width="0" height="26" rx="5">
      <animate attributeName="width" from="0" to="550" dur="1.1s" begin="0.85s" fill="freeze"/>
    </rect>
    <text class="poei1-label" x="820" y="243">90 W</text>
  </g>
  <g class="poei1-tick">
    <text x="250" y="281" text-anchor="middle">0 W</text>
    <text x="433.3" y="281" text-anchor="middle">30 W</text>
    <text x="616.7" y="281" text-anchor="middle">60 W</text>
    <text x="800" y="281" text-anchor="middle">90 W</text>
  </g>
  <path d="M30 294 H890" stroke="#34465f"/>
  <text class="poei1-sub" x="30" y="313">Repères côté PSE. La puissance garantie au PD est inférieure en raison des pertes et dépend du type exact.</text>
</svg>

---

# 4. Détection, classification, LLDP et admission

Un PSE doit reconnaître un PD compatible avant de procéder à l'alimentation normale. La classification permet d'établir le niveau de puissance pertinent pour la gestion de l'énergie.

Selon les capacités des équipements, d'autres échanges peuvent contribuer à préciser les besoins. LLDP est un protocole de découverte de voisins de couche 2 qui peut participer à des échanges d'informations de puissance sur les matériels compatibles.

Il faut séparer quatre opérations :

1. **Détection électrique :** vérifier la signature attendue d'un PD.
2. **Classification :** déterminer la classe de puissance selon le mécanisme applicable.
3. **Négociation complémentaire :** utiliser les échanges pris en charge, notamment LLDP lorsque cela s'applique.
4. **Admission :** vérifier les limites du port, la capacité du système et les règles d'allocation.

LLDP ne remplace pas automatiquement la détection électrique et n'autorise pas à dépasser les capacités du PSE ou du PD.

## 4.1 Pourquoi le switch peut-il réserver plus que la consommation mesurée ?

Le contrôleur de puissance ne doit pas nécessairement utiliser la consommation instantanée comme unique base de décision. Le PD peut consommer davantage dans certaines conditions, et une classe ou une politique d'allocation peut imposer de conserver une certaine capacité disponible.

La réservation représente la capacité retenue par le contrôleur. La consommation représente la puissance mesurée à un instant ou sur une période.

Ces informations servent à des fins différentes. Une consommation de 9 W ne signifie pas automatiquement que le contrôleur peut libérer le reste de la réservation.

## 4.2 Schéma animé — Processus d'admission

Ce schéma sépare les étapes et montre explicitement les résultats possibles : alimentation autorisée ou demande refusée.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 370" role="img" aria-labelledby="poei2-title">
  <title id="poei2-title">Séquence d'admission de puissance PoE</title>
  <defs>
    <marker id="poei2-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0 0 L6 3 L0 6 Z" fill="#69c9d9"/>
    </marker>
    <style>
      .poei2-bg{fill:#101827}
      .poei2-card{fill:#1b2b42;stroke:#526985;stroke-width:1.5}
      .poei2-head{fill:#f8fafc;font:700 14px Arial,sans-serif}
      .poei2-txt{fill:#cedbeb;font:12px Arial,sans-serif}
      .poei2-note{fill:#9eb1c8;font:11px Arial,sans-serif}
      .poei2-flow{fill:none;stroke:#69c9d9;stroke-width:2.7;stroke-dasharray:7 7;marker-end:url(#poei2-arrow);animation:poei2-dash 1s linear infinite}
      .poei2-yes{fill:#153a35;stroke:#46c9a4;stroke-width:1.5}
      .poei2-no{fill:#3a2b20;stroke:#edb866;stroke-width:1.5}
      @keyframes poei2-dash{to{stroke-dashoffset:-28}}
      @media(prefers-reduced-motion:reduce){.poei2-flow{animation:none}}
    </style>
  </defs>
  <rect class="poei2-bg" width="920" height="370" rx="16"/>
  <text class="poei2-head" x="30" y="32" font-size="19">Comment le PSE décide-t-il d'alimenter un PD ?</text>
  <text class="poei2-note" x="30" y="51">Le processus exact dépend du standard, du contrôleur et des capacités des appareils.</text>
  <g>
    <rect class="poei2-card" x="25" y="78" width="200" height="112" rx="10"/>
    <circle cx="48" cy="101" r="12" fill="#315276"/>
    <text x="48" y="105" text-anchor="middle" fill="#fff" font-size="11" font-weight="700">1</text>
    <text class="poei2-head" x="125" y="105" text-anchor="middle">Détection</text>
    <text class="poei2-txt" x="125" y="132" text-anchor="middle">Signature électrique</text>
    <text class="poei2-txt" x="125" y="149" text-anchor="middle">d'un PD compatible</text>
    <text class="poei2-note" x="125" y="173" text-anchor="middle">Pas de détection valide :</text>
    <text class="poei2-note" x="125" y="185" text-anchor="middle">pas d'alimentation normale.</text>
    <rect class="poei2-card" x="245" y="78" width="200" height="112" rx="10"/>
    <circle cx="268" cy="101" r="12" fill="#315276"/>
    <text x="268" y="105" text-anchor="middle" fill="#fff" font-size="11" font-weight="700">2</text>
    <text class="poei2-head" x="345" y="105" text-anchor="middle">Classification</text>
    <text class="poei2-txt" x="345" y="132" text-anchor="middle">Niveau de puissance</text>
    <text class="poei2-txt" x="345" y="149" text-anchor="middle">et capacités reconnues</text>
    <text class="poei2-note" x="345" y="173" text-anchor="middle">Type et classe déterminent</text>
    <text class="poei2-note" x="345" y="185" text-anchor="middle">les mécanismes applicables.</text>
    <rect class="poei2-card" x="465" y="78" width="200" height="112" rx="10"/>
    <circle cx="488" cy="101" r="12" fill="#315276"/>
    <text x="488" y="105" text-anchor="middle" fill="#fff" font-size="11" font-weight="700">3</text>
    <text class="poei2-head" x="565" y="105" text-anchor="middle">Budget et port</text>
    <text class="poei2-txt" x="565" y="132" text-anchor="middle">Limite individuelle</text>
    <text class="poei2-txt" x="565" y="149" text-anchor="middle">et capacité disponible</text>
    <text class="poei2-note" x="565" y="173" text-anchor="middle">LLDP peut préciser la demande</text>
    <text class="poei2-note" x="565" y="185" text-anchor="middle">sur matériel compatible.</text>
    <rect class="poei2-card" x="685" y="78" width="210" height="112" rx="10"/>
    <circle cx="708" cy="101" r="12" fill="#315276"/>
    <text x="708" y="105" text-anchor="middle" fill="#fff" font-size="11" font-weight="700">4</text>
    <text class="poei2-head" x="790" y="105" text-anchor="middle">Décision</text>
    <text class="poei2-txt" x="790" y="132" text-anchor="middle">Application des règles</text>
    <text class="poei2-txt" x="790" y="149" text-anchor="middle">et de la priorité</text>
    <text class="poei2-note" x="790" y="173" text-anchor="middle">Autoriser ou refuser</text>
    <text class="poei2-note" x="790" y="185" text-anchor="middle">la demande de puissance.</text>
  </g>
  <path class="poei2-flow" d="M225 132 H245"/>
  <path class="poei2-flow" d="M445 132 H465"/>
  <path class="poei2-flow" d="M665 132 H685"/>
  <path class="poei2-flow" d="M790 190 V218 H600 V245"/>
  <path class="poei2-flow" d="M790 218 V245"/>
  <text x="600" y="237" text-anchor="middle" fill="#8fe4c7" font-size="11" font-weight="700">ACCEPTÉE</text>
  <text x="810" y="237" text-anchor="middle" fill="#ffd28a" font-size="11" font-weight="700">REFUSÉE</text>
  <rect class="poei2-yes" x="485" y="245" width="230" height="65" rx="10"/>
  <text class="poei2-head" x="600" y="270" text-anchor="middle">Réserver et alimenter</text>
  <text class="poei2-txt" x="600" y="290" text-anchor="middle">Surveiller l'état du port</text>
  <rect class="poei2-no" x="730" y="245" width="165" height="65" rx="10"/>
  <text class="poei2-head" x="812" y="270" text-anchor="middle">Ne pas alimenter</text>
  <text class="poei2-txt" x="812" y="290" text-anchor="middle">Examiner les motifs</text>
  <text class="poei2-note" x="30" y="340">Un budget global positif ne garantit pas à lui seul l'admissibilité d'un port.</text>
</svg>

---

# 5. Calculer le budget PoE

Le budget global est une contrainte collective. Il dépend de l'alimentation du châssis, de son architecture et de la configuration de puissance.

## 5.1 Formule de base

Une première estimation peut être effectuée ainsi :

`Marge théorique = Budget PoE utilisable − Somme des réservations existantes`

Puis :

`Marge après demande = Marge théorique − Nouvelle puissance à réserver`

Cette méthode est utile pour comprendre la capacité restante, mais elle ne remplace pas la décision d'admission du PSE.

Le budget utilisable doit refléter la capacité réelle dans l'état matériel considéré. Il faut tenir compte, lorsque c'est pertinent, de la redondance de l'alimentation, des priorités et des réserves retenues pour les services critiques.

## 5.2 Exemple guidé

On dispose des données suivantes :

| Paramètre | Valeur |
|---|---:|
| Budget PoE utilisable | 240 W |
| Réservations existantes | 165 W |
| Nouvelle demande | 45 W |

La marge théorique initiale est :

`240 − 165 = 75 W`

Après la nouvelle demande :

`75 − 45 = 30 W`

La demande semble compatible avec le budget global. Il reste à vérifier la capacité individuelle du port, les capacités du PD et les règles d'admission.

## 5.3 Les erreurs de calcul fréquentes

**Utiliser le budget nominal plutôt que le budget utilisable.** La capacité réellement distribuable peut être inférieure selon l'état de l'alimentation et la politique du système.

**Additionner les puissances maximales des ports sans vérifier le budget global.** Les limites individuelles ne garantissent pas que tous les ports peuvent fonctionner simultanément à leur maximum.

**Soustraire la consommation instantanée au lieu des réservations.** Ce calcul peut surestimer la capacité disponible si le contrôleur conserve les réservations existantes.

**Ignorer la priorité des ports.** Le traitement d'une demande lorsque le budget est insuffisant dépend des règles du matériel.

**Oublier le scénario de panne.** Une alimentation redondante indisponible peut réduire la capacité utilisable.

## 5.4 Schéma animé — Répartition d'un budget de 240 W

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 340" role="img" aria-labelledby="poei3-title">
  <title id="poei3-title">Répartition d'un budget PoE de 240 watts</title>
  <defs>
    <style>
      .poei3-bg{fill:#101827}
      .poei3-head{fill:#f8fafc;font:700 18px Arial,sans-serif}
      .poei3-txt{fill:#d3dfef;font:13px Arial,sans-serif}
      .poei3-note{fill:#9fb2ca;font:11px Arial,sans-serif}
      .poei3-track{fill:#28374d}
      .poei3-reserved{fill:#5d99f5}
      .poei3-new{fill:#42c5a0}
      .poei3-free{fill:#61718a}
      .poei3-outline{fill:none;stroke:#e9f2ff;stroke-width:1.5;stroke-dasharray:5 5}
    </style>
  </defs>
  <rect class="poei3-bg" width="920" height="340" rx="16"/>
  <text class="poei3-head" x="30" y="34">Admission d'un PD : exemple de calcul</text>
  <text class="poei3-note" x="30" y="54">Budget utilisable : 240 W · réservations existantes : 165 W · nouvelle demande : 45 W</text>
  <text class="poei3-txt" x="40" y="91">Répartition du budget</text>
  <rect class="poei3-track" x="40" y="105" width="840" height="50" rx="7"/>
  <rect class="poei3-reserved" x="40" y="105" width="0" height="50" rx="6">
    <animate attributeName="width" from="0" to="577.5" dur="1.2s" begin="0.1s" fill="freeze"/>
  </rect>
  <rect class="poei3-new" x="617.5" y="105" width="0" height="50">
    <animate attributeName="width" from="0" to="157.5" dur="0.8s" begin="1.1s" fill="freeze"/>
  </rect>
  <rect class="poei3-free" x="775" y="105" width="0" height="50">
    <animate attributeName="width" from="0" to="105" dur="0.8s" begin="1.8s" fill="freeze"/>
  </rect>
  <rect class="poei3-outline" x="617.5" y="105" width="157.5" height="50" rx="4"/>
  <text x="328" y="135" fill="#fff" font-size="14" font-weight="700" text-anchor="middle">165 W réservés</text>
  <text x="696" y="135" fill="#072b26" font-size="13" font-weight="700" text-anchor="middle">45 W</text>
  <text x="827" y="135" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">30 W</text>
  <g>
    <rect x="40" y="188" width="260" height="87" rx="10" fill="#192d47" stroke="#5d99f5"/>
    <text class="poei3-txt" x="170" y="213" text-anchor="middle" font-weight="700">Marge initiale</text>
    <text class="poei3-head" x="170" y="240" text-anchor="middle">240 − 165 = 75 W</text>
    <text class="poei3-note" x="170" y="260" text-anchor="middle">Avant la nouvelle demande</text>
    <rect x="330" y="188" width="260" height="87" rx="10" fill="#15332f" stroke="#42c5a0"/>
    <text class="poei3-txt" x="460" y="213" text-anchor="middle" font-weight="700">Marge après demande</text>
    <text class="poei3-head" x="460" y="240" text-anchor="middle">75 − 45 = 30 W</text>
    <text class="poei3-note" x="460" y="260" text-anchor="middle">Capacité théorique restante</text>
    <rect x="620" y="188" width="260" height="87" rx="10" fill="#36291c" stroke="#edb866"/>
    <text class="poei3-txt" x="750" y="213" text-anchor="middle" font-weight="700">Contrôles complémentaires</text>
    <text class="poei3-txt" x="750" y="237" text-anchor="middle">Port, classe, priorité</text>
    <text class="poei3-note" x="750" y="260" text-anchor="middle">Le calcul seul ne suffit pas</text>
  </g>
  <text class="poei3-note" x="30" y="308">Les trois segments font 240 W au total. Les largeurs sont proportionnelles aux puissances affichées.</text>
  <text class="poei3-note" x="30" y="325">La barre représente des allocations, pas la consommation mesurée instantanément.</text>
</svg>

---

# 6. Dimensionner un parc PoE

Le dimensionnement doit partir des modèles d'équipements réellement prévus.

Pour chaque catégorie de PD, répertorier :
- le modèle et le standard PoE ;
- la puissance exigée ;
- les fonctions susceptibles d'augmenter la consommation ;
- le port ou type de port prévu ;
- les besoins de disponibilité ;
- la capacité électrique prévue pour le switch ;
- les marges et extensions futures.

## 6.1 Exemple : un étage de bureaux

Un étage comprend :
- 12 téléphones IP ;
- 6 points d'accès Wi-Fi ;
- 4 caméras IP.

Ce décompte ne suffit pas pour choisir un budget de 200 W, 300 W ou 500 W. Les équipements ont des besoins différents et les réservations du PSE peuvent dépendre de leur classe et des règles de l'équipement.

Il faut réunir les fiches techniques des modèles réellement utilisés, déterminer les allocations pertinentes et calculer le budget en fonction du mode d'exploitation attendu.

## 6.2 Prévoir les scénarios

Un bon dimensionnement compare au moins trois situations.

**Nominale :** les équipements fonctionnent dans le profil opérationnel attendu.

**Forte demande :** les appareils utilisent simultanément les fonctions qui demandent le plus de puissance.

**Dégradée :** une alimentation ou une partie de la capacité devient indisponible.

Dans un réseau critique, il faut déterminer quels services doivent rester disponibles en mode dégradé et vérifier que la capacité résiduelle répond à cette exigence.

Le pourcentage de réserve n'est pas universel. Il doit être justifié par les profils de charge, le niveau de redondance, les exigences de continuité et les règles de l'organisation.

---

# 7. Méthode de dépannage intermédiaire

Un diagnostic doit s'appuyer sur les observations du système. Il ne faut pas modifier plusieurs paramètres au hasard ni considérer un voyant comme une preuve suffisante.

La procédure générale est :

1. collecter l'état du port et du budget ;
2. observer les événements autour de l'incident ;
3. établir les hypothèses plausibles ;
4. réaliser des tests contrôlés ;
5. appliquer une correction documentée ;
6. confirmer la stabilité du service après correction.

## 7.1 Matrice de dépannage

| Symptôme | Causes possibles | Vérifications prioritaires |
|---|---|---|
| PD non détecté | Câble, compatibilité, port désactivé | État du port, câble connu comme fonctionnel, fiche technique |
| PD détecté mais refusé | Budget, classe, limite de port ou politique | Puissance réservée, budget global et journaux |
| PD démarre puis s'éteint | Profil de consommation, câble, défaut matériel | Événements horodatés et puissance disponible |
| Plusieurs PD sont touchés | Alimentation du switch, budget ou cause commune | État du châssis et journaux système |
| Lien Ethernet actif mais PD non opérationnel | Défaut d'alimentation ou de l'application | Statut PoE distinct du statut Ethernet |
| Consommation faible mais admission refusée | Réservations ou politique d'allocation | Capacité retenue par le contrôleur |
| Problème après remplacement d'un switch | Capacités ou configuration différentes | Comparer modèles, budgets, limites et paramètres |

## 7.2 Commandes et informations d'administration

Sur certaines plateformes Cisco, la commande suivante permet d'examiner l'état et les données PoE :

```text
show power inline
```

D'autres commandes peuvent aider à connaître l'état des interfaces et les journaux :

```text
show interfaces status
show logging
```

Ces commandes sont spécifiques à la famille d'équipements concernée. Il ne faut pas les exécuter sur un autre constructeur en supposant que la syntaxe sera identique.

Pour chaque incident, relever au minimum :
- le nom du switch et le port ;
- le modèle du PD ;
- le statut du lien Ethernet ;
- le statut PoE ;
- la classe ou l'allocation si disponible ;
- la consommation mesurée si disponible ;
- le budget utilisable et les réservations ;
- les événements horodatés ;
- les modifications de configuration récentes.

Les données que le matériel n'expose pas doivent être signalées comme non disponibles, et non remplacées par des valeurs supposées.

## 7.3 Pourquoi l'horodatage est essentiel

Les incidents doivent pouvoir être rapprochés des événements de l'infrastructure. Si plusieurs PD cessent de fonctionner pendant la même minute, la chronologie peut aider à identifier une perte commune d'alimentation, un changement de configuration ou une autre cause.

Sans horodatage cohérent, il devient beaucoup plus difficile de corréler les événements du switch aux alertes du système de supervision et aux observations du PD.

---

# 8. Travaux pratiques

## TP 1 — Inventaire et calcul du budget

1. inventorier les ports PoE actifs ;
2. identifier les PD et leurs modèles ;
3. relever les allocations disponibles dans le switch ;
4. calculer la marge théorique ;
5. contrôler les limites par port ;
6. identifier les risques en cas d'ajout d'un PD.

**Livrable :** tableau des ports, des PD, des allocations et de leurs états.

## TP 2 — Analyser un refus PoE

Dans un environnement de laboratoire :
1. relever l'état du port ;
2. relever les informations de puissance ;
3. examiner les journaux ;
4. former plusieurs hypothèses ;
5. effectuer les tests pertinents ;
6. documenter la cause établie ou préciser pourquoi les preuves sont insuffisantes.

Le but n'est pas seulement de rétablir le service : il faut expliquer pourquoi le défaut est survenu.

## TP 3 — Vérifier une migration

Après remplacement d'un switch :
1. comparer le budget PoE utilisable ;
2. comparer les limites par port ;
3. vérifier le standard attendu par les PD ;
4. contrôler les configurations de priorité ;
5. observer le comportement des PD les plus exigeants ;
6. archiver les résultats.

Deux switches possédant le même nombre de ports ne garantissent pas les mêmes capacités d'alimentation.

---

# 9. Étude de cas corrigée

Un switch possède un budget utilisable de 240 W. Les réservations totalisent 165 W. Un nouveau point d'accès nécessite une allocation de 45 W.

**Question 1 :** quelle est la marge initiale ?

`240 − 165 = 75 W`

**Question 2 :** quelle serait la marge après la demande ?

`75 − 45 = 30 W`

**Question 3 :** peut-on affirmer que le point d'accès fonctionnera ?

Non. Le budget global semble suffisant dans cet exemple, mais il faut vérifier le niveau PoE du point d'accès, la capacité du port, la négociation éventuelle, les priorités et les conditions du système.

**Question 4 :** pourquoi la mesure instantanée ne remplace-t-elle pas la réservation ?

Parce que la consommation peut varier et que le contrôleur peut retenir la puissance selon la classe ou sa politique.

**Question 5 :** que faire si l'admission est refusée malgré cette marge ?

Consulter les événements et le statut de puissance, puis contrôler les limites de port, la compatibilité et la configuration avant de modifier quoi que ce soit.

---

# 10. Évaluation intermédiaire

1. Quelle est la différence entre puissance PSE et puissance PD ?
2. Pourquoi la réservation peut-elle être supérieure à la consommation mesurée ?
3. Quel rôle LLDP peut-il jouer dans une implémentation PoE ?
4. Quelle différence existe-t-il entre la capacité individuelle d'un port et le budget global ?
5. Comment diagnostiquer un PD non alimenté alors que le lien Ethernet est actif ?
6. Quels sont les premiers éléments à collecter lors d'un incident PoE ?
7. Pourquoi faut-il examiner l'état des alimentations lors d'une panne touchant plusieurs ports ?
8. Pourquoi ne faut-il pas augmenter arbitrairement une limite de puissance ?

## Corrigé

1. Une partie de la puissance est dissipée dans la liaison et la puissance disponible côté PD est affectée par les pertes.
2. Le PSE peut réserver une puissance en fonction de la classe ou de sa politique, même si l'appareil consomme moins au moment de la mesure.
3. LLDP peut participer à des échanges de puissance entre équipements compatibles, sans remplacer les mécanismes électriques de détection.
4. La limite du port est locale ; le budget global représente une capacité partagée.
5. Examiner séparément le statut PoE, le budget, les journaux, le câble et la compatibilité du PD.
6. Le port, le PD, l'état Ethernet, l'état PoE, la puissance disponible, les réservations et les événements.
7. Une perte de capacité commune peut affecter plusieurs ports simultanément.
8. Il faut vérifier les capacités réelles du PSE, du PD et du câblage avant d'appliquer une modification.

---

# 11. Références techniques

- [Ethernet Alliance — Présentation IEEE 802.3bt](https://ethernetalliance.org/wp-content/uploads/2018/04/WP_EA_Overview8023bt_FINAL.pdf)
- [Cisco — Dépannage du PoE](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst3750/software/troubleshooting/g_power_over_ethernet.html)
- [Microchip — Types et standards PoE](https://developerhelp.microchip.com/xwiki/bin/view/applications/ethernet/poe/standards/)

Toujours consulter les documents correspondant au modèle exact du matériel et à sa version logicielle.