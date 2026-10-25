# PoE — Intermédiaire
## Standards, classification, budget, administration et dépannage

**Niveau :** Intermédiaire  
**Prérequis :** notions PSE/PD, Ethernet, puissance électrique et premiers diagnostics d’un switch.  
**Objectif :** administrer un déploiement PoE, comprendre ses limites, anticiper les refus d’alimentation et construire une méthode de dépannage reproductible.


# 1. Passer de la compréhension à l’administration

Au niveau débutant, le PoE est présenté comme une manière de transporter énergie et données par un même câble compatible. L’administration d’un réseau impose d’aller plus loin : il faut connaître les capacités réelles du PSE, les besoins du PD, les mécanismes de classification, les réservations et la politique du contrôleur de puissance.

Un parc de téléphones IP ne se dimensionne pas nécessairement de la même façon qu’un parc de caméras motorisées ou de points d’accès Wi-Fi de forte puissance. Même si ces appareils possèdent des connecteurs identiques, ils peuvent avoir des besoins et des comportements différents.

Pour chaque équipement alimenté, il faut pouvoir répondre à cinq questions :

1. Quel standard PoE et quel niveau de puissance le PD prend-il en charge ?
2. Le port PSE peut-il fournir ce niveau de puissance ?
3. Le switch possède-t-il assez de budget pour l’ensemble des équipements ?
4. Quel mécanisme détermine ou négocie la puissance réservée ?
5. Comment le switch signale-t-il un refus, un défaut ou une perte d’alimentation ?

L’objectif de ce cours est d'apporter une réponse méthodique à ces questions, sans dépendre des conventions d’un seul constructeur.


# 2. Types PoE et puissance réellement disponible

Les principales familles IEEE PoE sont les suivantes :

| Norme | Type PoE | Maximum de référence côté PSE | Maximum de référence disponible côté PD |
|---|---|---:|---:|
| IEEE 802.3af | Type 1 | 15,4 W | 12,95 W |
| IEEE 802.3at | Type 2 | 30 W | 25,5 W |
| IEEE 802.3bt | Type 3 | jusqu’à 60 W | jusqu’à 51 W |
| IEEE 802.3bt | Type 4 | jusqu’à 90 W | jusqu’à 71,3 W |

Les valeurs présentées sont les plafonds couramment utilisés pour comparer les types concernés. La classe exacte, le type de PD, les pertes électriques et les capacités des équipements déterminent les conditions applicables au produit réel.

## 2.1 Pourquoi distinguer puissance PSE et puissance PD ?

Le PSE est la source d’énergie de la liaison. Le PD est le récepteur. Entre les deux, le courant traverse des conducteurs présentant une résistance électrique.

Cette résistance provoque des pertes. Une partie de l’énergie est transformée en chaleur dans le câblage. La puissance qui arrive au PD est donc susceptible d’être inférieure à la puissance délivrée par le PSE.

La différence devient importante quand :
- la distance de câblage augmente ;
- la puissance demandée est élevée ;
- le câble ou ses terminaisons ne répondent pas aux exigences de conception ;
- plusieurs câbles regroupés provoquent des conditions thermiques moins favorables ;
- le PD utilise des fonctions qui entraînent une consommation importante.

Il ne faut pas appliquer un pourcentage arbitraire à tous les projets pour représenter ces pertes. Le dimensionnement doit utiliser les limites et les hypothèses prévues par le standard, les caractéristiques du câble et les informations du fabricant.

## 2.2 La compatibilité n’est pas synonyme de puissance identique

Deux appareils peuvent être compatibles au sens de l’interopérabilité sans offrir la même puissance maximale.

Un PD de puissance élevée connecté à un PSE de capacité inférieure ne reçoit pas automatiquement toute la puissance de son profil maximal. Selon les capacités du système, l’appareil peut fonctionner à puissance réduite, être limité ou ne pas démarrer dans certaines conditions.

Il faut donc vérifier l’ensemble des éléments :
- standard côté PSE ;
- standard et classe côté PD ;
- puissance disponible et puissance requise ;
- limites du port ;
- capacité globale du switch ;
- éventuelles extensions propriétaires.

Les termes commerciaux comme « PoE+ », « PoE++ », « High PoE » ou des désignations équivalentes ne suffisent pas toujours à identifier le niveau exact de conformité. La fiche technique détaillée est indispensable.

## 2.3 Alimentation sur deux paires ou quatre paires

Les premières générations de PoE normalisé utilisent deux paires du câblage pour le transfert d’énergie. IEEE 802.3bt permet des niveaux de puissance plus élevés, avec une alimentation possible sur quatre paires selon le type et la classe.

Cette distinction doit être prise en compte dans la conception, la qualité du câblage, les terminaisons et la compatibilité. Il ne suffit pas de compter les fils présents dans une gaine : les conducteurs et le câblage complet doivent être conformes aux exigences du lien.

Pour les types de puissance élevée, il faut aussi prendre en considération l’échauffement dans les faisceaux de câbles, les pratiques de pose et les recommandations du câblage retenu.

## 2.4 Schéma animé — Comparer les types PoE

Ce graphique compare les plafonds de puissance de référence côté PSE. Il ne représente pas la consommation réelle d’un appareil.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 340" role="img" aria-labelledby="poei1-title">
<title id="poei1-title">Comparaison animée des puissances PoE par type</title>
<defs><style>
.poei1-bg{fill:#101827}.poei1-h{fill:#f8fafc;font:700 17px Arial,sans-serif}.poei1-t{fill:#d1dbea;font:12px Arial,sans-serif}.poei1-sub{fill:#9eb1c9;font:11px Arial,sans-serif}.poei1-track{fill:#24354d}.poei1-fill1{fill:#60a5fa;transform-box:fill-box;transform-origin:left center;animation:poei1-grow 1.6s ease-out both}.poei1-fill2{fill:#53d5c1;transform-box:fill-box;transform-origin:left center;animation:poei1-grow 1.6s ease-out both;animation-delay:.25s}.poei1-fill3{fill:#b6a0ff;transform-box:fill-box;transform-origin:left center;animation:poei1-grow 1.6s ease-out both;animation-delay:.5s}.poei1-fill4{fill:#ffc56b;transform-box:fill-box;transform-origin:left center;animation:poei1-grow 1.6s ease-out both;animation-delay:.75s}@keyframes poei1-grow{from{transform:scaleX(.03)}to{transform:scaleX(1)}}@media(prefers-reduced-motion:reduce){.poei1-fill1,.poei1-fill2,.poei1-fill3,.poei1-fill4{animation:none}}
</style></defs>
<rect class="poei1-bg" width="900" height="340" rx="18"/>
<text class="poei1-h" x="450" y="30" text-anchor="middle">Puissance maximale côté PSE — comparaison indicative</text>
<text class="poei1-sub" x="450" y="49" text-anchor="middle">Échelle visuelle proportionnelle, plafonds de référence usuels</text>
<g>
<text class="poei1-h" x="42" y="94">Type 1 — 802.3af</text><rect class="poei1-track" x="250" y="76" width="500" height="24" rx="5"/><rect class="poei1-fill1" x="250" y="76" width="85.56" height="24" rx="5"/><text class="poei1-t" x="770" y="93">15,4 W</text>
<text class="poei1-h" x="42" y="151">Type 2 — 802.3at</text><rect class="poei1-track" x="250" y="133" width="500" height="24" rx="5"/><rect class="poei1-fill2" x="250" y="133" width="166.67" height="24" rx="5"/><text class="poei1-t" x="770" y="150">30 W</text>
<text class="poei1-h" x="42" y="208">Type 3 — 802.3bt</text><rect class="poei1-track" x="250" y="190" width="500" height="24" rx="5"/><rect class="poei1-fill3" x="250" y="190" width="333.33" height="24" rx="5"/><text class="poei1-t" x="770" y="207">60 W</text>
<text class="poei1-h" x="42" y="265">Type 4 — 802.3bt</text><rect class="poei1-track" x="250" y="247" width="500" height="24" rx="5"/><rect class="poei1-fill4" x="250" y="247" width="500" height="24" rx="5"/><text class="poei1-t" x="770" y="264">90 W</text>
</g>
<path d="M250 291 H750" stroke="#71849e" stroke-width="1"/>
<text class="poei1-sub" x="250" y="309">0 W</text><text class="poei1-sub" x="750" y="309" text-anchor="end">90 W</text>
<text class="poei1-sub" x="450" y="329" text-anchor="middle">La puissance maximale PSE ne doit pas être confondue avec la puissance reçue par le PD.</text>
</svg>


# 3. Classes de puissance : comprendre ce que le switch réserve

Une classe PoE aide le système à déterminer le niveau de puissance associé au PD. Les mécanismes exacts diffèrent selon le standard et le type de matériel.

Pour l’administrateur, cette notion a une conséquence concrète : la quantité de puissance que le contrôleur réserve peut différer de la consommation que l’on mesure à un moment donné.

Un PD peut consommer peu au repos et beaucoup plus dans certaines conditions. Si le PSE devait réserver uniquement la consommation instantanée, il pourrait accepter un nombre excessif d’appareils, puis manquer de capacité lorsque plusieurs d’entre eux sollicitent fortement leur alimentation.

La réservation est donc une règle de gestion de capacité, pas un compteur de consommation instantanée.

## 3.1 Exemple de différence entre réservation et mesure

Considérons un PD pour lequel le switch réserve 30 W, alors que la télémétrie montre une consommation de 12 W au moment de l’observation.

Ces valeurs ne sont pas contradictoires :
- 30 W représentent la capacité retenue par le système ;
- 12 W représentent la consommation observée à l’instant de la mesure ;
- la marge disponible dépend de la politique de réservation et de la capacité réelle du système.

Un autre switch pourrait mettre en œuvre une politique différente, si le matériel et la configuration le permettent. Il faut donc consulter les données de la plate-forme concernée, plutôt que supposer une méthode unique.

## 3.2 Classement, échange LLDP et allocation

LLDP (*Link Layer Discovery Protocol*) est un protocole de découverte de voisins de couche 2. Certaines implémentations PoE utilisent des échanges LLDP pour préciser les besoins en puissance ou ajuster l’allocation selon les capacités prises en charge.

Il faut cependant distinguer :
- la détection électrique nécessaire à l’alimentation PoE normalisée ;
- la classification selon le mécanisme prévu ;
- les échanges de couche 2 susceptibles d’affiner la demande ;
- la décision finale du PSE d’accorder ou de refuser la puissance.

LLDP ne remplace pas automatiquement tous les mécanismes électriques du PoE. Les capacités d’échange, les états et les commandes disponibles dépendent du matériel, du PD et du standard.

## 3.3 Pourquoi il faut vérifier l’état réel du port

Le nom du port et le voyant Ethernet sont insuffisants pour connaître la situation énergétique. Un switch administrable peut exposer plusieurs informations différentes :

- état Ethernet du lien ;
- statut de la fonction PoE ;
- puissance réservée ;
- consommation mesurée ;
- classe détectée ou informations de négociation ;
- motif de refus ou d’interruption ;
- budget restant du système.

Il n’est pas garanti que toutes ces informations soient disponibles sur chaque équipement. Il faut documenter les données réellement fournies par la plate-forme et signaler les mesures non disponibles comme inconnues, plutôt que leur attribuer une valeur fictive.


# 4. Schéma animé — Classification et décision d’admission

Ce schéma sépare volontairement la détection, la classification, la négociation éventuelle et la décision d’admission.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 325" role="img" aria-labelledby="poei2-title">
<title id="poei2-title">Processus animé de détection et d’allocation PoE</title>
<defs><style>
.poei2-bg{fill:#101827}.poei2-box{fill:#1b2b42;stroke:#526b8c;stroke-width:1.8}.poei2-h{fill:#f8fafc;font:700 14px Arial,sans-serif}.poei2-t{fill:#d0dceb;font:12px Arial,sans-serif}.poei2-link{fill:none;stroke:#4ddbb0;stroke-width:3;stroke-dasharray:7 8;animation:poei2-dash 1s linear infinite}.poei2-accent{fill:#4ddbb0;animation:poei2-pulse 1.6s ease-in-out infinite}.poei2-note{fill:#9db0c8;font:11px Arial,sans-serif}@keyframes poei2-dash{to{stroke-dashoffset:-30}}@keyframes poei2-pulse{0%,100%{opacity:.35}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.poei2-link,.poei2-accent{animation:none}}
</style></defs>
<rect class="poei2-bg" width="900" height="325" rx="18"/>
<text class="poei2-h" x="450" y="31" text-anchor="middle" font-size="18">Logique de contrôle du PSE</text>
<rect class="poei2-box" x="24" y="77" width="194" height="135" rx="12"/>
<text class="poei2-h" x="121" y="105" text-anchor="middle">1. Détection</text>
<text class="poei2-t" x="121" y="132" text-anchor="middle">Signature électrique</text><text class="poei2-t" x="121" y="149" text-anchor="middle">attendue d’un PD</text>
<circle class="poei2-accent" cx="121" cy="180" r="6"><animate attributeName="r" values="4;7;4" dur="1.6s" repeatCount="indefinite"/></circle>
<text class="poei2-t" x="121" y="199" text-anchor="middle">Détection valide ?</text>
<rect class="poei2-box" x="244" y="77" width="194" height="135" rx="12"/>
<text class="poei2-h" x="341" y="105" text-anchor="middle">2. Classification</text>
<text class="poei2-t" x="341" y="132" text-anchor="middle">Classe et besoin</text><text class="poei2-t" x="341" y="149" text-anchor="middle">de puissance</text>
<text class="poei2-t" x="341" y="180" text-anchor="middle">Évaluer les limites</text><text class="poei2-t" x="341" y="197" text-anchor="middle">du couple PSE/PD</text>
<rect class="poei2-box" x="464" y="77" width="194" height="135" rx="12"/>
<text class="poei2-h" x="561" y="105" text-anchor="middle">3. Négociation</text>
<text class="poei2-t" x="561" y="132" text-anchor="middle">LLDP et politiques</text><text class="poei2-t" x="561" y="149" text-anchor="middle">si applicables</text>
<text class="poei2-t" x="561" y="180" text-anchor="middle">Préciser l’allocation</text><text class="poei2-t" x="561" y="197" text-anchor="middle">selon le matériel</text>
<rect class="poei2-box" x="684" y="77" width="192" height="135" rx="12"/>
<text class="poei2-h" x="780" y="105" text-anchor="middle">4. Admission</text>
<text class="poei2-t" x="780" y="132" text-anchor="middle">Vérifier le budget</text><text class="poei2-t" x="780" y="149" text-anchor="middle">et les limites du port</text>
<circle class="poei2-accent" cx="780" cy="180" r="6"><animate attributeName="opacity" values=".2;1;.2" dur="1.5s" repeatCount="indefinite"/></circle>
<text class="poei2-t" x="780" y="199" text-anchor="middle">Accorder ou refuser</text>
<path class="poei2-link" d="M218 145 H244 M438 145 H464 M658 145 H684"/>
<rect x="70" y="241" width="760" height="50" rx="10" fill="#182a3f" stroke="#4b6483"/>
<text class="poei2-h" x="450" y="261" text-anchor="middle">Point clé : détecter un PD n’équivaut pas à lui accorder n’importe quelle puissance.</text>
<text class="poei2-note" x="450" y="279" text-anchor="middle">Les mécanismes et les messages varient suivant le standard, les capacités et la politique de l’équipement.</text>
</svg>


# 5. Calculer le budget global du switch

Le budget PoE est une contrainte collective. Tous les ports puisent dans une capacité électrique qui dépend notamment de l’alimentation, de l’architecture interne et des limites logicielles ou matérielles du switch.

## 5.1 Calcul de la marge théorique

Une première approximation utile est :

`Marge théorique = Budget PoE utilisable − Somme des réservations existantes`

Lorsqu’on étudie une nouvelle demande :

`Marge après demande = Marge théorique − Puissance à réserver pour le nouveau PD`

Cette formule est un outil de raisonnement. Elle ne remplace pas les règles d’admission du PSE. Le budget utilisable doit représenter la capacité réellement exploitable dans l’état actuel du matériel.

Il faut également tenir compte des alimentations redondantes, du comportement en cas de panne d’une source, de la politique de priorité, des limites par port et des réserves de conception.

## 5.2 Exemple chiffré

Supposons un switch avec :
- budget PoE utilisable : 240 W ;
- réservations existantes : 165 W ;
- demande d’un nouveau PD : 45 W.

La marge théorique avant admission est :

`240 − 165 = 75 W`

La marge théorique après admission est :

`75 − 45 = 30 W`

La demande est donc compatible avec le budget global dans cet exemple. Ce n’est toutefois pas une preuve suffisante pour autoriser le port.

Il reste à vérifier :
- la capacité maximale du port ;
- la classe ou le niveau de puissance requis ;
- la compatibilité de la source et du PD ;
- le statut de la négociation éventuelle ;
- le fonctionnement du switch dans sa configuration actuelle ;
- les contraintes liées à une alimentation redondante défaillante, le cas échéant.

## 5.3 Pourquoi un calcul global peut-il être insuffisant ?

Un switch peut disposer de 100 W de marge au niveau du système, tout en refusant une demande sur un port qui ne prend pas en charge la puissance requise.

Il peut également disposer d’une capacité électrique totale suffisante mais être configuré avec une politique qui limite la puissance ou la priorité de certains ports.

Le bon raisonnement consiste donc à vérifier successivement :
1. l’admissibilité au niveau du port ;
2. la compatibilité entre PSE et PD ;
3. le budget global utilisable ;
4. la politique d’allocation et les conditions matérielles.


# 6. Schéma animé — Répartition du budget

Les valeurs sont illustratives. Le diagramme distingue les réservations existantes, une demande et la marge restante.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 325" role="img" aria-labelledby="poei3-title">
<title id="poei3-title">Budget PoE : allocations existantes, nouvelle demande et marge restante</title>
<defs><style>
.poei3-bg{fill:#101827}.poei3-h{fill:#f8fafc;font:700 16px Arial,sans-serif}.poei3-t{fill:#d1dbea;font:12px Arial,sans-serif}.poei3-note{fill:#9eb1c8;font:11px Arial,sans-serif}.poei3-track{fill:#26374f}.poei3-current{fill:#60a5fa;transform-box:fill-box;transform-origin:left center;animation:poei3-grow 1.4s ease-out both}.poei3-new{fill:#4ddbb0;transform-box:fill-box;transform-origin:left center;animation:poei3-grow 1.1s ease-out both;animation-delay:1s}.poei3-free{fill:#64748b}@keyframes poei3-grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}@media(prefers-reduced-motion:reduce){.poei3-current,.poei3-new{animation:none}}
</style></defs>
<rect class="poei3-bg" width="900" height="325" rx="18"/>
<text class="poei3-h" x="450" y="31" text-anchor="middle">Budget utilisable : 240 W — valeurs purement illustratives</text>
<text class="poei3-t" x="55" y="79">Budget global</text>
<rect class="poei3-track" x="55" y="91" width="790" height="29" rx="6"/>
<rect class="poei3-current" x="55" y="91" width="543.1" height="29" rx="6"/>
<rect class="poei3-new" x="598.1" y="91" width="148.1" height="29" rx="6"/>
<rect class="poei3-free" x="746.2" y="91" width="98.8" height="29" rx="6"/>
<text class="poei3-t" x="55" y="146">165 W réservés</text>
<text class="poei3-t" x="450" y="146" text-anchor="middle">45 W demandés</text>
<text class="poei3-t" x="845" y="146" text-anchor="end">30 W restants</text>
<path d="M55 169 H845" stroke="#4b617f" stroke-width="1"/>
<rect x="55" y="190" width="245" height="83" rx="10" fill="#172c46" stroke="#60a5fa"/>
<text class="poei3-h" x="177" y="215" text-anchor="middle">Avant admission</text>
<text class="poei3-t" x="177" y="240" text-anchor="middle">240 − 165 = 75 W</text>
<text class="poei3-note" x="177" y="258" text-anchor="middle">Marge théorique initiale</text>
<rect x="327" y="190" width="245" height="83" rx="10" fill="#14322f" stroke="#4ddbb0"/>
<text class="poei3-h" x="449" y="215" text-anchor="middle">Après admission</text>
<text class="poei3-t" x="449" y="240" text-anchor="middle">75 − 45 = 30 W</text>
<text class="poei3-note" x="449" y="258" text-anchor="middle">Marge théorique résiduelle</text>
<rect x="599" y="190" width="246" height="83" rx="10" fill="#35291b" stroke="#f6bf69"/>
<text class="poei3-h" x="722" y="215" text-anchor="middle">Validation obligatoire</text>
<text class="poei3-t" x="722" y="240" text-anchor="middle">Port, PD, classe, priorité</text>
<text class="poei3-note" x="722" y="258" text-anchor="middle">Le calcul global ne suffit pas seul</text>
<text class="poei3-note" x="450" y="302" text-anchor="middle">La barre illustre une réservation de capacité, pas la mesure instantanée de la consommation.</text>
</svg>


# 7. Dimensionnement d’un parc d’équipements

Un dimensionnement correct doit utiliser la consommation et le profil de puissance des appareils prévus, et non simplement leur nombre.

Supposons qu’un étage comporte :
- 12 téléphones IP ;
- 6 points d’accès Wi-Fi ;
- 4 caméras réseau.

Les quantités seules ne permettent pas de conclure au budget nécessaire. Il faut connaître :
- le modèle et les besoins de chaque famille de PD ;
- la puissance d’admission à réserver par appareil ;
- la capacité des ports ;
- la puissance utilisable du switch ;
- les exigences de disponibilité ;
- la marge pour l’extension future.

Le dimensionnement se fait idéalement à partir des informations du fabricant et du comportement attendu de l’installation.

## 7.1 Trois scénarios utiles

**Scénario nominal :** les équipements fonctionnent selon le profil courant prévu.

**Scénario de forte demande :** plusieurs PD utilisent simultanément les fonctions qui sollicitent le plus leur alimentation.

**Scénario dégradé :** une alimentation redondante est indisponible ou une partie de la capacité est perdue.

Un réseau critique ne doit pas être dimensionné uniquement pour le scénario nominal si le service doit survivre à un incident matériel. Il faut chiffrer la capacité utilisable dans les états pertinents.

## 7.2 Calcul guidé

Un administrateur relève les informations suivantes sur un switch :

| Paramètre | Valeur illustrative |
|---|---:|
| Budget PoE utilisable | 370 W |
| Réservations existantes | 270 W |
| Puissance à réserver pour un nouveau PD | 60 W |

La marge théorique avant la demande est :

`370 − 270 = 100 W`

La marge théorique après la demande est :

`100 − 60 = 40 W`

Le budget global semble suffisant au vu de ces valeurs. Il faut néanmoins vérifier les limites du port et du PD, les éventuelles contraintes de classe, et le budget utilisable dans l’état matériel réel.

## 7.3 Pourquoi faut-il prévoir une marge ?

Un système dimensionné exactement à sa limite offre peu de souplesse. Il peut devenir problématique lorsque de nouveaux appareils sont ajoutés, lorsque les besoins changent ou lorsqu’une source d’alimentation est perdue.

Une marge appropriée n’est pas un chiffre universel. Elle dépend du profil des charges, des exigences de disponibilité, du niveau de redondance et du plan d’évolution du réseau.


# 8. Dépannage intermédiaire : analyser avant de modifier

Un diagnostic professionnel doit distinguer les faits, les hypothèses et les corrections appliquées.

Une méthode efficace comprend quatre étapes :
1. **Collecter :** recueillir l’état du port, les compteurs, les journaux et les caractéristiques du matériel.
2. **Comparer :** comparer le comportement à un port fonctionnel ou au fonctionnement attendu.
3. **Tester :** réaliser un test contrôlé, en ne changeant qu’un facteur à la fois lorsque cela est possible.
4. **Confirmer :** vérifier que la correction résout le symptôme sans créer un autre problème.

## 8.1 Matrice de dépannage

| Symptôme | Causes possibles | Vérifications prioritaires |
|---|---|---|
| PD non détecté | Câble, PD non compatible, port désactivé | État du port, câble testé, compatibilité du PD |
| PD détecté mais alimentation refusée | Budget, limite du port, politique | Puissance réservée, budget global et logs |
| PD démarre puis s’éteint | Profil de consommation, câble, défaut matériel | Événements horodatés et puissance disponible |
| Plusieurs PD tombent ensemble | Alimentation du switch, budget ou événement commun | État du châssis, réservations, journaux système |
| Le port Ethernet est actif mais le PD ne fonctionne pas | Problème applicatif ou alimentation partielle | Statut PoE distinct du statut Ethernet |
| Consommation apparemment faible mais admission refusée | Réservations ou politique d’allocation | Capacité retenue par le contrôleur |
| Panne après remplacement du switch | Profil des ports ou capacité différente | Comparer les références, les paramètres et les limites |

Le même symptôme peut avoir plusieurs causes. La priorité est de collecter des preuves qui permettent de départager les hypothèses.

## 8.2 Pourquoi ne faut-il pas forcer immédiatement la puissance ?

Augmenter une limite configurée ou contourner la procédure d’admission sans connaître les capacités du matériel peut conduire à une alimentation non adaptée. Il faut d’abord vérifier que le PD, le PSE et la liaison sont conçus pour le niveau de puissance recherché.

Une correction doit respecter la documentation du constructeur, les limites du standard et les exigences électriques de l’installation.


# 9. Commandes et outils d’administration

Les commandes sont spécifiques au constructeur et à la famille de système d’exploitation. Il faut utiliser la documentation correspondant à la version logicielle du switch.

Sur certaines plateformes Cisco Catalyst, par exemple, `show power inline` permet d’examiner l’état PoE des ports et des informations de puissance. La disponibilité et le détail de la sortie dépendent toutefois du matériel et de la version.

Les commandes de contrôle d’interface, les commandes de journaux et les commandes de budget PoE doivent être consultées dans la documentation de la plate-forme. Ne copie pas une commande de configuration dans un réseau de production sans en vérifier l’effet.

## 9.1 Informations à relever

Pour chaque port concerné, cherche à établir :
- le statut administratif et opérationnel ;
- l’état de la fonction PoE ;
- la classe ou l’allocation connue ;
- la puissance réservée, si elle est exposée ;
- la consommation mesurée, si elle est disponible ;
- le budget restant du système ;
- les événements associés au PD ;
- le moment où le problème a commencé.

Les informations manquantes doivent être identifiées comme non disponibles. Une plate-forme qui n’expose pas un compteur n’autorise pas à supposer que sa valeur est nulle.

## 9.2 Pourquoi collecter l’heure exacte ?

Un événement horodaté permet de rapprocher le statut PoE d’autres événements : redémarrage du switch, changement de configuration, mise à jour, perte d’une alimentation, ou modification de connectivité.

La chronologie est souvent essentielle pour déterminer si la cause provient du PD, du port, de la capacité du système ou d’un événement commun.


# 10. Travaux pratiques

## TP 1 — Inventaire et budget

**Objectif :** construire une vision du budget utilisé et de la capacité restante.

1. Inventorier les ports PoE actifs.
2. Relever les modèles de PD et leurs besoins de puissance.
3. Relever le budget global et les allocations affichées par le switch.
4. Calculer la marge théorique à partir des réservations.
5. Vérifier les limites individuelles des ports.
6. Évaluer si l’ajout d’un PD serait admissible.

**Livrable :** un tableau indiquant le port, le PD, le standard, l’allocation, la mesure disponible, le statut et les éventuels risques.

## TP 2 — Analyser un refus PoE

1. Choisir un cas de laboratoire où l’alimentation d’un PD est refusée.
2. Collecter les informations du port et du système.
3. Relever les événements qui entourent le refus.
4. Établir deux ou trois hypothèses plausibles.
5. Réaliser une vérification contrôlée par hypothèse.
6. Rédiger la cause déterminée ou expliquer pourquoi les preuves sont insuffisantes.

Le but n’est pas seulement de rétablir le service. Il faut être capable d’expliquer pourquoi la correction a fonctionné.

## TP 3 — Vérifier un remplacement d’équipement

Après le remplacement d’un switch par une autre référence :
1. comparer le budget PoE utilisable ;
2. comparer les puissances maximales par port ;
3. vérifier les réservations et les priorités ;
4. contrôler les paramètres des ports ;
5. tester les PD les plus exigeants ;
6. documenter les différences entre les deux équipements.

Un nombre identique de ports ne signifie pas une capacité d’alimentation identique.


# 11. Étude de cas : ajout d’un point d’accès

Un réseau possède un switch dont le budget PoE utilisable est de 240 W. Le système réserve déjà 165 W. Un nouveau point d’accès demande une allocation de 45 W.

### Questions

1. Quelle est la marge théorique initiale ?
2. Quelle est la marge théorique après la demande ?
3. Peut-on conclure immédiatement que le port sera alimenté ?
4. Quelles informations supplémentaires faut-il vérifier ?
5. Pourquoi la consommation mesurée de l’appareil ne remplace-t-elle pas sa réservation ?

### Corrigé détaillé

**1. Marge initiale**

`240 − 165 = 75 W`

Le système dispose théoriquement de 75 W avant la nouvelle admission.

**2. Marge après demande**

`75 − 45 = 30 W`

Une fois les 45 W ajoutés aux réservations, la marge théorique serait de 30 W.

**3. La marge suffit-elle pour conclure ?**

Non. Elle permet de constater que la demande est compatible avec le budget global de l’exemple, mais elle ne garantit pas que le port peut fournir cette puissance.

**4. Vérifications complémentaires**

Il faut vérifier le standard et le niveau de puissance du point d’accès, la capacité du port, les conditions de classification ou de négociation, les priorités configurées et la capacité électrique réelle du switch.

**5. Réservation contre consommation**

La consommation mesurée correspond à l’utilisation à un instant particulier. La réservation est une décision d’allocation du système, destinée à tenir compte des besoins et des règles du contrôleur. Les deux valeurs peuvent donc être différentes.


# 12. Évaluation intermédiaire

Réponds aux questions sans consulter les sections précédentes, puis compare tes réponses avec le corrigé.

1. Quelle différence existe-t-il entre la puissance délivrée par le PSE et celle disponible à l’entrée du PD ?
2. Pourquoi une consommation mesurée de 10 W ne prouve-t-elle pas qu’un port ayant une réservation de 30 W peut libérer 20 W pour un nouvel appareil ?
3. Quel rôle LLDP peut-il jouer dans une implémentation PoE ?
4. Quelle différence existe-t-il entre une limite de port et un budget global ?
5. Pourquoi faut-il vérifier les capacités du port lorsqu’il reste assez de budget global ?
6. Comment distinguer un refus d’admission d’une panne du câble ?
7. Quels éléments faut-il collecter avant de modifier une configuration PoE ?
8. Pourquoi doit-on examiner les alimentations du châssis dans le cas d’une panne touchant plusieurs ports ?

## Corrigé

1. Une partie de l’énergie est dissipée dans la liaison. Le PD ne reçoit donc pas nécessairement toute la puissance délivrée par le PSE.
2. Le switch peut réserver la puissance selon la classe, la demande ou sa politique, indépendamment de la consommation momentanée.
3. LLDP peut participer à des échanges de puissance complémentaires sur les équipements compatibles. Il ne remplace pas tous les mécanismes électriques.
4. La limite du port concerne un port particulier ; le budget global concerne la capacité distribuable par le système.
5. Le port peut être incapable de fournir le niveau demandé, même si le budget global semble suffisant.
6. On compare les statuts Ethernet et PoE, les événements du contrôleur et le comportement obtenu avec un câble connu comme fonctionnel.
7. Statut du port, caractéristiques du PD et du PSE, budget, réservation, mesure éventuelle, journaux et chronologie.
8. Une source défaillante peut modifier la capacité totale et provoquer un problème commun à plusieurs ports.


# 13. Références techniques

- [Cisco — Tableau des standards PoE et puissances disponibles côté PD](https://www.cisco.com/c/en/us/products/collateral/networking/industrial-switches/poe-ind-data-control-single-cable-so.html)
- [Cisco — Configuration et administration de PoE](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst_digital_building_switches/software/15-2_7_e/configuration_guide/b_1527e_consolidated_cdb_cg/m_1526e_poe_cg_cdb.pdf)
- [Ethernet Alliance — Évolution des standards PoE](https://ethernetalliance.org/wp-content/uploads/2020/02/EthernetAlliance_Gen2PoECertProgram_techbrief-FINAL-19DEC19.pdf)
- [Microchip — Types, classes et caractéristiques électriques PoE](https://developerhelp.microchip.com/xwiki/bin/view/applications/ethernet/poe/standards/)

Pour les opérations réelles, utilise les commandes et les recommandations correspondant au modèle exact du switch, à sa version logicielle et aux PD installés.