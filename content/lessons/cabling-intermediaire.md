# Câblage réseau et normes — Niveau intermédiaire

> **Fichier :** `cabling-intermediaire.md`  
> **Parcours :** 2/3 — concevoir, installer, tester et réceptionner un câblage de bâtiment.  
> **Prérequis :** maîtriser les familles cuivre/fibre, T568A/B, la notion de canal et les contrôles de base.  
> **Objectif :** transformer un besoin réseau en design de câblage vérifiable, choisir les classes de composants, comprendre les paramètres électriques/optique et préparer une recette professionnelle.

---

## 1. Raisonner en lien complet, pas en bobine de câble

Un réseau structuré est un système : câble fixe, prises, panneau, cordons, connecteurs, raccords éventuels, chemins et locaux. Chaque élément peut contribuer à l'échec de la liaison ou réduire sa marge de performance.

Le processus de conception doit partir des services attendus : débits, PoE, durée de vie, conditions ambiantes, chemins disponibles, redondance, sécurité incendie et méthode de test. La catégorie d'un seul câble ne caractérise pas l'ensemble du canal.

## 2. Architecture horizontale et backbone

Dans un bâtiment, la logique d'architecture sépare généralement :

- **Zone de travail :** prise, cordon et équipement utilisateur.
- **Câblage horizontal :** liaison permanente entre local télécom et sortie de télécommunication ou point prévu par la conception.
- **Local télécom / TR :** panneaux, guides, équipements actifs, alimentation, refroidissement et liaison de masse/bonding selon les exigences applicables.
- **Backbone :** interconnexion des locaux techniques, étages ou bâtiments, souvent sur fibre pour les liaisons inter-bâtiments ou les longues distances.
- **Entrée de bâtiment :** transition entre câblage du site et services externes, avec dispositions adaptées à l'environnement et à la protection.

### Schéma animé — structure d'un étage

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" role="img" aria-labelledby="cabint1t cabint1d">
<title id="cabint1t">Architecture horizontale d'un étage</title><desc id="cabint1d">Le local télécom héberge switch et panneaux. Des liaisons permanentes traversent les chemins de câbles vers des prises desservant les zones de travail.</desc>
<defs><marker id="cabint1a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67c8ff"/></marker><style>.cabint1bg{fill:#0b1220}.cabint1p{fill:#142239;stroke:#3a506f;stroke-width:1.4}.cabint1h{fill:#f4f7fb;font:700 16px sans-serif}.cabint1x{fill:#cbd5e1;font:13px sans-serif}.cabint1s{fill:#9aadc5;font:12px sans-serif}.cabint1f{fill:none;stroke:#67c8ff;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#cabint1a);animation:cabint1flow 1.9s linear infinite}@keyframes cabint1flow{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.cabint1f{animation:none}}</style></defs>
<rect class="cabint1bg" width="960" height="360" rx="18"/><text class="cabint1h" x="24" y="32">Du local technique aux prises — horizontal / backbone</text>
<rect class="cabint1p" x="28" y="72" width="240" height="225" rx="12"/><text class="cabint1h" x="148" y="103" text-anchor="middle">Local télécom (TR)</text><rect x="55" y="124" width="186" height="45" rx="7" fill="#233653" stroke="#5b759b"/><text class="cabint1x" x="148" y="152" text-anchor="middle">Switch / actifs</text><rect x="55" y="187" width="186" height="45" rx="7" fill="#233653" stroke="#5b759b"/><text class="cabint1x" x="148" y="215" text-anchor="middle">Panneau de brassage</text><text class="cabint1s" x="148" y="267" text-anchor="middle">Étiquetage + gestion</text>
<rect class="cabint1p" x="348" y="88" width="260" height="190" rx="12"/><text class="cabint1h" x="478" y="118" text-anchor="middle">Chemins de câbles</text><path d="M374 145 H582 M374 162 H582 M374 179 H582 M374 196 H582" stroke="#4f6482" stroke-width="2"/><text class="cabint1x" x="478" y="232" text-anchor="middle">Fixation et rayon adaptés</text><text class="cabint1s" x="478" y="252" text-anchor="middle">Séparation selon les règles du site</text>
<rect class="cabint1p" x="688" y="72" width="244" height="225" rx="12"/><text class="cabint1h" x="810" y="103" text-anchor="middle">Zone de travail</text><rect x="718" y="129" width="184" height="48" rx="7" fill="#233653" stroke="#5b759b"/><text class="cabint1x" x="810" y="158" text-anchor="middle">Prise télécom</text><rect x="718" y="197" width="184" height="48" rx="7" fill="#233653" stroke="#5b759b"/><text class="cabint1x" x="810" y="226" text-anchor="middle">Cordons + équipement</text><text class="cabint1s" x="810" y="270" text-anchor="middle">PC / AP / téléphone</text>
<path class="cabint1f" d="M268 165 H348"/><path class="cabint1f" d="M608 165 H688"/><rect x="28" y="315" width="904" height="26" rx="8" fill="#102b33" stroke="#286c70"/><text x="480" y="333" fill="#a7f3e8" font="13px sans-serif" text-anchor="middle">Les composants et la longueur du canal complet déterminent la conformité.</text></svg>

## 3. Références de câblage et portée typique

En câblage cuivre équilibré, une conception classique pour les applications Ethernet sur paires torsadées peut viser un **canal de 100 m**, composé typiquement d'un **lien permanent de 90 m maximum** et d'une allocation de cordons jusqu'à environ 10 m au total. Il s'agit du modèle largement utilisé en câblage structuré ; les détails dépendent de la classe/catégorie, du canal et des conditions d'application.

| Famille | Bande passante de référence | Décision de conception typique |
|---|---:|---|
| Cat 5e | 100 MHz | Gigabit dans un canal conforme ; choix à comparer au cycle de vie attendu |
| Cat 6 | 250 MHz | Gigabit ; 10GBASE-T possible uniquement sur une portée et dans des conditions validées, pas une promesse à 100 m |
| Cat 6A | 500 MHz | Choix courant pour des canaux 10GBASE-T jusqu'à 100 m lorsqu'ils sont conformes à la norme applicable |
| Cat 8 | 2 000 MHz | Cas spécialisés de datacenter et canaux courts conformes à leur application |

La catégorie doit être considérée de bout en bout. Cat 6A avec une prise plus faible, une mauvaise terminaison ou des cordons inadaptés ne constitue pas un canal Cat 6A conforme.

## 4. Paramètres cuivre à comprendre

Un certificateur peut mesurer plusieurs phénomènes de transmission. Les résultats sont comparés aux limites de test sélectionnées pour la catégorie/classe et le modèle de lien.

- **Wire map :** continuité et correspondance des broches ; recherche notamment inversions, coupures et paires mal raccordées selon l'outil.
- **Longueur :** estimation à partir de la propagation ; le résultat dépend aussi du NVP choisi et de la méthode de mesure.
- **Insertion loss :** perte du signal en traversant le lien.
- **Return loss :** énergie réfléchie en raison d'impédances non homogènes.
- **NEXT / PSNEXT :** diaphonie mesurée à l'extrémité proche, par paire ou somme de puissances.
- **ACR-F / PSACR-F :** diaphonie à l'extrémité distante et sa somme de puissances, selon les définitions de test concernées.
- **Propagation delay et delay skew :** retard et différence de retard entre paires.
- **Alien crosstalk :** couplage entre câbles voisins, particulièrement important dans certains faisceaux hautes performances.

On ne peut pas déterminer la conformité par le seul débit négocié entre deux ports. Un lien peut négocier une vitesse inférieure tout en masquant un problème, ou fonctionner temporairement malgré une marge insuffisante.

## 5. T568A/T568B, paires et erreurs de terminaison

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

Sur les deux extrémités d'un lien droit, utiliser le même schéma. Les paires doivent rester intactes : si l'ordre des couleurs donne l'impression de continuité mais les conducteurs appartiennent à de mauvaises paires électriques, un simple testeur de continuité peut manquer une **paire dédoublée** (*split pair*). La certification haute fréquence et les tests de bon niveau sont importants en réception.

## 6. Blindage, bonding et perturbations

Le blindage doit être conçu comme un système complet : câble, prise, panneau, cordons, équipement et infrastructure de bonding/earthing selon les normes applicables. Ne fais pas un raccordement de blindage improvisé et ne déduis pas les obligations de terre d'une seule couleur de gaine.

Pour réduire les perturbations et préserver les performances :

- planifier la séparation avec les circuits de puissance selon le code électrique et la nature du parcours ;
- éviter les croisements prolongés parallèles non prévus avec des câbles d'énergie ;
- respecter la capacité de remplissage et la fixation du chemin de câbles ;
- utiliser les rayons de courbure et efforts de traction du fabricant ;
- maintenir les torsades au plus près de la terminaison, dans les limites spécifiées ;
- éviter les écrasements, les angles serrés et les faisceaux excessivement comprimés.

Il n'existe pas de distance universelle à appliquer aveuglément entre toutes les catégories de câbles et toutes les installations électriques : les règles dépendent du type de câblage, de la présence de séparateurs, du parcours et du code local.

## 7. PoE et dimensionnement des faisceaux

PoE combine données et alimentation électrique dans un système Ethernet compatible. Le concepteur doit calculer le budget de puissance, le niveau demandé par les terminaux, le budget du PSE et les pertes. Les puissances annoncées côté source ne sont pas toutes livrées au terminal.

À haut niveau de puissance, plusieurs câbles groupés peuvent chauffer. Les facteurs comprennent le calibre du conducteur, le type d'isolant, la taille et le serrage du faisceau, la température ambiante, le chemin de câbles et les conditions de dissipation. Suivre la conception du fabricant et les exigences normatives ; éviter le cuivre de qualité inconnue ou les conducteurs CCA lorsque l'application exige les caractéristiques d'un câble cuivre conforme.

## 8. Fibres : choisir OM/OS et les optiques ensemble

| Famille | Type | Notes de conception |
|---|---|---|
| OM3 / OM4 / OM5 | Multimode | Portée et débit dépendent des caractéristiques précises de fibre et de l'application optique retenue |
| OS2 | Monomode | Appropriée à de nombreuses liaisons de backbone et portées plus longues avec transceivers compatibles |

N'invente pas une distance d'usage à partir du seul nom du type de fibre. La portée Ethernet varie selon la norme PHY, le débit, la longueur d'onde et la fiche du transceiver. Vérifie également les nombres de fibres, le schéma de polarité, les connecteurs, le type de polissage, les tiroirs optiques et les conditions extérieures/intérieures.

### Calcul de budget optique — exemple pédagogique

La puissance reçue dépend de la puissance émise et de toutes les pertes du trajet :

`P_rx (dBm) = P_tx (dBm) - pertes totales (dB)`

Les pertes totales comprennent au minimum l'atténuation de la fibre sur la distance, les connecteurs, les épissures et les autres événements pertinents. Compare le résultat aux limites de puissance du transceiver, à sa sensibilité et à sa puissance d'entrée maximale, en gardant une marge d'ingénierie approuvée. Les valeurs numériques exactes doivent venir des fiches techniques et de la méthode de test de la liaison réelle.

## 9. Inspection et nettoyage des connecteurs optiques

La contamination des faces optiques est une cause fréquente de défaut. La règle pratique est **Inspecter → nettoyer si nécessaire → inspecter de nouveau**. Inspecte les deux faces et l'adaptateur avant accouplement. Utilise les outils et solvants prévus pour la fibre, sans toucher les faces ni réutiliser les consommables contaminés.

Ne regarde pas directement dans une fibre ou un port optique. Utilise un microscope d'inspection adapté et les précautions du fabricant.

## 10. Réception et certification des liens

Une procédure de réception professionnelle précise :

1. **Le modèle testé :** lien permanent, canal, ou autre configuration reconnue du système de câblage.
2. **La limite d'essai :** exactement celle définie au contrat, par exemple la classe/catégorie cible selon la norme du projet.
3. **L'équipement :** certificateur adapté, logiciel, adaptateurs, calibration et paramètres de test corrects.
4. **L'identification :** même identifiant aux deux extrémités et dans le registre du bâtiment.
5. **Les preuves :** rapport brut, date, opérateur, résultats et corrections appliquées.
6. **La recette :** critères PASS/FAIL écrits, gestion des échecs et procédure de retest après réparation.

Un test de continuité, un test de qualification et une certification ne sont pas équivalents. Pour la fibre, une mesure de perte d'insertion (OLTS) et une mesure OTDR répondent à des besoins différents ; les méthodes et les exigences exactes doivent être précisées pour la réception.

## 11. Schéma animé — procédure de recette

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 330" role="img" aria-labelledby="cabint2t cabint2d">
<title id="cabint2t">Flux de réception d'un câblage structuré</title><desc id="cabint2d">Le technicien identifie le lien, inspecte les terminaisons, effectue le test correspondant à la limite d'essai, documente le résultat et corrige puis reteste les échecs.</desc>
<defs><marker id="cabint2a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#62d6bf"/></marker><style>.cabint2bg{fill:#0b1220}.cabint2p{fill:#17243a;stroke:#3c506f;stroke-width:1.5}.cabint2h{fill:#f5f8fc;font:700 15px sans-serif}.cabint2x{fill:#cbd5e1;font:12px sans-serif}.cabint2f{fill:none;stroke:#62d6bf;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#cabint2a);animation:cabint2flow 1.8s linear infinite}@keyframes cabint2flow{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.cabint2f{animation:none}}</style></defs>
<rect class="cabint2bg" width="940" height="330" rx="18"/><text class="cabint2h" x="24" y="32">Recette : de l'identification à l'acceptation documentaire</text>
<rect class="cabint2p" x="22" y="76" width="160" height="100" rx="10"/><text class="cabint2h" x="102" y="106" text-anchor="middle">1. Identifier</text><text class="cabint2x" x="102" y="131" text-anchor="middle">Lien, extrémités,</text><text class="cabint2x" x="102" y="150" text-anchor="middle">catégorie / classe</text>
<rect class="cabint2p" x="210" y="76" width="160" height="100" rx="10"/><text class="cabint2h" x="290" y="106" text-anchor="middle">2. Inspecter</text><text class="cabint2x" x="290" y="131" text-anchor="middle">Terminaisons,</text><text class="cabint2x" x="290" y="150" text-anchor="middle">connecteurs, pose</text>
<rect class="cabint2p" x="398" y="76" width="160" height="100" rx="10"/><text class="cabint2h" x="478" y="106" text-anchor="middle">3. Tester</text><text class="cabint2x" x="478" y="131" text-anchor="middle">Limite correcte,</text><text class="cabint2x" x="478" y="150" text-anchor="middle">adaptateurs calibrés</text>
<rect class="cabint2p" x="586" y="76" width="160" height="100" rx="10"/><text class="cabint2h" x="666" y="106" text-anchor="middle">4. Documenter</text><text class="cabint2x" x="666" y="131" text-anchor="middle">Rapport + identifiant,</text><text class="cabint2x" x="666" y="150" text-anchor="middle">date et opérateur</text>
<rect class="cabint2p" x="774" y="76" width="144" height="100" rx="10"/><text class="cabint2h" x="846" y="106" text-anchor="middle">5. Accepter</text><text class="cabint2x" x="846" y="131" text-anchor="middle">PASS conforme</text><text class="cabint2x" x="846" y="150" text-anchor="middle">ou actions</text>
<path class="cabint2f" d="M182 126 H210"/><path class="cabint2f" d="M370 126 H398"/><path class="cabint2f" d="M558 126 H586"/><path class="cabint2f" d="M746 126 H774"/>
<path class="cabint2f" d="M846 176 V226 H478 V176"/><rect x="276" y="229" width="404" height="60" rx="9" fill="#3b2527" stroke="#a85555"/><text x="478" y="253" text-anchor="middle" fill="#fecaca" font="700 14px sans-serif">FAIL → rechercher la cause → réparer → retester</text><text x="478" y="273" text-anchor="middle" fill="#e5caca" font="12px sans-serif">Conserver les mesures d'origine et de retest dans le dossier du lien</text></svg>

## 12. Atelier intermédiaire — recette d'un étage

Un étage possède 48 prises cuivre et deux liaisons fibre vers le local central. Construis le dossier de réception suivant :

- matrice des prises par salle et des ports de panneau ;
- nomenclature des câbles, prises, panneaux, cordons et chemins ;
- standard de câblage et édition contractuelle retenus ;
- modèle exact du test (lien permanent/canal), limite choisie et configuration de l'appareil ;
- procédure de repérage, test, correction et retest ;
- résultats cuivre ;
- résultats optiques comprenant la méthode, les longueurs d'onde et les limites applicables ;
- plans de récolement, photos des baies et liste des réserves.

La recette doit distinguer les défauts de performance d'un simple défaut administratif (identifiant absent, rapport mal nommé) : tous deux doivent être corrigés, mais pas de la même manière.

## 13. Contrôle rapide avant réception

- [ ] Câble, prises, panneau et cordons répondent à la classe/catégorie cible.
- [ ] Le canal et les limites de longueur sont vérifiés.
- [ ] Les rayons, tractions, fixations et chemins respectent les spécifications de pose.
- [ ] Les parcours et pénétrations répondent aux règles de construction et de sécurité incendie.
- [ ] Les tests utilisent la bonne limite et le bon type de lien.
- [ ] Tous les liens ont un identifiant unique documenté.
- [ ] Les liens optiques ont été inspectés, nettoyés si besoin et retestés.
- [ ] Les rapports et plans de récolement ont été remis.

## 14. Références techniques

- [ISO/IEC 11801-1 et amendement 1:2025](https://www.iso.org/standard/93480.html).
- [ANSI/TIA-568.2-E, câble cuivre, version publiée en 2024](https://tiaonline.org/standardannouncement/tia-publishes-new-standards-ansi-tia-568-2-e-and-ansi-tia-568-5-1/).
- [ANSI/TIA-568.3-E, fibre optique](https://tiaonline.org/standardannouncement/tia-issues-updated-optical-fiber-cabling-component-standard-ansi-tia-568-3-e/).
- [ANSI/TIA-569-E, chemins et locaux télécom](https://tiaonline.org/standard/tia-569/).
- [Fluke Networks — inspection et nettoyage optiques](https://fr.flukenetworks.com/edocs/wp-fiber-cleaning-and-inspection-white-paper).

**Suite :** `cabling-expert.md` — conception avancée, gestion du risque, calcul optique, contrôle documentaire et mise en service à l'échelle d'un campus.
