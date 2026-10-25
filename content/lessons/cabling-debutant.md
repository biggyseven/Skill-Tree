# Câblage réseau et normes — Niveau débutant

> **Fichier :** `cabling-debutant.md`  
> **Parcours :** 1/3 — comprendre les composants, choisir le bon support et réaliser une installation propre.  
> **Prérequis :** notions de réseau local, switch, routeur et Ethernet.  
> **Objectif :** reconnaître le câblage cuivre et fibre, lire un brochage RJ45, comprendre la limite usuelle de distance et effectuer les premiers contrôles sans confondre test de continuité et certification.


## 1. Pourquoi le câblage est-il important ?

Le câblage est la partie physique du réseau. Il relie les prises murales, panneaux de brassage, équipements actifs, points d'accès Wi-Fi, téléphones IP, caméras, serveurs et locaux techniques.

Un lien peut échouer à cause d'une mauvaise configuration, mais aussi à cause d'une paire mal terminée, d'un câble écrasé, d'un connecteur contaminé, d'une fibre pliée trop fortement ou d'une liaison trop longue. Une installation propre doit être **adaptée à l'application, installée selon les règles applicables, identifiée et testée**.

Le but n'est pas seulement d'obtenir un voyant vert au switch. Le but est d'obtenir un lien qui respecte les performances attendues et reste maintenable.

## 2. Les éléments d'un câblage structuré

- **Câble horizontal :** relie la salle de télécommunication à une zone de travail ou à un point de consolidation prévu par la conception.
- **Prise de télécommunication :** terminaison côté utilisateur.
- **Panneau de brassage (patch panel) :** terminaison côté baie, facilitant l'administration.
- **Cordon de brassage :** relie le panneau au switch ou à un autre équipement.
- **Baie et guides-câbles :** organisent les équipements et limitent la traction sur les cordons.
- **Câblage de backbone :** interconnecte les locaux techniques, étages ou bâtiments.
- **Chemins de câbles, conduits et pénétrations :** protègent et organisent le trajet physique.

### Schéma animé — du switch à l'utilisateur

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 330" role="img" aria-labelledby="cab1t cab1d">
  <title id="cab1t">Trajet d'un lien de câblage structuré</title><desc id="cab1d">Le switch est relié par un cordon au panneau de brassage. Un câble horizontal rejoint une prise murale, puis un cordon relie le poste.</desc>
  <defs><marker id="cab1arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#59d8c7"/></marker><style>
  .cab1bg{fill:#0b1220}.cab1p{fill:#152238;stroke:#3c506f;stroke-width:1.5}.cab1h{fill:#f4f7fb;font:700 17px sans-serif}.cab1x{fill:#cbd5e1;font:14px sans-serif}.cab1s{fill:#9aaec6;font:12px sans-serif}.cab1f{fill:none;stroke:#59d8c7;stroke-width:3;stroke-dasharray:9 8;marker-end:url(#cab1arr);animation:cab1flow 1.8s linear infinite}@keyframes cab1flow{to{stroke-dashoffset:-34}}@media(prefers-reduced-motion:reduce){.cab1f{animation:none}}
  </style></defs>
  <rect class="cab1bg" width="960" height="330" rx="18"/><text class="cab1h" x="28" y="34">Un lien structuré, plusieurs éléments à contrôler</text>
  <rect class="cab1p" x="25" y="92" width="155" height="114" rx="11"/><text class="cab1h" x="102" y="126" text-anchor="middle">Switch</text><text class="cab1x" x="102" y="151" text-anchor="middle">Port actif</text><text class="cab1s" x="102" y="176" text-anchor="middle">Baie réseau</text>
  <rect class="cab1p" x="220" y="92" width="155" height="114" rx="11"/><text class="cab1h" x="297" y="126" text-anchor="middle">Patch panel</text><text class="cab1x" x="297" y="151" text-anchor="middle">Brassage</text><text class="cab1s" x="297" y="176" text-anchor="middle">Terminaison fixe</text>
  <rect class="cab1p" x="415" y="92" width="155" height="114" rx="11"/><text class="cab1h" x="492" y="126" text-anchor="middle">Câble fixe</text><text class="cab1x" x="492" y="151" text-anchor="middle">Horizontal</text><text class="cab1s" x="492" y="176" text-anchor="middle">Dans les chemins</text>
  <rect class="cab1p" x="610" y="92" width="145" height="114" rx="11"/><text class="cab1h" x="682" y="126" text-anchor="middle">Prise</text><text class="cab1x" x="682" y="151" text-anchor="middle">RJ45 / jack</text><text class="cab1s" x="682" y="176" text-anchor="middle">Zone de travail</text>
  <rect class="cab1p" x="795" y="92" width="140" height="114" rx="11"/><text class="cab1h" x="865" y="126" text-anchor="middle">Poste</text><text class="cab1x" x="865" y="151" text-anchor="middle">PC / téléphone</text><text class="cab1s" x="865" y="176" text-anchor="middle">Équipement final</text>
  <path class="cab1f" d="M180 149 H220"/><path class="cab1f" d="M375 149 H415"/><path class="cab1f" d="M570 149 H610"/><path class="cab1f" d="M755 149 H795"/>
  <rect x="25" y="237" width="910" height="62" rx="10" fill="#102b33" stroke="#286c70"/><text x="45" y="261" fill="#a7f3e8" font="700 14px sans-serif">Point essentiel</text><text class="cab1x" x="45" y="283">La performance du lien dépend du canal complet : câble fixe, terminaisons, cordons, connecteurs et qualité d'installation.</text>
</svg>

Les flèches animées illustrent le trajet logique du lien ; elles ne représentent pas un débit réel. L'animation peut être désactivée selon les préférences du navigateur.

## 3. Cuivre ou fibre optique ?

| Support | Atouts | Limites / points de vigilance | Utilisations courantes |
|---|---|---|---|
| Cuivre à paires torsadées | Économique, simple à terminer, transport Ethernet et PoE sur les variantes compatibles | Distance et immunité électromagnétique limitées par la conception ; sensibilité à la qualité de pose | Postes, téléphones IP, caméras, points d'accès |
| Fibre multimode (OM) | Bonne option pour certaines liaisons de bâtiment et de salle informatique | Distance liée à la classe de fibre, au débit et aux transceivers | Baies, datacenter, backbone de courte/moyenne portée |
| Fibre monomode (OS) | Très adaptée aux distances plus longues et aux débits élevés avec optiques appropriées | Optiques, connectique et budget optique à choisir précisément | Backbone, campus, interconnexion de bâtiments |

Ne choisis pas une fibre seulement d'après la couleur de sa gaine. Il faut confirmer sa désignation, son environnement d'installation, son nombre de fibres, ses connecteurs, son type de polissage et les caractéristiques des modules optiques.

## 4. Catégories cuivre : que signifient Cat 5e, Cat 6 et Cat 6A ?

La catégorie décrit les performances du câblage et de ses composants ; ce n'est ni le débit garanti pour tous les équipements ni une simple couleur de câble.

| Catégorie | Bande passante de référence courante | Usage typique |
|---|---:|---|
| Cat 5e | 100 MHz | Gigabit Ethernet dans un canal conforme |
| Cat 6 | 250 MHz | Gigabit ; certains usages 10GBASE-T sur distances plus courtes, selon conditions et conformité |
| Cat 6A | 500 MHz | 10GBASE-T jusqu'à 100 m dans un canal conforme à la conception applicable |
| Cat 8 | 2 000 MHz | Cas spécifiques à haut débit et courte portée en environnement datacenter, selon la norme et le canal prévu |

Pour une installation neuve de bâtiment qui doit rester évolutive, Cat 6A constitue souvent un choix pertinent, mais le choix final doit tenir compte de la capacité requise, du cheminement, de l'environnement, du coût et des normes retenues. Un câble Cat 6 ne doit pas être considéré comme une promesse universelle de 10 Gb/s sur 100 m.

## 5. La limite usuelle du cuivre Ethernet : 100 mètres

Pour beaucoup de déploiements Ethernet sur paires torsadées, l'architecture de câblage classique repose sur un **canal pouvant atteindre 100 m**, comprenant typiquement :

- jusqu'à **90 m de lien permanent** (câblage fixe, prises et panneau de brassage) ;
- une allocation typique d'au plus **10 m au total pour les cordons** de brassage et de zone de travail.

Ces chiffres sont une règle de conception courante, pas une autorisation de poser n'importe quel câble sur 100 m. La catégorie, le nombre de connexions, la température, la présence de PoE et les règles propres à l'application doivent être pris en compte. Les cas particuliers doivent être validés avec le standard applicable et la documentation constructeur.

Au-delà de la portée permise, utilise une architecture appropriée : fibre optique, équipement intermédiaire prévu par la conception, ou autre solution d'ingénierie validée. Ne rajoute pas simplement un coupleur en espérant conserver les performances.

## 6. Comprendre les paires et le connecteur RJ45

Un câble Ethernet cuivre à quatre paires contient huit conducteurs regroupés par paires torsadées. Le maintien des torsades jusqu'à proximité du point de terminaison aide à préserver les performances électriques.

Les noms commerciaux utilisent souvent « RJ45 » pour le connecteur modulaire 8P8C courant sur Ethernet. Dans une installation structurée, les prises et panneaux doivent être du système approprié, et les terminaison doivent suivre le code choisi.

### Brochage T568A et T568B

| Broche | T568A | T568B |
|---:|---|---|
| 1 | Blanc/vert | Blanc/orange |
| 2 | Vert | Orange |
| 3 | Blanc/orange | Blanc/vert |
| 4 | Bleu | Bleu |
| 5 | Blanc/bleu | Blanc/bleu |
| 6 | Orange | Vert |
| 7 | Blanc/marron | Blanc/marron |
| 8 | Marron | Marron |

Choisis le même schéma aux deux extrémités d'un lien droit : A-A ou B-B. Un câble avec A à une extrémité et B à l'autre est un câble croisé historique. Les équipements modernes prennent souvent en charge l'auto-MDI-X, mais ce mécanisme ne remplace pas un câblage structuré correctement terminé.

### Schéma animé — conserver l'ordre des paires

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 300" role="img" aria-labelledby="cab2t cab2d">
<title id="cab2t">Les quatre paires d'un câble cuivre Ethernet</title><desc id="cab2d">Quatre paires torsadées distinctes sont présentées avec les couleurs usuelles, puis arrivent au connecteur avec un ordre de brochage contrôlé.</desc>
<defs><style>.cab2bg{fill:#0b1220}.cab2p{fill:#152238;stroke:#3c506f;stroke-width:1.4}.cab2h{fill:#f4f7fb;font:700 17px sans-serif}.cab2x{fill:#cbd5e1;font:14px sans-serif}.cab2s{fill:#9aacc4;font:12px sans-serif}.cab2w{fill:none;stroke-width:5;stroke-linecap:round;stroke-dasharray:7 5;animation:cab2move 2.2s linear infinite}@keyframes cab2move{to{stroke-dashoffset:-24}}@media(prefers-reduced-motion:reduce){.cab2w{animation:none}}</style></defs>
<rect class="cab2bg" width="940" height="300" rx="18"/><text class="cab2h" x="28" y="34">Quatre paires torsadées — ne pas les détorsader inutilement</text>
<rect class="cab2p" x="28" y="62" width="500" height="202" rx="12"/><text class="cab2x" x="48" y="88">Couleurs schématiques (les bandes blanches sont représentées par des tirets)</text>
<text class="cab2x" x="48" y="121">Paire verte</text><path class="cab2w" d="M165 116 H490" stroke="#34d399"/><text class="cab2x" x="48" y="157">Paire orange</text><path class="cab2w" d="M165 152 H490" stroke="#fb923c"/><text class="cab2x" x="48" y="193">Paire bleue</text><path class="cab2w" d="M165 188 H490" stroke="#60a5fa"/><text class="cab2x" x="48" y="229">Paire marron</text><path class="cab2w" d="M165 224 H490" stroke="#c08457"/>
<rect class="cab2p" x="585" y="62" width="327" height="202" rx="12"/><text class="cab2h" x="748" y="91" text-anchor="middle">Terminaison contrôlée</text><g transform="translate(630 111)"><rect x="0" y="0" width="240" height="72" rx="8" fill="#d9e2ed" stroke="#718096"/><g fill="#1f2937"><rect x="14" y="11" width="18" height="34"/><rect x="42" y="11" width="18" height="34"/><rect x="70" y="11" width="18" height="34"/><rect x="98" y="11" width="18" height="34"/><rect x="126" y="11" width="18" height="34"/><rect x="154" y="11" width="18" height="34"/><rect x="182" y="11" width="18" height="34"/><rect x="210" y="11" width="18" height="34"/></g><g fill="#334155" font="10px sans-serif" text-anchor="middle"><text x="23" y="61">1</text><text x="51" y="61">2</text><text x="79" y="61">3</text><text x="107" y="61">4</text><text x="135" y="61">5</text><text x="163" y="61">6</text><text x="191" y="61">7</text><text x="219" y="61">8</text></g></g><text class="cab2s" x="748" y="213" text-anchor="middle">A-A ou B-B pour un lien droit</text><text class="cab2s" x="748" y="233" text-anchor="middle">Contrôler avec un testeur adapté</text></svg>

Le dessin rappelle la séparation des paires ; il ne remplace pas la vue exacte des broches d'un connecteur ou de la documentation de l'outil de terminaison. Vérifie toujours si le brochage affiché est vu côté contacts, côté câble ou côté prise.

## 7. Câbles U/UTP, F/UTP et S/FTP

Les lettres décrivent la construction du blindage :

- **U/UTP** : aucun blindage global ni individuel des paires ;
- **F/UTP** : écran global en feuille, paires non individuellement blindées ;
- **S/FTP** : écran général tressé et écran en feuille autour de chaque paire.

Les désignations complètes peuvent varier selon le système de nomenclature utilisé ; lis la fiche produit plutôt que de te fier à une abréviation isolée. Un câblage blindé n'est pas automatiquement meilleur dans toutes les installations : il exige des composants compatibles et une architecture de liaison équipotentielle et de bonding conforme au projet. Ne raccorde pas un blindage de façon improvisée.

## 8. PoE : données et alimentation sur le même câble

Le PoE (*Power over Ethernet*) permet à un équipement compatible d'être alimenté par le câble réseau, par exemple un téléphone IP, un point d'accès ou une caméra.

À retenir :

- vérifier la compatibilité du switch ou injecteur et du terminal ;
- calculer le budget de puissance total disponible sur le switch ;
- utiliser un câble cuivre conforme, provenant d'un fournisseur identifiable ;
- considérer l'échauffement des faisceaux, la température ambiante et la qualité des connecteurs, en particulier aux puissances élevées ;
- ne pas utiliser de conducteurs en aluminium cuivré (CCA) comme substitut improvisé au câble cuivre massif conforme attendu par la conception.

## 9. Fibre optique : les bons réflexes

La fibre transporte la lumière. Elle est insensible aux perturbations électromagnétiques sur le support optique lui-même et convient bien au backbone. Mais elle nécessite les bons composants : transceivers compatibles, type de fibre adapté, connecteurs correspondants, bonne polarité et budget optique suffisant.

- **OM** désigne les classes de fibre multimode.
- **OS** désigne les classes de fibre monomode dans le système ISO/IEC.
- **LC** est un connecteur courant sur les transceivers Ethernet ; d'autres familles existent.
- **UPC** et **APC** désignent des finitions de ferrule différentes : ne les accouple pas de façon incorrecte.

Ne regarde jamais l'extrémité d'une fibre ou d'un émetteur optique pour vérifier s'il émet. Utilise des méthodes d'inspection et de mesure adaptées.

## 10. Sécurité et qualité de pose

1. Identifier tous les câbles avant de couper, tirer ou déconnecter.
2. Vérifier les chemins de câble et les règles de séparation avec l'énergie électrique selon le code local et le type de cheminement.
3. Respecter le rayon de courbure et la traction maximale spécifiés par le fabricant.
4. Éviter d'écraser le câble avec des colliers trop serrés ou une porte de baie.
5. Ne pas laisser les paires détorsadées inutilement à la terminaison.
6. Respecter la classification incendie et les exigences du bâtiment pour la gaine de câble.
7. Réinstaller correctement le calfeutrement coupe-feu des traversées de parois lorsque c'est requis.
8. Faire réaliser le bonding et les travaux électriques par du personnel qualifié conformément aux règles locales.

Un câble « LSZH » n'est pas pour autant ignifuge ou adapté à tous les parcours. La gaine, la réaction au feu, la fumée, l'acidité, la présence d'un usage extérieur et les règles de construction doivent être examinées selon le contexte.

## 11. Premiers tests : continuité ou certification ?

| Outil | Ce qu'il vérifie | Ce qu'il ne garantit pas à lui seul |
|---|---|---|
| Testeur de continuité simple | Coupure, inversion ou mauvais ordre de conducteurs selon le modèle | Performance de transmission à la catégorie prévue |
| Testeur de qualification | Aptitude estimée à certaines applications | Certification complète d'un lien selon la norme choisie |
| Certificateur de câblage | Mesures et limites d'essai correspondant au lien et à la classe/catégorie sélectionnés | Bon fonctionnement permanent de tout équipement actif ou de toute application future |
| Source + photomètre optique (OLTS) | Perte d'insertion optique selon la méthode de mesure | Localisation complète de tous les événements sur le trajet |
| OTDR | Localisation estimée des événements et pertes le long de la fibre | Remplacement automatique de toutes les mesures de perte de bout en bout |

Une simple lumière de continuité qui passe n'est pas la preuve qu'un câble Cat 6 ou Cat 6A satisfait les performances exigées.

## 12. Atelier débutant — réaliser et documenter un lien

### Matériel

- câble à paires torsadées adapté au parcours ;
- prise et panneau de brassage compatibles ;
- outil de terminaison approprié ;
- cordons conformes ;
- testeur adéquat ;
- étiquettes aux deux extrémités.

### Procédure

1. Relever les deux extrémités et le numéro du lien prévu.
2. Confirmer la catégorie du câble, de la prise, du panneau et des cordons.
3. Faire passer le câble en respectant l'environnement d'installation, les limites du fabricant et les chemins prévus.
4. Terminer les deux extrémités sur le même schéma T568A ou T568B.
5. Poser les étiquettes côté baie et côté prise.
6. Effectuer le test requis pour le niveau de réception attendu.
7. Documenter le résultat, la date, le testeur utilisé et l'identifiant du lien.

### Fiche de relevé

| Champ | Exemple à renseigner |
|---|---|
| Identifiant | `BLD1-TR1-PP01-024` |
| Origine | Baie TR1, panneau PP01, port 24 |
| Destination | Salle 101, prise A |
| Catégorie / classe visée | Selon le projet approuvé |
| Schéma de terminaison | T568A ou T568B |
| Longueur mesurée | Valeur issue de l'outil |
| Résultat | PASS/FAIL selon la limite retenue |
| Rapport | Nom du fichier de résultats |

## 13. Mini-évaluation

**1.** Le testeur de continuité indique « OK ». Peut-on affirmer que le lien est certifié Cat 6A ?  
**Réponse :** non. Le testeur de continuité ne mesure généralement pas l'ensemble des paramètres hautes fréquences requis.

**2.** Un canal cuivre est conçu autour de 100 m. Peut-on utiliser sans vérification un lien fixe de 100 m puis ajouter deux longs cordons ?  
**Réponse :** non. Le canal entier, ses composants, ses connexions et la limite de la norme doivent être considérés.

**3.** Un câble U/UTP est-il obligatoirement mauvais ?  
**Réponse :** non. Il peut convenir à une installation conforme ; le choix dépend de l'environnement électromagnétique, de la conception et des règles du projet.

**4.** Peut-on mélanger les connecteurs APC et UPC parce qu'ils sont mécaniquement proches ?  
**Réponse :** non. Le type de polissage doit être compatible ; l'accouplement incorrect peut détériorer la performance optique.

## 14. Références pour approfondir

- [ISO/IEC 11801-1 — câblage générique des locaux d'utilisateurs](https://www.iso.org/standard/66182.html) — consulter aussi l'amendement 1:2025 et son corrigendum lorsqu'applicables : [ISO/IEC 11801-1/Amd 1:2025](https://www.iso.org/standard/93480.html).
- [ANSI/TIA-568.2-E — câblage cuivre symétrique, publié en 2024](https://tiaonline.org/standardannouncement/tia-publishes-new-standards-ansi-tia-568-2-e-and-ansi-tia-568-5-1/).
- [ANSI/TIA-568.3-E — câblage et composants fibre optique](https://tiaonline.org/standardannouncement/tia-issues-updated-optical-fiber-cabling-component-standard-ansi-tia-568-3-e/).
- [IEC 60332-1-2:2025 — essai de propagation verticale de flamme sur un câble individuel](https://webstore.iec.ch/en/publication/80873). Cet essai ne suffit pas à caractériser à lui seul le comportement au feu d'un faisceau complet.
- [Fluke Networks — inspection, nettoyage et contamination des fibres](https://fr.flukenetworks.com/edocs/wp-fiber-cleaning-and-inspection-white-paper).

Les textes complets des normes sont généralement payants. Avant de déployer, vérifier l'édition contractuelle du projet, le code du bâtiment et les obligations locales : une référence ANSI/TIA n'est pas automatiquement une règle légale dans tous les pays.


**Suite :** `cabling-intermediaire.md` — conception du cheminement, essais de certification, choix cuivre/fibre et réception de chantier.
