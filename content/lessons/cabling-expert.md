# Câblage réseau et normes — Niveau expert

> **Fichier :** `cabling-expert.md`  
> **Parcours :** 3/3 — concevoir, spécifier, gouverner et auditer l'infrastructure physique à l'échelle d'un campus ou d'un datacenter.  
> **Prérequis :** maîtriser les familles de câble, l'architecture horizontale/backbone, la terminologie de certification cuivre et les bases de mesure optique.  
> **Objectif :** traduire les exigences de service et de bâtiment en une spécification testable, analyser les risques, contrôler les travaux et produire un dossier d'infrastructure maintenable.


## 1. L'expert conçoit un système complet

Le choix d'un câble à lui seul ne définit pas une infrastructure conforme. La performance finale dépend des composants, du canal, des terminaisons, du cheminement, de l'environnement, du raccordement équipotentiel/bonding lorsque requis, du choix des matériaux pour le feu, de l'identification et des méthodes de validation.

Un dossier professionnel doit donc séparer :

1. **Exigences d'application :** débits, PoE, disponibilité, environnement, durée de vie, extensions.
2. **Normes de câblage :** famille ISO/IEC ou ANSI/TIA, édition et limites de test contractuelles.
3. **Exigences de construction :** locaux, chemins, séparation, pénétrations, support, protection incendie et règles électriques locales.
4. **Spécification des composants :** performance, environnement, connectique, résistance mécanique, gaine et traçabilité.
5. **Méthode d'installation :** tirage, manutention, repérage, terminaisons, inspection et contrôle qualité.
6. **Essais et critères d'acceptation :** limites, appareils, adaptateurs, calibration, rapports et procédure de retest.
7. **Livrables :** plans de récolement, registre de liens, rapports, photos, garanties et procédures de dépannage.

## 2. Les normes : déterminer lesquelles s'appliquent réellement

Le premier geste d'expert n'est pas de réciter un numéro de norme : c'est de déterminer le référentiel contractuel et les obligations légales du site.

| Référence | Portée générale | À quoi elle sert dans le projet |
|---|---|---|
| ISO/IEC 11801 (série) | Câblage générique des locaux d'utilisateurs | Architecture et exigences génériques, selon la partie et l'amendement applicables |
| ANSI/TIA-568.0 / 568.1 | Principes de câblage générique et infrastructure de bâtiment commercial dans le cadre TIA | Architecture et exigences de conception selon le scope de chaque document |
| ANSI/TIA-568.2-E (2024) | Câblage cuivre équilibré et composants | Performance des liaisons et composants cuivre dans son champ d'application |
| ANSI/TIA-568.3-E (2022) | Câblage fibre optique et composants | Conception des liaisons et composants optiques selon le champ du standard |
| ANSI/TIA-569-E | Chemins et espaces télécom | Locaux, chemins, conduits et planification des espaces |
| ANSI/TIA-606-D | Administration du câblage | Identifiants, registres, étiquetage et relations entre composants |
| ANSI/TIA-607-E (2024) | Bonding et earthing de l'infrastructure télécom | Infrastructure de liaison équipotentielle et son intégration, selon le contexte applicable |
| IEEE 802.3 (et amendements pertinents) | Technologie Ethernet et PHY/MAC, diverses fonctions selon les amendements | Compatibilité de l'application Ethernet, du PoE et du matériel actif |
| IEC 60332 (série) | Méthodes d'essai de propagation de flamme sur câbles | Comprendre l'essai feu correspondant ; il ne remplace pas les règles de construction locales |

ISO/IEC et ANSI/TIA sont des référentiels différents, bien qu'ils couvrent plusieurs sujets proches. Ne mélange pas leurs catégories ou limites d'essai comme si elles étaient automatiquement interchangeables. La norme demandée pour la conception, le matériel et la certification doit être explicite dans la spécification.

Les normes complètes sont fréquemment payantes. Vérifie l'édition officielle en vigueur au moment de la consultation et l'édition incorporée au contrat. Une norme volontaire peut devenir obligatoire parce qu'elle est référencée par un contrat, un code ou un règlement ; l'effet juridique dépend du pays et du projet.

## 3. Ingénierie du cuivre hautes performances

### 3.1. Concevoir Cat 6A pour 10GBASE-T

Lorsque le besoin de conception est 10GBASE-T jusqu'à 100 m sur cuivre, Cat 6A constitue le choix classique de câblage structuré adapté, sous réserve que le lien complet réponde au référentiel retenu. Il faut préciser la classe/catégorie visée, les composants, le type de lien à tester, les limites de réception et la qualité documentaire attendue.

Cat 6 peut prendre en charge des usages 10GBASE-T sur certaines portées plus courtes et dans certaines conditions, mais ne doit pas être spécifié comme un remplacement automatique de Cat 6A sur 100 m.

### 3.2. Paramètres à surveiller

- perte d'insertion et perte de retour ;
- NEXT/PSNEXT et ACR-F/PSACR-F ;
- longueur, délai de propagation et déséquilibre du délai ;
- continuité du blindage lorsqu'il est présent et applicable ;
- alien crosstalk dans les architectures où l'environnement l'exige ;
- performance après installation, et non seulement les caractéristiques commerciales de la bobine.

### 3.3. PoE, faisceaux et température

Le dimensionnement PoE doit couvrir la puissance requise au terminal, le budget du PSE, les pertes du canal et l'environnement thermique. Des faisceaux denses et de grande puissance peuvent augmenter la température des conducteurs et affecter les marges de transmission. L'expert doit vérifier les règles de regroupement et de température applicables à la famille de câble, le diamètre des conducteurs, la ventilation, les chemins et la recommandation du fabricant.

N'utilise pas une formule unique de déclassement thermique comme substitut à une conception documentée : il faut s'appuyer sur le standard pertinent, les caractéristiques du produit, le faisceau réel et les conditions d'installation.

### 3.4. Blindage, equipotentialité et sécurité électrique

Le blindage exige la compatibilité de bout en bout et une conception appropriée de bonding/earthing. Une terminaison non prévue peut annuler l'avantage recherché ou créer des défauts. Les travaux de terre et les liaisons à l'infrastructure électrique doivent être effectués par du personnel compétent selon le code local ; l'expert réseau ne doit pas improviser des pontages électriques.

## 4. Fibre optique : choix, marge optique et mesures

### 4.1. Choisir le type de fibre et le transceiver comme un couple

OM3, OM4 et OM5 sont des familles de fibres multimodes ; OS2 est une famille de monomode utilisée dans de nombreuses applications de backbone. Ces désignations ne suffisent pas à déterminer la portée opérationnelle. Vérifie la norme PHY, le débit, la longueur d'onde, la classe exacte de fibre, la perte admissible, les connecteurs et la fiche du transceiver.

Pour une liaison bâtiment à bâtiment, considérer notamment :

- fibre adaptée à la pose intérieure, extérieure ou mixte ;
- nombre de fibres et croissance prévue ;
- possibilité d'ajouter ou de réparer par épissure ;
- armure, protection anti-rongeurs, résistance à l'eau et contraintes mécaniques si exigées ;
- transition intérieure/extérieure, mise à la terre d'éléments métalliques et protection contre la foudre selon le projet ;
- tiroirs, boîtiers, connecteurs, polarité et réserves de fibre ;
- accessibilité pour inspection et maintenance.

Une fibre monomode extérieure et un cordon monomode intérieur ne sont pas automatiquement interchangeables du point de vue mécanique ou réglementaire, même si la classification optique semble proche. La gaine doit être adaptée à l'environnement.

### 4.2. Budget de perte optique

La formule d'ingénierie de base est :

`Puissance reçue (dBm) = Puissance émise (dBm) - perte totale (dB)`

La perte totale vient notamment de l'atténuation de la fibre par longueur, des connecteurs, des épissures, des répartiteurs et des événements prévus dans l'architecture.

**Exemple purement pédagogique :** si un lien présente 2,4 dB de pertes totales et que l'émetteur délivre `-2 dBm`, le niveau calculé en réception est `-4,4 dBm`. Ce chiffre doit ensuite être comparé aux limites minimale et maximale acceptables du récepteur et au budget de l'optique réelle. L'exemple n'est pas une cible universelle.

Le budget minimum ne suffit pas à conclure. Il faut aussi contrôler l'éblouissement éventuel par une puissance reçue trop forte, le seuil de surcharge du récepteur, les marges en vieillissement et réparation, et les règles de l'application. Documente les hypothèses : longueur, nombre de connecteurs, nombre d'épissures, longueur d'onde et limites du transceiver.

### Schéma animé — chaîne de mesure et budget optique

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 355" role="img" aria-labelledby="cabex1t cabex1d">
<title id="cabex1t">Budget optique d'une liaison fibre</title><desc id="cabex1d">Un émetteur optique traverse un connecteur, une fibre et une épissure avant d'atteindre le récepteur. Les pertes de chaque élément s'additionnent et la puissance reçue est comparée aux limites du transceiver.</desc>
<defs><marker id="cabex1a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#a78bfa"/></marker><style>.cabex1bg{fill:#0b1220}.cabex1p{fill:#19243b;stroke:#455776;stroke-width:1.5}.cabex1h{fill:#f5f8fc;font:700 16px sans-serif}.cabex1x{fill:#cbd5e1;font:13px sans-serif}.cabex1s{fill:#a4b5cc;font:12px sans-serif}.cabex1f{fill:none;stroke:#a78bfa;stroke-width:3;stroke-dasharray:9 8;marker-end:url(#cabex1a);animation:cabex1flow 1.9s linear infinite}@keyframes cabex1flow{to{stroke-dashoffset:-34}}@media(prefers-reduced-motion:reduce){.cabex1f{animation:none}}</style></defs>
<rect class="cabex1bg" width="960" height="355" rx="18"/><text class="cabex1h" x="24" y="32">Du lancement du signal à la mesure en réception</text>
<rect class="cabex1p" x="24" y="77" width="155" height="105" rx="11"/><text class="cabex1h" x="101" y="110" text-anchor="middle">Transceiver TX</text><text class="cabex1x" x="101" y="137" text-anchor="middle">Puissance émise</text><text class="cabex1s" x="101" y="158" text-anchor="middle">dBm</text>
<rect class="cabex1p" x="215" y="77" width="140" height="105" rx="11"/><text class="cabex1h" x="285" y="110" text-anchor="middle">Connecteur</text><text class="cabex1x" x="285" y="137" text-anchor="middle">Perte d'insertion</text><text class="cabex1s" x="285" y="158" text-anchor="middle">dB</text>
<rect class="cabex1p" x="391" y="77" width="168" height="105" rx="11"/><text class="cabex1h" x="475" y="110" text-anchor="middle">Fibre optique</text><text class="cabex1x" x="475" y="137" text-anchor="middle">Longueur × atténuation</text><text class="cabex1s" x="475" y="158" text-anchor="middle">dB</text>
<rect class="cabex1p" x="595" y="77" width="140" height="105" rx="11"/><text class="cabex1h" x="665" y="110" text-anchor="middle">Épissure</text><text class="cabex1x" x="665" y="137" text-anchor="middle">Perte mesurée</text><text class="cabex1s" x="665" y="158" text-anchor="middle">dB</text>
<rect class="cabex1p" x="771" y="77" width="165" height="105" rx="11"/><text class="cabex1h" x="853" y="110" text-anchor="middle">Transceiver RX</text><text class="cabex1x" x="853" y="137" text-anchor="middle">Puissance reçue</text><text class="cabex1s" x="853" y="158" text-anchor="middle">dBm</text>
<path class="cabex1f" d="M179 129 H215"/><path class="cabex1f" d="M355 129 H391"/><path class="cabex1f" d="M559 129 H595"/><path class="cabex1f" d="M735 129 H771"/>
<rect x="24" y="218" width="912" height="99" rx="11" fill="#182b35" stroke="#377181"/><text x="46" y="246" fill="#a5f3fc" font="700 15px sans-serif">Calcul et acceptation</text><text class="cabex1x" x="46" y="273">P_rx = P_tx − Σ pertes (dB)</text><text class="cabex1x" x="46" y="296">Comparer au budget et à la sensibilité/surcharge du récepteur réel, avec marge d'ingénierie documentée.</text></svg>

## 5. Méthodes d'essai fibre : OLTS et OTDR

**OLTS / source + photomètre :** mesure la perte d'insertion de bout en bout avec la méthode de référence, la longueur d'onde et les cordons de référence définis. C'est un type de mesure essentiel pour l'acceptation de la perte du lien.

**OTDR :** analyse les événements le long de la fibre, fournit une estimation de leur position et de leur perte/réflexion selon les conditions de mesure. Les zones mortes, les cordons d'amorce et de réception, l'indice de réfraction configuré et la méthode de lecture doivent être pris en compte.

Ces essais ne sont pas substituables sans nuance : un rapport OTDR ne remplace pas automatiquement les critères d'acceptation de perte de bout en bout, et un OLTS ne localise pas toujours le défaut. Précise le test requis dans le contrat.

Avant le raccordement : inspecter les faces, nettoyer si nécessaire, inspecter à nouveau, puis connecter. Ne jamais regarder dans le cœur d'une fibre ou d'un port optique.

## 6. Incendie, environnement de pose et réglementation

La classification de gaine doit correspondre à l'usage : intérieur, extérieur, conduit, élévation, environnement industriel, plénum ou autre espace spécifique selon le code concerné. LSZH, CM/CMR/CMP, réaction au feu CPR et classifications locales ne sont pas des synonymes ; leur application dépend du pays, de l'usage et des textes juridiquement applicables.

IEC 60332-1-2:2025 spécifie un essai de propagation verticale de flamme sur un câble individuel dans des conditions d'essai définies. L'essai d'un câble individuel ne prouve pas à lui seul le comportement d'un faisceau de câbles. Pour un risque d'incendie élevé, examiner les essais de câbles en faisceau, les spécifications du bâtiment et les systèmes de calfeutrement coupe-feu requis.

Les règles de séparation avec les câbles d'énergie, les limites de remplissage des chemins, le rayon de courbure, la traction, le support mécanique, la protection contre l'eau et le feu doivent provenir du référentiel applicable et du fabricant. Ne fixe pas une distance universelle de séparation sans contexte.

## 7. Exemple de spécification technique à intégrer au marché

Une spécification d'appel d'offres devrait préciser au minimum :

- normes et éditions contractuelles ;
- performance du canal attendu et type de lien à certifier ;
- catégories/classes des câbles cuivre et composants ;
- types de fibre, nombres de brins, connecteurs, polissage, polarité et classes de gaine ;
- exigences PoE et calcul des budgets de puissance ;
- environnement et réglementation incendie pour chaque parcours ;
- règles de pose, fixations, séparation, traction et courbure ;
- système d'étiquetage et format du registre des liens ;
- équipements et méthodes de test, limites, rapports et procédure de retest ;
- critères d'acceptation des plans de récolement et réserves ;
- dossiers à remettre, formation de l'exploitant et exigences de garantie.

Éviter les formules vagues comme « câble de haute qualité » ou « certifié Cat 6A » si les critères de composants, de lien, d'essai et de preuve ne sont pas spécifiés.

## 8. Administration et repérage avec une méthode maintenable

Un identifiant doit rester univoque et suivre une convention documentée, par exemple :

`SITE-BATIMENT-LOCAL-PANNEAU-PORT ↔ ETAGE-SALLE-PRISE`

Exemple pédagogique :

`DLA-B1-TR02-PP03-024 ↔ DLA-B1-L2-S205-TO-A`

Le même identifiant logique doit être retrouvé dans :

- le label physique ;
- les plans de récolement ;
- le registre IPAM ou CMDB si intégré ;
- le rapport de certification ;
- les fiches d'intervention et de changement.

Les conventions de nommage doivent être définies par le projet ; l'exemple n'est pas une convention officielle universelle.

## 9. Schéma animé — traçabilité et boucle d'amélioration

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 330" role="img" aria-labelledby="cabex2t cabex2d">
<title id="cabex2t">Traçabilité de la conception à l'exploitation</title><desc id="cabex2d">Les plans et la nomenclature guident la pose, qui est inspectée et testée. Les résultats sont archivés et remis à l'exploitation ; les changements maintiennent les dossiers à jour.</desc>
<defs><marker id="cabex2a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#5bd5bd"/></marker><style>.cabex2bg{fill:#0b1220}.cabex2p{fill:#18243a;stroke:#455978;stroke-width:1.5}.cabex2h{fill:#f5f8fc;font:700 15px sans-serif}.cabex2x{fill:#cbd5e1;font:12px sans-serif}.cabex2f{fill:none;stroke:#5bd5bd;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#cabex2a);animation:cabex2flow 1.8s linear infinite}@keyframes cabex2flow{to{stroke-dashoffset:-31}}@media(prefers-reduced-motion:reduce){.cabex2f{animation:none}}</style></defs>
<rect class="cabex2bg" width="960" height="330" rx="18"/><text class="cabex2h" x="24" y="31">Traçabilité : chaque lien reste vérifiable après la remise du chantier</text>
<rect class="cabex2p" x="22" y="73" width="169" height="91" rx="10"/><text class="cabex2h" x="106" y="103" text-anchor="middle">Concevoir</text><text class="cabex2x" x="106" y="128" text-anchor="middle">Plans + normes</text><text class="cabex2x" x="106" y="145" text-anchor="middle">+ nomenclature</text>
<rect class="cabex2p" x="211" y="73" width="169" height="91" rx="10"/><text class="cabex2h" x="295" y="103" text-anchor="middle">Installer</text><text class="cabex2x" x="295" y="128" text-anchor="middle">Pose + labels</text><text class="cabex2x" x="295" y="145" text-anchor="middle">+ photos</text>
<rect class="cabex2p" x="400" y="73" width="169" height="91" rx="10"/><text class="cabex2h" x="484" y="103" text-anchor="middle">Tester</text><text class="cabex2x" x="484" y="128" text-anchor="middle">Cuivre / optique</text><text class="cabex2x" x="484" y="145" text-anchor="middle">+ rapports</text>
<rect class="cabex2p" x="589" y="73" width="169" height="91" rx="10"/><text class="cabex2h" x="673" y="103" text-anchor="middle">Réceptionner</text><text class="cabex2x" x="673" y="128" text-anchor="middle">Réserves et</text><text class="cabex2x" x="673" y="145" text-anchor="middle">critères PASS</text>
<rect class="cabex2p" x="778" y="73" width="160" height="91" rx="10"/><text class="cabex2h" x="858" y="103" text-anchor="middle">Exploiter</text><text class="cabex2x" x="858" y="128" text-anchor="middle">Registre +</text><text class="cabex2x" x="858" y="145" text-anchor="middle">changements</text>
<path class="cabex2f" d="M191 118 H211"/><path class="cabex2f" d="M380 118 H400"/><path class="cabex2f" d="M569 118 H589"/><path class="cabex2f" d="M758 118 H778"/>
<path class="cabex2f" d="M858 164 V220 H106 V164"/><rect x="267" y="222" width="426" height="70" rx="10" fill="#112f36" stroke="#377a78"/><text x="480" y="248" fill="#a7f3e8" font="700 14px sans-serif" text-anchor="middle">Boucle de mise à jour</text><text class="cabex2x" x="480" y="269" text-anchor="middle">Toute modification produit une mise à jour du registre,</text><text class="cabex2x" x="480" y="285" text-anchor="middle">des plans et des références de tests.</text></svg>

## 10. Audit final avant mise en service

- [ ] Les normes et éditions contractuelles sont écrites noir sur blanc.
- [ ] Tous les composants du canal sont identifiés et conformes au besoin.
- [ ] Les chemins, locaux, capacités de support et pénétrations sont validés.
- [ ] La protection au feu et la séparation de l'énergie respectent les règles applicables au site.
- [ ] Les exigences de bonding sont prises en charge par le corps de métier compétent.
- [ ] Le PoE est dimensionné pour puissance, faisceau et environnement.
- [ ] Les liens cuivre utilisent le bon test, la bonne limite et des rapports conservés.
- [ ] La fibre est inspectée et nettoyée selon le besoin ; les mesures OLTS/OTDR sont choisies selon le contrat.
- [ ] Les noms de lien correspondent au repérage physique, aux rapports et aux plans.
- [ ] Les défauts ont un propriétaire, une action de correction et un rapport de retest.
- [ ] L'exploitant reçoit le registre, les plans de récolement et la procédure de changement.

## 11. Références techniques

- [ISO/IEC 11801-1 — édition 2017 et amendement 1:2025](https://www.iso.org/standard/93480.html) ; vérifier les corrigenda applicables dans le registre ISO/IEC.
- [ANSI/TIA-568.2-E — câble cuivre, édition publiée en 2024](https://tiaonline.org/standardannouncement/tia-publishes-new-standards-ansi-tia-568-2-e-and-ansi-tia-568-5-1/).
- [ANSI/TIA-568.3-E — fibre optique, édition publiée en 2022](https://tiaonline.org/standardannouncement/tia-issues-updated-optical-fiber-cabling-component-standard-ansi-tia-568-3-e/).
- [ANSI/TIA-569-E — chemins et espaces télécom](https://tiaonline.org/standard/tia-569/).
- [ANSI/TIA-607-E — bonding et earthing télécom](https://tiaonline.org/standardannouncement/tia-publishes-new-standard-ansi-tia-607-e-generic-telecommunications-bonding-and-grounding-earthing-for-customer-premises/).
- [IEC 60332-1-2:2025 — essai de propagation verticale de flamme](https://webstore.iec.ch/en/publication/80873).
- [Fluke Networks — inspection/nettoyage optique](https://fr.flukenetworks.com/edocs/wp-fiber-cleaning-and-inspection-white-paper).


**Fin de la série :** `cabling-debutant.md` → `cabling-intermediaire.md` → `cabling-expert.md`.
