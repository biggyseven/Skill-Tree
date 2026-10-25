# OSPFv2 — Niveau Intermédiaire

**Durée indicative :** 4 à 6 heures, hors répétition des laboratoires.  
**Prérequis :** maîtriser `ospf-debutant.md` : Router ID, paquets OSPFv2, états de voisinage, LSDB, SPF, métrique, DR/BDR et configuration d’une aire unique.  
**Environnement recommandé :** Packet Tracer pour les notions compatibles ; idéalement une maquette Cisco IOS/IOS XE ou un émulateur qui prend en charge plusieurs aires OSPF ; Wireshark pour examiner les paquets et LSA.

Ce cours est la **suite directe de `ospf-debutant.md`**. Les bases ne sont pas reprises pas à pas. Le niveau débutant apprenait comment OSPF découvre un voisin et calcule un chemin dans une aire. Ici, on examine ce qui change quand le domaine est découpé en plusieurs aires : frontières ABR/ASBR, portée des LSA, types d’aires, agrégation, métriques externes et dépannage à travers les frontières. Le niveau Expert approfondira ensuite l’ingénierie de convergence, l’optimisation à grande échelle, la sécurité opérationnelle, les migrations et l’analyse des incidents complexes.

> **Convention technique :** les commandes sont des exemples Cisco IOS/IOS XE et les préfixes sont des adresses de documentation. Le comportement précis de certaines options (notamment les aires totalement stub, les filtres, l’authentification et les commandes de résumé) varie selon la plateforme et la version. Valide toujours la syntaxe avec l’aide CLI et le guide de la version utilisée.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :

- concevoir une topologie multi-aires qui respecte le rôle du backbone Area 0 ;
- distinguer routeur interne, ABR et ASBR sans confondre leur fonction ;
- lire les LSA de types 1 à 5 et expliquer le rôle du type 7 dans une NSSA ;
- anticiper les effets d’une aire stub, NSSA ou d’une variante totalement stub ;
- configurer un résumé inter-aire et reconnaître les risques de résumés trop larges ;
- comprendre les routes externes E1 et E2 ;
- expliquer le fonctionnement des virtual links et leurs limites ;
- diagnostiquer une route manquante en séparant voisinage, LSDB, ABR/ASBR, sélection de route et plan de données ;
- produire un dossier de laboratoire reproductible, avec preuve avant/après et procédure de retour arrière.

## Utiliser les schémas

Les schémas SVG sont inclus directement dans le fichier Markdown : aucun répertoire d’images ni fichier séparé n’est nécessaire. Chaque animation représente un parcours logique indiqué par une liaison visible. Les points animés ne constituent pas une capture exacte de paquets ni un chronométrage protocolaire. Si ton lecteur neutralise les animations SVG, la topologie statique reste lisible ; tu peux aussi ouvrir le bloc SVG dans un navigateur récent.


## 1. Ce qui change lorsqu’OSPF passe à plusieurs aires

### 1.1 Pourquoi ne pas conserver un seul grand domaine ?

Dans une petite topologie, une aire unique simplifie le modèle mental : les routeurs de cette aire partagent une LSDB décrivant la topologie de l’aire et calculent leurs arbres SPF à partir de cette information. Quand le domaine grandit, la quantité de liens, de routeurs et de changements de topologie augmente. Une modification peut déclencher davantage de diffusion et de calcul, même dans des parties éloignées du réseau où seule une information de destination serait suffisante.

La conception multi-aires permet de limiter la connaissance détaillée de la topologie à des zones de routage et de diffuser des informations de résumé entre elles. Cela peut améliorer l’évolutivité opérationnelle, réduire le volume d’informations topologiques détaillées hors de l’aire source et permettre une agrégation plus lisible des préfixes. Ce bénéfice n’est pas automatique : une mauvaise frontière, un plan d’adressage non agrégable ou des résumés trop larges peuvent rendre le diagnostic plus difficile.

### 1.2 Le backbone Area 0 est une structure, pas simplement un numéro

L’aire 0, ou `0.0.0.0`, est le backbone OSPFv2. Les informations inter-aires sont échangées en s’appuyant sur ce backbone. Dans une conception normale, chaque aire non-backbone doit être reliée à Area 0 par un ABR. Il faut donc concevoir la topologie logique pour que cette relation soit explicite et stable.

Un identifiant d’aire différent ne crée pas automatiquement une séparation physique. C’est l’association des interfaces et liens OSPF à chaque aire qui détermine la structure. Un réseau/IP partagé appartient à une aire OSPF sur l’interface correspondante ; évite de placer un même segment ambigu dans plusieurs aires sans une conception et une prise en charge spécifiques.

### Schéma 1 — Architecture multi-aires et rôle des ABR

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="520" viewBox="0 0 1040 520" role="img" aria-label="OSPF multi-aires : rôle des ABR" style="display:block;width:100%;max-width:1040px;height:auto;font-family:Inter,Arial,sans-serif">
<defs>
 <marker id="arrC31" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#43c7f5"/></marker>
 <marker id="arrG31" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#4ade80"/></marker>
 <marker id="arrA31" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/></marker>
 <marker id="arrR31" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fb7185"/></marker>
 <filter id="glow31" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1040" height="520" rx="18" fill="#0b1220"/>
<text x="26" y="32" fill="#edf5ff" font-size="22" font-weight="700">OSPF multi-aires : rôle des ABR</text>
<text x="27" y="56" fill="#a7bad0" font-size="13">Chaque aire possède sa LSDB ; les ABR relient le backbone aux aires non-backbone.</text>
<line x1="26" y1="73" x2="1014" y2="73" stroke="#334960" stroke-width="1.5"/>
<rect x="35" y="100" width="350" height="330" rx="16" fill="#10291f" stroke="#2b7152" stroke-width="1.5"/><text x="55" y="126" fill="#86efac" font-size="16" font-weight="700">AREA 10 — SITE A</text><rect x="365" y="100" width="335" height="330" rx="16" fill="#102239" stroke="#316a95" stroke-width="1.5"/><text x="390" y="126" fill="#7dd3fc" font-size="16" font-weight="700">AREA 0 — BACKBONE</text><rect x="685" y="100" width="320" height="330" rx="16" fill="#251c3a" stroke="#7054a0" stroke-width="1.5"/><text x="705" y="126" fill="#ddd6fe" font-size="16" font-weight="700">AREA 20 — SITE B</text><path d="M155 245 L190 245" fill="none" stroke="#4ade80" stroke-width="4"/><path d="M300 245 L330 245" fill="none" stroke="#4ade80" stroke-width="4"/><path d="M440 245 L475 245" fill="none" stroke="#43c7f5" stroke-width="4"/><path d="M585 245 L630 245" fill="none" stroke="#43c7f5" stroke-width="4"/><path d="M740 245 L770 245" fill="none" stroke="#c4b5fd" stroke-width="4"/><path d="M880 245 L900 245" fill="none" stroke="#c4b5fd" stroke-width="4"/><rect x="50" y="205" width="105" height="80" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="102.5" y="231" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">LAN A</text><text x="102.5" y="252" text-anchor="middle" fill="#a7bad0" font-size="12">10.10.10.0/24</text><rect x="190" y="202" width="110" height="86" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="245.0" y="228" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">R10</text><text x="245.0" y="249" text-anchor="middle" fill="#a7bad0" font-size="12">RID 10.10.10.10</text><rect x="330" y="202" width="110" height="86" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="385.0" y="228" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">ABR-A</text><text x="385.0" y="249" text-anchor="middle" fill="#a7bad0" font-size="12">Area 10 + 0</text><rect x="475" y="202" width="110" height="86" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="530.0" y="228" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">R0</text><text x="530.0" y="249" text-anchor="middle" fill="#a7bad0" font-size="12">Area 0 only</text><rect x="630" y="202" width="110" height="86" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="685.0" y="228" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">ABR-B</text><text x="685.0" y="249" text-anchor="middle" fill="#a7bad0" font-size="12">Area 0 + 20</text><rect x="770" y="202" width="110" height="86" rx="13" fill="#211d37" stroke="#c4b5fd" stroke-width="2"/><text x="825.0" y="228" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">R20</text><text x="825.0" y="249" text-anchor="middle" fill="#a7bad0" font-size="12">RID 20.20.20.20</text><rect x="900" y="205" width="85" height="80" rx="13" fill="#211d37" stroke="#c4b5fd" stroke-width="2"/><text x="942.5" y="231" text-anchor="middle" fill="#edf5ff" font-size="12" font-weight="700">LAN B</text><text x="942.5" y="252" text-anchor="middle" fill="#a7bad0" font-size="12">10.20.20.0/24</text><text x="185" y="312" fill="#86efac" font-size="12" text-anchor="middle">LSDB de l’aire 10</text><text x="500" y="312" fill="#7dd3fc" font-size="12" text-anchor="middle">LSDB de l’aire 0</text><text x="830" y="312" fill="#ddd6fe" font-size="12" text-anchor="middle">LSDB de l’aire 20</text><rect x="75" y="350" width="890" height="48" rx="10" fill="#0d1827" stroke="#334960"/><text x="520" y="369" fill="#edf5ff" font-size="13" font-weight="700" text-anchor="middle">Les ABR créent des annonces de résumé (Type 3) aux frontières d’aire.</text><text x="520" y="387" fill="#a7bad0" font-size="11" text-anchor="middle">Ils ne recopient pas simplement toute la LSDB d’une aire vers les autres.</text><circle r="5.5" fill="#4ade80" stroke="#edf5ff" stroke-width="1.5"><animateMotion dur="3.5s" repeatCount="indefinite" path="M155 245 L190 245 L300 245 L330 245"/></circle><circle r="5.5" fill="#43c7f5" stroke="#edf5ff" stroke-width="1.5"><animateMotion dur="4.5s" begin="-1.2s" repeatCount="indefinite" path="M440 245 L475 245 L585 245 L630 245"/></circle><circle r="5.5" fill="#c4b5fd" stroke="#edf5ff" stroke-width="1.5"><animateMotion dur="3.8s" begin="-2s" repeatCount="indefinite" path="M740 245 L770 245 L880 245 L900 245"/></circle><text x="26" y="498" fill="#a7bad0" font-size="11">Les points animés restent sur les liens dessinés ; ils représentent le parcours logique du contrôle, pas une trame unique traversant toutes les aires.</text></svg></div>

**Lecture du schéma :** R10 et R20 sont des routeurs internes à leurs aires respectives. ABR-A possède au moins une interface dans Area 10 et une dans Area 0 ; ABR-B relie Area 20 à Area 0. Le routeur interne R0 appartient à Area 0. Les détails de topologie sont simplifiés : les liens physiques, les réseaux de transit et les interfaces doivent tous être configurés dans la même aire que le segment auquel ils appartiennent.

### 1.3 Rôles : routeur interne, ABR et ASBR

| Rôle | Fonction | Ce qu’il ne faut pas supposer |
|---|---|---|
| Routeur interne | Toutes ses interfaces OSPF concernées appartiennent à la même aire | Qu’il possède une LSDB détaillée des autres aires |
| ABR (*Area Border Router*) | Relie plusieurs aires OSPF, dont le backbone dans une conception normale ; construit et annonce les informations inter-aires | Qu’il retransmet à l’identique chaque LSA de l’aire source vers toutes les autres aires |
| ASBR (*Autonomous System Boundary Router*) | Introduit dans OSPF des routes issues d’une autre source de routage, par exemple des routes statiques ou un autre protocole, via redistribution | Qu’il est nécessairement un ABR ; un ASBR peut être interne à une aire |
| ABR/ASBR | Un routeur peut remplir les deux rôles | Que les deux fonctions impliquent le même type de LSA |

### 1.4 Process ID, Router ID et Area ID

Le Process ID Cisco identifie un processus dans la configuration locale ; il n’a pas à être identique entre tous les routeurs. Le Router ID identifie un routeur OSPF et doit être unique. L’Area ID désigne l’aire sur une interface OSPF. Un voisinage normal requiert des paramètres compatibles sur le lien : sous-réseau, type de réseau, timers, authentification, options et Area ID, selon le contexte.

Une erreur de conception fréquente est de voir un voisin `FULL` puis de conclure que toutes les routes devraient automatiquement être présentes. `FULL` indique une adjacence synchronisée selon les règles du segment. Cela ne prouve ni qu’un préfixe est annoncé par un ABR, ni qu’un résumé est correct, ni que la RIB choisit la route, ni que les filtres autorisent le trafic.


## 2. Les LSA : savoir qui les origine et où elles vivent

### 2.1 LSA et paquets ne sont pas la même chose

Une LSA est une annonce d’état de liens ou de routage. Une LSU (*Link State Update*) est un type de paquet OSPF transportant une ou plusieurs LSA. Les routeurs échangent des résumés de base, demandent les informations manquantes, puis diffusent les mises à jour nécessaires. Dans un environnement multi-aires, toutes les catégories de LSA n’ont pas la même portée.

### Schéma 2 — Types de LSA et portée

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="560" viewBox="0 0 1040 560" role="img" aria-label="Familles de LSA OSPFv2 et portée" style="display:block;width:100%;max-width:1040px;height:auto;font-family:Inter,Arial,sans-serif">
<defs>
 <marker id="arrC32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#43c7f5"/></marker>
 <marker id="arrG32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#4ade80"/></marker>
 <marker id="arrA32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/></marker>
 <marker id="arrR32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fb7185"/></marker>
 <filter id="glow32" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1040" height="560" rx="18" fill="#0b1220"/>
<text x="26" y="32" fill="#edf5ff" font-size="22" font-weight="700">Familles de LSA OSPFv2 et portée</text>
<text x="27" y="56" fill="#a7bad0" font-size="13">Le type et la portée d’une LSA déterminent où elle est connue et quel rôle la génère.</text>
<line x1="26" y1="73" x2="1014" y2="73" stroke="#334960" stroke-width="1.5"/>
<rect x="35" y="105" width="295" height="285" rx="15" fill="#10291f" stroke="#2b7152" stroke-width="1.5"/><text x="55" y="132" fill="#86efac" font-size="15" font-weight="700">TOPOLOGIE D’UNE AIRE</text><rect x="365" y="105" width="300" height="285" rx="15" fill="#102239" stroke="#316a95" stroke-width="1.5"/><text x="385" y="132" fill="#7dd3fc" font-size="15" font-weight="700">ANNONCES INTER-AIRES</text><rect x="700" y="105" width="305" height="285" rx="15" fill="#251c3a" stroke="#7054a0" stroke-width="1.5"/><text x="720" y="132" fill="#ddd6fe" font-size="15" font-weight="700">ANNONCES EXTERNES</text><rect x="60" y="160" width="245" height="72" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="182.5" y="186" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">Type 1 — Router LSA</text><text x="182.5" y="207" text-anchor="middle" fill="#a7bad0" font-size="12">Origine : chaque routeur</text><rect x="60" y="250" width="245" height="72" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="182.5" y="276" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">Type 2 — Network LSA</text><text x="182.5" y="297" text-anchor="middle" fill="#a7bad0" font-size="12">Origine : DR d’un segment</text><rect x="395" y="160" width="240" height="72" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="515.0" y="186" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">Type 3 — Summary</text><text x="515.0" y="207" text-anchor="middle" fill="#a7bad0" font-size="12">Origine : ABR, préfixe réseau</text><rect x="395" y="250" width="240" height="72" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="515.0" y="276" text-anchor="middle" fill="#edf5ff" font-size="12" font-weight="700">Type 4 — ASBR Summary</text><text x="515.0" y="297" text-anchor="middle" fill="#a7bad0" font-size="12">Origine : ABR, chemin vers ASBR</text><rect x="730" y="160" width="245" height="72" rx="13" fill="#211d37" stroke="#c4b5fd" stroke-width="2"/><text x="852.5" y="186" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">Type 5 — AS External</text><text x="852.5" y="207" text-anchor="middle" fill="#a7bad0" font-size="12">Origine : ASBR, aires normales</text><rect x="730" y="250" width="245" height="72" rx="13" fill="#302612" stroke="#fbbf24" stroke-width="2"/><text x="852.5" y="276" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">Type 7 — NSSA External</text><text x="852.5" y="297" text-anchor="middle" fill="#a7bad0" font-size="12">Origine : ASBR dans la NSSA</text><text x="182" y="352" fill="#86efac" font-size="11" text-anchor="middle">Flottent dans la portée de leur aire</text><text x="515" y="352" fill="#7dd3fc" font-size="11" text-anchor="middle">L’ABR origine un résumé adapté</text><text x="852" y="352" fill="#ddd6fe" font-size="11" text-anchor="middle">Portée selon le type d’aire</text><rect x="55" y="410" width="930" height="62" rx="10" fill="#0d1827" stroke="#334960"/><text x="75" y="434" fill="#7dd3fc" font-size="12" font-weight="700">Frontière d’aire :</text><text x="190" y="434" fill="#edf5ff" font-size="12">l’ABR calcule l’information inter-aire puis origine une nouvelle Type 3.</text><text x="75" y="454" fill="#fbbf24" font-size="12">NSSA :</text><text x="130" y="454" fill="#edf5ff" font-size="12">une Type 7 peut être traduite en Type 5 par un ABR si les conditions sont réunies.</text><text x="35" y="510" fill="#edf5ff" font-size="12" font-weight="700">À ne pas confondre :</text><text x="153" y="510" fill="#a7bad0" font-size="12">LSA = information de routage ; LSU = paquet pouvant transporter plusieurs LSA.</text><text x="26" y="540" fill="#a7bad0" font-size="11">Le diagramme montre les rôles et la portée ; les règles d’inondation exactes dépendent du type de LSA et du type d’aire.</text></svg></div>

### 2.2 Référence rapide : LSA de type 1 à 7

| Type | Nom courant | Origine typique | Portée et usage | Point de vigilance |
|---:|---|---|---|---|
| 1 | Router-LSA | Chaque routeur OSPF dans une aire | Décrit les liens du routeur dans cette aire | Ne fournit pas la topologie détaillée de toutes les aires |
| 2 | Network-LSA | DR sur certains segments multi-accès | Décrit les routeurs attachés au segment | N’est pas émis pour chaque lien point-à-point |
| 3 | Summary LSA réseau | ABR | Annonce un préfixe inter-aire | Peut être résumé ou filtré selon la politique et la plateforme |
| 4 | ASBR Summary LSA | ABR | Donne le chemin vers un ASBR hors de l’aire | À distinguer de l’annonce de préfixe externe elle-même |
| 5 | AS-External LSA | ASBR | Annonce une route externe dans les aires normales concernées | Non propagée dans une aire stub standard |
| 6 | Group-membership LSA | Multicast OSPF historique (MOSPF) | Généralement non utilisée dans les déploiements OSPF usuels modernes | Ne pas la traiter comme un type normal de route unicast dans un laboratoire IOS courant |
| 7 | NSSA External LSA | ASBR situé dans une NSSA | Transporte une route externe au sein de la NSSA | Peut être traduite en Type 5 par un ABR selon les conditions |

Les règles exactes de diffusion dépendent du type d’aire et du type de LSA. La distinction essentielle est la suivante : les types 1 et 2 décrivent la topologie à l’intérieur d’une aire ; les types 3 et 4 diffusent des informations inter-aires ; les types 5 et 7 représentent des routes externes avec des règles de portée différentes.

### 2.3 Pourquoi un ABR ne copie-t-il pas toute la LSDB ?

Les routeurs d’une aire ne reçoivent pas normalement la LSDB complète de toutes les autres aires. Au lieu de relayer sans distinction chaque Router-LSA d’une autre aire, un ABR annonce les destinations inter-aires selon le modèle OSPF. Le résumé Type 3 décrit un préfixe externe à l’aire destinataire mais interne au domaine OSPF ; le Type 4 décrit la façon d’atteindre un ASBR lorsque cela est nécessaire.

C’est la raison pour laquelle la panne d’un résumé peut couper une destination dans une aire alors que les routeurs de l’aire distante continuent d’avoir leurs voisins `FULL`. La bonne méthode consiste à vérifier l’information attendue à chaque frontière : LSDB locale, ABR connecté aux bonnes aires, type d’aire, éventuel résumé/filtre, puis route installée.

### 2.4 Lire les routes sur Cisco IOS

Les codes usuels incluent :

- `O` : route intra-aire ;
- `O IA` : route inter-aire ;
- `O E1` et `O E2` : routes externes Type 1 et Type 2 ;
- `O N1` et `O N2` : routes externes issues d’une NSSA, sur les plateformes qui les représentent ainsi.

Les codes et détails de sortie varient selon la plateforme. Utilise une commande de route et la base OSPF ensemble : une route absente de la RIB peut venir de la LSDB, d’une route concurrente, d’un résumé ou du traitement du prochain saut.


## 3. Types d’aires : normal, stub et NSSA

Le type d’aire est une politique de routage partagée. Les routeurs de l’aire doivent avoir une configuration compatible ; une incohérence de type d’aire empêche le voisinage de s’établir normalement ou crée des résultats inattendus.

### Schéma 3 — Comparaison des types d’aires

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="500" viewBox="0 0 1040 500" role="img" aria-label="Comparer les types d’aires" style="display:block;width:100%;max-width:1040px;height:auto;font-family:Inter,Arial,sans-serif">
<defs>
 <marker id="arrC26" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#43c7f5"/></marker>
 <marker id="arrG26" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#4ade80"/></marker>
 <marker id="arrA26" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/></marker>
 <marker id="arrR26" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fb7185"/></marker>
 <filter id="glow26" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1040" height="500" rx="18" fill="#0b1220"/>
<text x="26" y="32" fill="#edf5ff" font-size="22" font-weight="700">Comparer les types d’aires</text>
<text x="27" y="56" fill="#a7bad0" font-size="13">Le type d’aire détermine les informations externes et inter-aires qui peuvent y être diffusées.</text>
<line x1="26" y1="73" x2="1014" y2="73" stroke="#334960" stroke-width="1.5"/>
<rect x="190" y="105" width="190" height="48" rx="10" fill="#19283b" stroke="#4ade80" stroke-width="2"/><text x="285.0" y="134" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">Normale</text><rect x="392" y="105" width="190" height="48" rx="10" fill="#19283b" stroke="#43c7f5" stroke-width="2"/><text x="487.0" y="134" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">Stub</text><rect x="594" y="105" width="190" height="48" rx="10" fill="#19283b" stroke="#c4b5fd" stroke-width="2"/><text x="689.0" y="134" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">Totally stubby*</text><rect x="796" y="105" width="190" height="48" rx="10" fill="#19283b" stroke="#fbbf24" stroke-width="2"/><text x="891.0" y="134" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">NSSA</text><text x="32" y="188" fill="#a7bad0" font-size="12" font-weight="700">Type 1/2</text><rect x="190" y="165" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="285.0" y="187" text-anchor="middle" fill="#edf5ff" font-size="12">Oui</text><rect x="392" y="165" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="487.0" y="187" text-anchor="middle" fill="#edf5ff" font-size="12">Oui</text><rect x="594" y="165" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="689.0" y="187" text-anchor="middle" fill="#edf5ff" font-size="12">Oui</text><rect x="796" y="165" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="891.0" y="187" text-anchor="middle" fill="#edf5ff" font-size="12">Oui</text><text x="32" y="236" fill="#a7bad0" font-size="12" font-weight="700">Type 3 inter-aire</text><rect x="190" y="213" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="285.0" y="235" text-anchor="middle" fill="#edf5ff" font-size="12">Oui</text><rect x="392" y="213" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="487.0" y="235" text-anchor="middle" fill="#edf5ff" font-size="12">Oui</text><rect x="594" y="213" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="689.0" y="235" text-anchor="middle" fill="#edf5ff" font-size="10">Défaut typiquement</text><rect x="796" y="213" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="891.0" y="235" text-anchor="middle" fill="#edf5ff" font-size="12">Oui</text><text x="32" y="284" fill="#a7bad0" font-size="12" font-weight="700">Type 4/5 ASBR/externe</text><rect x="190" y="261" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="285.0" y="283" text-anchor="middle" fill="#edf5ff" font-size="12">Oui</text><rect x="392" y="261" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="487.0" y="283" text-anchor="middle" fill="#edf5ff" font-size="12">Non</text><rect x="594" y="261" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="689.0" y="283" text-anchor="middle" fill="#edf5ff" font-size="12">Non</text><rect x="796" y="261" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="891.0" y="283" text-anchor="middle" fill="#edf5ff" font-size="12">Non</text><text x="32" y="332" fill="#a7bad0" font-size="12" font-weight="700">Type 7 externe</text><rect x="190" y="309" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="285.0" y="331" text-anchor="middle" fill="#edf5ff" font-size="12">Non</text><rect x="392" y="309" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="487.0" y="331" text-anchor="middle" fill="#edf5ff" font-size="12">Non</text><rect x="594" y="309" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="689.0" y="331" text-anchor="middle" fill="#edf5ff" font-size="12">Non</text><rect x="796" y="309" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="891.0" y="331" text-anchor="middle" fill="#edf5ff" font-size="12">Oui</text><text x="32" y="380" fill="#a7bad0" font-size="12" font-weight="700">Route défaut ABR</text><rect x="190" y="357" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="285.0" y="379" text-anchor="middle" fill="#edf5ff" font-size="12">Selon config.</text><rect x="392" y="357" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="487.0" y="379" text-anchor="middle" fill="#edf5ff" font-size="10">Généralement oui</text><rect x="594" y="357" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="689.0" y="379" text-anchor="middle" fill="#edf5ff" font-size="10">Généralement oui</text><rect x="796" y="357" width="190" height="34" rx="7" fill="#0d1725" stroke="#334960" stroke-width="1"/><text x="891.0" y="379" text-anchor="middle" fill="#edf5ff" font-size="12">Selon config.</text><text x="35" y="430" fill="#a7bad0" font-size="12">* « Totally stubby » est une variante d’implémentation, notamment Cisco ; la syntaxe n’est pas universelle.</text><text x="35" y="451" fill="#a7bad0" font-size="12">Une NSSA bloque localement les Type 5 mais permet certaines routes externes locales en Type 7.</text><text x="35" y="472" fill="#a7bad0" font-size="12">Les options exactes, en particulier l’annonce du défaut, doivent être vérifiées sur la plate-forme.</text></svg></div>

### 3.1 Aire normale

Une aire normale peut apprendre les informations OSPF internes et inter-aires ainsi que les routes externes autorisées par le domaine. C’est le modèle général pour apprendre les types de LSA sans politique de réduction particulière.

### 3.2 Aire stub

Une aire stub limite la présence de routes externes de type 5 et les informations ASBR associées. L’ABR fournit généralement une route par défaut pour permettre l’accès aux destinations extérieures que l’aire ne décrit pas individuellement. Le but est de réduire les informations de routage qui n’ont pas besoin d’être détaillées dans cette aire.

Une aire stub ne doit pas contenir d’ASBR qui injecte des routes externes au sein de l’aire. Tous les routeurs de l’aire doivent accepter la même définition d’aire. La route par défaut doit être vérifiée dans la table, plutôt que supposée à partir de la commande.

### 3.3 Aire totalement stub (variante dépendante du constructeur)

Sur certaines plateformes, une variante dite *totally stubby area* restreint davantage les routes de résumé inter-aires, en ne fournissant typiquement qu’une route par défaut en plus des informations internes à l’aire. Le terme et la syntaxe peuvent être propres à l’implémentation. Ne copie pas une commande Cisco dans un environnement d’un autre constructeur sans vérifier l’équivalent pris en charge.

### 3.4 NSSA (*Not-So-Stubby Area*)

Une NSSA garde une partie du comportement d’une stub, mais permet à un ASBR situé dans l’aire d’introduire certaines routes externes au moyen de LSA Type 7. Ces LSA restent dans la NSSA ; un ABR peut les traduire en LSA Type 5 à destination des autres parties du domaine, selon les indicateurs, règles de sélection et options de configuration. Toutes les routes Type 7 ne sont pas nécessairement traduites dans tous les scénarios.

### 3.5 Comparaison opérationnelle

| Fonction | Normale | Stub | Totally stubby (implémentation) | NSSA |
|---|---|---|---|---|
| LSA Type 1/2 locales | Oui | Oui | Oui | Oui |
| Résumés inter-aires Type 3 | Oui | Oui selon politique | Réduits ; souvent défaut seulement | Oui selon politique |
| LSA Type 5 externes dans l’aire | Oui | Non | Non | Non, remplacées localement par Type 7 |
| LSA Type 7 dans l’aire | Non requis | Non | Non | Oui pour les routes externes admises |
| ASBR local autorisé | Oui | Non, pas pour redistribution externe dans la stub | Non | Oui |
| Route par défaut | Dépend des routes annoncées | Généralement fournie par ABR | Généralement fournie par ABR | Dépend de la configuration de l’ABR et de l’objectif |

### 3.6 Configuration illustrative d’une stub

Sur tous les routeurs de l’aire 10, y compris les routeurs internes et l’ABR qui la dessert, une configuration IOS classique peut inclure :

```cisco
router ospf 10
 area 10 stub
```

Cette ligne n’est pas une configuration complète : les annonces réseau, l’association des interfaces et les autres paramètres restent nécessaires. Vérifie qu’aucun besoin d’ASBR local ne contredit le choix stub.

### 3.7 Configuration illustrative d’une NSSA

Sur tous les routeurs qui participent à l’aire 20 NSSA :

```cisco
router ospf 10
 area 20 nssa
```

Les options permettant d’annoncer une route par défaut ou de traduire les Type 7 dépendent du rôle de l’ABR et du système. Avant d’activer la redistribution, utilise une route-map ou un mécanisme de filtrage équivalent pour limiter les préfixes, choisir les métriques et documenter le chemin de retour.


## 4. Agrégation inter-aire : réduire le volume sans cacher un défaut

### 4.1 Pourquoi résumer ?

Un résumé permet à un ABR d’annoncer un préfixe agrégé à d’autres aires plutôt que d’annoncer séparément chaque préfixe interne. Cette simplification peut réduire le nombre de routes inter-aires et limiter la diffusion de certains changements à travers les frontières. Elle est efficace lorsque le plan d’adressage est hiérarchique et que les préfixes sont contigus, alignés et attribués selon une logique de site ou de service.

### Schéma 4 — Résumé /22 à la frontière ABR

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="500" viewBox="0 0 1040 500" role="img" aria-label="Agrégation inter-aire sur un ABR" style="display:block;width:100%;max-width:1040px;height:auto;font-family:Inter,Arial,sans-serif">
<defs>
 <marker id="arrC32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#43c7f5"/></marker>
 <marker id="arrG32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#4ade80"/></marker>
 <marker id="arrA32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/></marker>
 <marker id="arrR32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fb7185"/></marker>
 <filter id="glow32" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1040" height="500" rx="18" fill="#0b1220"/>
<text x="26" y="32" fill="#edf5ff" font-size="22" font-weight="700">Agrégation inter-aire sur un ABR</text>
<text x="27" y="56" fill="#a7bad0" font-size="13">Quatre préfixes /24 contigus et alignés peuvent être représentés vers le backbone par un résumé /22.</text>
<line x1="26" y1="73" x2="1014" y2="73" stroke="#334960" stroke-width="1.5"/>
<rect x="35" y="105" width="400" height="305" rx="15" fill="#10291f" stroke="#2b7152" stroke-width="1.5"/><text x="55" y="132" fill="#86efac" font-size="15" font-weight="700">AREA 10 — ROUTES DÉTAILLÉES</text><rect x="610" y="105" width="395" height="305" rx="15" fill="#102239" stroke="#316a95" stroke-width="1.5"/><text x="630" y="132" fill="#7dd3fc" font-size="15" font-weight="700">AREA 0 — RÉSUMÉ INTER-AIRE</text><rect x="70" y="165" width="230" height="36" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="185.0" y="191" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">10.20.0.0/24</text><rect x="70" y="215" width="230" height="36" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="185.0" y="241" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">10.20.1.0/24</text><rect x="70" y="265" width="230" height="36" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="185.0" y="291" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">10.20.2.0/24</text><rect x="70" y="315" width="230" height="36" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="185.0" y="341" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">10.20.3.0/24</text><rect x="680" y="215" width="245" height="85" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="802.5" y="241" text-anchor="middle" fill="#edf5ff" font-size="16" font-weight="700">10.20.0.0/22</text><text x="802.5" y="262" text-anchor="middle" fill="#a7bad0" font-size="12">10.20.0.0 — 10.20.3.255</text><path d="M300 183 L400 183" fill="none" stroke="#4ade80" stroke-width="2"/><path d="M300 233 L400 233" fill="none" stroke="#4ade80" stroke-width="2"/><path d="M300 283 L400 283" fill="none" stroke="#4ade80" stroke-width="2"/><path d="M300 333 L400 333" fill="none" stroke="#4ade80" stroke-width="2"/><rect x="435" y="220" width="145" height="75" rx="13" fill="#211d37" stroke="#c4b5fd" stroke-width="2"/><text x="507.5" y="246" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">ABR</text><text x="507.5" y="267" text-anchor="middle" fill="#a7bad0" font-size="12">area range</text><path d="M400 183 L435 240" fill="none" stroke="#4ade80" stroke-width="2"/><path d="M400 233 L435 246" fill="none" stroke="#4ade80" stroke-width="2"/><path d="M400 283 L435 270" fill="none" stroke="#4ade80" stroke-width="2"/><path d="M400 333 L435 282" fill="none" stroke="#4ade80" stroke-width="2"/><path d="M580 257 L680 257" fill="none" stroke="#43c7f5" stroke-width="4"/><circle r="5.5" fill="#43c7f5" stroke="#edf5ff" stroke-width="1.2"><animateMotion dur="4s" repeatCount="indefinite" path="M580 257 L680 257"/></circle><rect x="640" y="330" width="335" height="52" rx="9" fill="#2c1f24" stroke="#b45360"/><text x="807" y="351" text-anchor="middle" fill="#fecdd3" font-size="12" font-weight="700">Attention aux trous dans le résumé</text><text x="807" y="369" text-anchor="middle" fill="#fecdd3" font-size="11">un préfixe absent peut être couvert par l’agrégat</text><text x="35" y="444" fill="#a7bad0" font-size="12">Le résumé n’efface pas les routes détaillées à l’intérieur de l’aire source ; il réduit les annonces inter-aires.</text><text x="35" y="466" fill="#a7bad0" font-size="12">Exemple IOS sur l’ABR : area 10 range 10.20.0.0 255.255.252.0 — vérifier l’alignement et la couverture réelle avant production.</text></svg></div>

### 4.2 Calculer un agrégat propre

Les quatre réseaux `10.20.0.0/24`, `10.20.1.0/24`, `10.20.2.0/24` et `10.20.3.0/24` peuvent être représentés par `10.20.0.0/22`. Le masque `/22` couvre les adresses de `10.20.0.0` à `10.20.3.255`, à condition que le préfixe de départ soit aligné sur une frontière `/22`.

L’agrégat peut cacher les détails internes sans supprimer les routes plus spécifiques de l’aire qui les contient. Cependant, si le résumé couvre des réseaux qui n’existent pas réellement, un routeur éloigné peut envoyer le trafic vers l’ABR parce qu’il croit que le préfixe est atteignable derrière ce dernier. Selon la configuration et le comportement de la plateforme, une route de rejet associée au résumé ou l’absence de route détaillée peut produire un trou noir pour des adresses non utilisées.

### 4.3 Exemple IOS sur l’ABR

```cisco
router ospf 10
 area 10 range 10.20.0.0 255.255.252.0
```

Cette commande est indicative pour les plateformes compatibles. Elle doit être configurée sur l’ABR approprié et la plage doit correspondre aux routes de l’aire concernée. Vérifie la route de résumé annoncée, les préfixes détaillés en amont, et le comportement lorsque l’un des préfixes est absent.

### 4.4 Checklist avant de résumer

- Les préfixes sont-ils contigus et alignés ?
- Le résumé correspond-il à un site ou une fonction clairement identifiée ?
- Des sous-réseaux inutilisés sont-ils couverts ?
- Le plan de routage local peut-il livrer chaque destination couverte ?
- Le retour arrière et le test d’un sous-réseau manquant sont-ils prévus ?
- Le résumé réduit-il réellement la table ou ne fait-il qu’obscurcir une incohérence ?

### 4.5 Résumé, filtrage et redistribution ne sont pas synonymes

L’agrégation combine plusieurs préfixes en un préfixe plus large à la frontière. Le filtrage empêche certaines informations d’être annoncées selon une politique. La redistribution introduit dans OSPF des routes apprises par une autre source. Ces mécanismes peuvent être utilisés ensemble, mais répondent à des objectifs différents.

Une erreur fréquente est de redistribuer toutes les routes statiques ou toutes les routes d’un protocole externe pour « faire apparaître » un préfixe manquant. Cela peut créer des boucles, des routes plus préférées que prévu, ou une diffusion trop large. Définis le périmètre, la métrique, la balise/tag de route si elle est prise en charge et la politique anti-boucle avant la redistribution.


## 5. ASBR et routes externes E1/E2

Un ASBR injecte dans OSPF des routes provenant d’une source externe, par exemple des routes statiques ou d’un protocole de routage différent. L’annonce externe peut être décrite par une LSA Type 5 dans les aires normales compatibles ou par une Type 7 dans une NSSA. La route installée dépend de l’annonce, du coût de chemin vers l’ASBR, du type de métrique externe et des règles de sélection OSPF.

### Schéma 5 — Différence E1 / E2

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="510" viewBox="0 0 1040 510" role="img" aria-label="Lien virtuel : prolonger logiquement le backbone" style="display:block;width:100%;max-width:1040px;height:auto;font-family:Inter,Arial,sans-serif">
<defs>
 <marker id="arrC48" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#43c7f5"/></marker>
 <marker id="arrG48" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#4ade80"/></marker>
 <marker id="arrA48" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/></marker>
 <marker id="arrR48" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fb7185"/></marker>
 <filter id="glow48" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1040" height="510" rx="18" fill="#0b1220"/>
<text x="26" y="32" fill="#edf5ff" font-size="22" font-weight="700">Lien virtuel : prolonger logiquement le backbone</text>
<text x="27" y="56" fill="#a7bad0" font-size="13">Cas de dépannage hérité : deux fragments de l’aire 0 reliés logiquement à travers une aire de transit commune.</text>
<line x1="26" y1="73" x2="1014" y2="73" stroke="#334960" stroke-width="1.5"/>
<rect x="35" y="110" width="300" height="300" rx="15" fill="#102239" stroke="#316a95" stroke-width="1.5"/><text x="55" y="137" fill="#7dd3fc" font-size="15" font-weight="700">AREA 0 — SEGMENT A</text><rect x="370" y="110" width="300" height="300" rx="15" fill="#10291f" stroke="#2b7152" stroke-width="1.5"/><text x="390" y="137" fill="#86efac" font-size="15" font-weight="700">AREA 10 — TRANSIT</text><rect x="705" y="110" width="300" height="300" rx="15" fill="#102239" stroke="#316a95" stroke-width="1.5"/><text x="725" y="137" fill="#7dd3fc" font-size="15" font-weight="700">AREA 0 — SEGMENT B</text><rect x="75" y="205" width="170" height="75" rx="13" fill="#141f30" stroke="#43c7f5" stroke-width="2"/><text x="160.0" y="231" text-anchor="middle" fill="#edf5ff" font-size="15" font-weight="700">ABR-A</text><text x="160.0" y="252" text-anchor="middle" fill="#a7bad0" font-size="12">Area 0 + Area 10</text><rect x="435" y="205" width="170" height="75" rx="13" fill="#141f30" stroke="#4ade80" stroke-width="2"/><text x="520.0" y="231" text-anchor="middle" fill="#edf5ff" font-size="15" font-weight="700">R-TRANSIT</text><text x="520.0" y="252" text-anchor="middle" fill="#a7bad0" font-size="12">Area 10 uniquement</text><rect x="765" y="205" width="170" height="75" rx="13" fill="#141f30" stroke="#43c7f5" stroke-width="2"/><text x="850.0" y="231" text-anchor="middle" fill="#edf5ff" font-size="15" font-weight="700">ABR-B</text><text x="850.0" y="252" text-anchor="middle" fill="#a7bad0" font-size="12">Area 10 + Area 0</text><path d="M245 242 L435 242" fill="none" stroke="#4ade80" stroke-width="4"/><path d="M605 242 L765 242" fill="none" stroke="#4ade80" stroke-width="4"/><path d="M160 205 C280 148 730 148 850 205" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-dasharray="8 6"/><text x="520" y="190" text-anchor="middle" fill="#ddd6fe" font-size="12" font-weight="700">Virtual link logique ABR-A ↔ ABR-B</text><text x="185" y="320" text-anchor="middle" fill="#a7bad0" font-size="12">Backbone segment A</text><text x="520" y="320" text-anchor="middle" fill="#a7bad0" font-size="12">Chemin physique de transit</text><text x="850" y="320" text-anchor="middle" fill="#a7bad0" font-size="12">Backbone segment B</text><circle r="5.5" fill="#4ade80" stroke="#edf5ff" stroke-width="1.3"><animateMotion dur="4s" repeatCount="indefinite" path="M245 242 L435 242 L605 242 L765 242"/></circle><rect x="90" y="350" width="860" height="38" rx="9" fill="#30201c" stroke="#9a5b31"/><text x="520" y="374" text-anchor="middle" fill="#fed7aa" font-size="12" font-weight="700">Solution de contournement, pas une architecture cible : rétablir une continuité native de l’aire 0 si possible.</text><text x="35" y="461" fill="#a7bad0" font-size="12">Un lien virtuel exige des ABR aux deux extrémités et une aire de transit commune non stub.</text></svg></div>

### 5.1 E1 (*External Type 1*)

La métrique E1 prend en compte le coût externe annoncé et le coût OSPF interne nécessaire pour atteindre l’ASBR. Elle permet donc de comparer le coût total du chemin jusqu’au réseau externe. Si deux sorties mènent au même réseau, la distance interne à chaque ASBR participe au coût global.

### 5.2 E2 (*External Type 2*)

E2 compare d’abord la métrique externe. Le coût interne vers l’ASBR est utilisé pour départager des chemins qui ont la même métrique externe, selon les règles OSPF et la plateforme. C’est le comportement externe traditionnel souvent utilisé par défaut dans plusieurs configurations Cisco, mais vérifie toujours le résultat réellement installé.

### 5.3 Choix et lecture des routes

Il est important de distinguer type de route et valeur de métrique. Le type de chemin OSPF est pris en compte dans les règles de sélection : les routes intra-aire et inter-aire ne sont pas simplement mises en compétition avec des routes externes comme si toutes leurs valeurs étaient interchangeables. Le meilleur résultat affiché par la table dépend aussi d’éventuelles routes issues d’autres protocoles et de leur préférence administrative.

Commandes utiles :

```cisco
show ip route ospf
show ip ospf database external
show ip ospf border-routers
show ip protocols
```

Selon la plateforme, les commandes peuvent différer. Lors d’un audit, relève la LSA externe (préfixe, métrique, type E1/E2, routeur annonceur), le coût vers l’ASBR et la route retenue. Ne change pas la métrique avant d’avoir identifié quel élément influence réellement la sélection.

### 5.4 Exemple de redistribution : pourquoi le contrôle compte

Une configuration pédagogique peut ressembler à :

```cisco
router ospf 10
 redistribute static subnets
```

Cette ligne seule est trop large pour représenter une bonne pratique de production. Elle peut injecter de nombreuses routes statiques dans OSPF si elles satisfont les conditions de la plateforme. Dans un vrai changement, limite les préfixes par route-map ou l’équivalent, définis la métrique et le type externe, décide si une balise de route est nécessaire, et assure-toi que le même préfixe ne sera pas réinjecté dans son origine par un autre chemin.


## 6. NSSA en pratique : comprendre la traduction Type 7 → Type 5

### Schéma 6 — ASBR local à la NSSA

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="510" viewBox="0 0 1040 510" role="img" aria-label="NSSA : la traduction Type 7 → Type 5" style="display:block;width:100%;max-width:1040px;height:auto;font-family:Inter,Arial,sans-serif">
<defs>
 <marker id="arrC36" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#43c7f5"/></marker>
 <marker id="arrG36" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#4ade80"/></marker>
 <marker id="arrA36" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/></marker>
 <marker id="arrR36" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fb7185"/></marker>
 <filter id="glow36" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1040" height="510" rx="18" fill="#0b1220"/>
<text x="26" y="32" fill="#edf5ff" font-size="22" font-weight="700">NSSA : la traduction Type 7 → Type 5</text>
<text x="27" y="56" fill="#a7bad0" font-size="13">Le même ABR possède une interface dans la NSSA et une interface dans le backbone ; les annonces ont des portées distinctes.</text>
<line x1="26" y1="73" x2="1014" y2="73" stroke="#334960" stroke-width="1.5"/>
<rect x="35" y="105" width="420" height="315" rx="15" fill="#2b2413" stroke="#a9842d" stroke-width="1.5"/><text x="55" y="132" fill="#fcd34d" font-size="15" font-weight="700">AREA 20 — NSSA</text><rect x="435" y="105" width="570" height="315" rx="15" fill="#102239" stroke="#316a95" stroke-width="1.5"/><text x="455" y="132" fill="#7dd3fc" font-size="15" font-weight="700">AREA 0 + AIRES NORMALES</text><rect x="65" y="190" width="150" height="82" rx="13" fill="#302612" stroke="#fbbf24" stroke-width="2"/><text x="140.0" y="216" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">ASBR</text><text x="140.0" y="237" text-anchor="middle" fill="#a7bad0" font-size="12">route externe</text><rect x="365" y="178" width="180" height="106" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="455.0" y="204" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">ABR</text><text x="455.0" y="225" text-anchor="middle" fill="#a7bad0" font-size="12">interface NSSA + Area 0</text><rect x="735" y="190" width="220" height="82" rx="13" fill="#211d37" stroke="#c4b5fd" stroke-width="2"/><text x="845.0" y="216" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">Routeurs OSPF</text><text x="845.0" y="237" text-anchor="middle" fill="#a7bad0" font-size="12">route externe apprise</text><path d="M215 231 L365 231" fill="none" stroke="#fbbf24" stroke-width="4"/><path d="M545 231 L735 231" fill="none" stroke="#c4b5fd" stroke-width="4"/><text x="286" y="210" text-anchor="middle" fill="#fcd34d" font-size="12" font-weight="700">LSA Type 7</text><text x="640" y="210" text-anchor="middle" fill="#ddd6fe" font-size="12" font-weight="700">LSA Type 5 traduite</text><circle r="5.5" fill="#fbbf24" stroke="#edf5ff" stroke-width="1.3"><animateMotion dur="3.2s" repeatCount="indefinite" path="M215 231 L365 231"/></circle><circle r="5.5" fill="#c4b5fd" stroke="#edf5ff" stroke-width="1.3"><animateMotion dur="4s" begin="-1s" repeatCount="indefinite" path="M545 231 L735 231"/></circle><text x="60" y="318" fill="#fcd34d" font-size="12">La Type 7 reste dans la NSSA.</text><text x="60" y="338" fill="#a7bad0" font-size="11">L’ASBR local doit redistribuer</text><text x="60" y="354" fill="#a7bad0" font-size="11">uniquement les routes prévues.</text><text x="565" y="318" fill="#7dd3fc" font-size="12">L’ABR peut générer une Type 5</text><text x="565" y="338" fill="#a7bad0" font-size="11">si la LSA Type 7 est éligible à</text><text x="565" y="354" fill="#a7bad0" font-size="11">la traduction et la configuration le permet.</text><rect x="485" y="372" width="470" height="30" rx="8" fill="#0b1725" stroke="#334960"/><text x="720" y="392" text-anchor="middle" fill="#edf5ff" font-size="11">Le Type 5 n’est pas la même LSA Type 7 simplement relayée.</text><text x="35" y="461" fill="#a7bad0" font-size="12">La portée et les règles NSSA varient avec la configuration ; vérifier la LSDB de chaque côté de la frontière.</text></svg></div>

Le schéma indique un mécanisme conceptuel : l’ASBR local annonce une route externe dans la NSSA par une Type 7. L’ABR peut créer une Type 5 correspondante à l’extérieur de cette NSSA, si les conditions de traduction sont satisfaites. Cette traduction ne transforme pas toutes les routes ni tous les types d’aires en informations externes identiques ; les règles de portée restent essentielles.

Pour diagnostiquer une route NSSA absente, vérifie :

1. la route existe-t-elle dans la table source de l’ASBR ?
2. la redistribution est-elle configurée et filtrée comme prévu ?
3. la LSA Type 7 est-elle présente dans la LSDB de la NSSA ?
4. le bit de traduction et les options de l’ABR permettent-ils la traduction voulue ?
5. une Type 5 apparaît-elle dans la LSDB d’une aire normale ?
6. la route externe est-elle installée, ou une route plus préférée la remplace-t-elle ?

Ne commence pas par modifier le coût. Un problème de traduction ou de portée se produit avant la sélection finale de métrique.


## 7. Virtual links : à connaître, sans en faire un choix par défaut

Un virtual link permet de relier logiquement deux ABR du backbone via une aire de transit commune lorsque la continuité normale de l’Area 0 est absente. Les deux extrémités doivent être des ABR et le transit doit être une aire OSPF appropriée, généralement non stub. Le lien virtuel est considéré comme faisant partie du backbone, mais dépend de la connectivité et du calcul intra-aire dans l’aire de transit.

### Schéma 7 — Virtual link à travers une aire de transit

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="520" viewBox="0 0 1040 520" role="img" aria-label="OSPF externe : comparer E1 et E2" style="display:block;width:100%;max-width:1040px;height:auto;font-family:Inter,Arial,sans-serif">
<defs>
 <marker id="arrC32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#43c7f5"/></marker>
 <marker id="arrG32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#4ade80"/></marker>
 <marker id="arrA32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/></marker>
 <marker id="arrR32" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fb7185"/></marker>
 <filter id="glow32" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1040" height="520" rx="18" fill="#0b1220"/>
<text x="26" y="32" fill="#edf5ff" font-size="22" font-weight="700">OSPF externe : comparer E1 et E2</text>
<text x="27" y="56" fill="#a7bad0" font-size="13">Même topologie, deux critères de métrique : E1 additionne les coûts ; E2 compare d’abord la métrique externe.</text>
<line x1="26" y1="73" x2="1014" y2="73" stroke="#334960" stroke-width="1.5"/>
<rect x="28" y="105" width="480" height="330" rx="15" fill="#102239" stroke="#316a95" stroke-width="1.5"/><text x="48" y="132" fill="#7dd3fc" font-size="15" font-weight="700">E1 — COÛT TOTAL</text><rect x="532" y="105" width="480" height="330" rx="15" fill="#251c3a" stroke="#7054a0" stroke-width="1.5"/><text x="552" y="132" fill="#ddd6fe" font-size="15" font-weight="700">E2 — MÉTRIQUE EXTERNE</text><rect x="48" y="220" width="95" height="62" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="95.5" y="246" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">R-IN</text><text x="95.5" y="267" text-anchor="middle" fill="#a7bad0" font-size="12">source</text><rect x="205" y="160" width="105" height="58" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="257.5" y="186" text-anchor="middle" fill="#edf5ff" font-size="12" font-weight="700">ASBR-A</text><text x="257.5" y="207" text-anchor="middle" fill="#a7bad0" font-size="12">coût interne 10</text><rect x="205" y="285" width="105" height="58" rx="13" fill="#302612" stroke="#fbbf24" stroke-width="2"/><text x="257.5" y="311" text-anchor="middle" fill="#edf5ff" font-size="12" font-weight="700">ASBR-B</text><text x="257.5" y="332" text-anchor="middle" fill="#a7bad0" font-size="12">coût interne 25</text><rect x="385" y="220" width="95" height="62" rx="13" fill="#211d37" stroke="#c4b5fd" stroke-width="2"/><text x="432.5" y="246" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">EXT</text><text x="432.5" y="267" text-anchor="middle" fill="#a7bad0" font-size="12">préfixe</text><path d="M143 235 L172 235 L172 189 L205 189" fill="none" stroke="#4ade80" stroke-width="3"/><path d="M143 267 L172 267 L172 314 L205 314" fill="none" stroke="#fbbf24" stroke-width="3"/><path d="M310 189 L350 189 L350 235 L385 235" fill="none" stroke="#4ade80" stroke-width="3"/><path d="M310 314 L350 314 L350 267 L385 267" fill="none" stroke="#fbbf24" stroke-width="3"/><text x="172" y="176" fill="#86efac" font-size="10" text-anchor="middle">interne 10</text><text x="172" y="300" fill="#fcd34d" font-size="10" text-anchor="middle">interne 25</text><text x="350" y="176" fill="#86efac" font-size="10" text-anchor="middle">externe 20</text><text x="350" y="300" fill="#fcd34d" font-size="10" text-anchor="middle">externe 20</text><text x="268" y="373" text-anchor="middle" fill="#86efac" font-size="12" font-weight="700">A : 10 + 20 = 30  •  B : 25 + 20 = 45</text><text x="268" y="394" text-anchor="middle" fill="#edf5ff" font-size="11">A gagne grâce au coût total le plus faible.</text><rect x="552" y="220" width="95" height="62" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="599.5" y="246" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">R-IN</text><text x="599.5" y="267" text-anchor="middle" fill="#a7bad0" font-size="12">source</text><rect x="709" y="160" width="105" height="58" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="761.5" y="186" text-anchor="middle" fill="#edf5ff" font-size="12" font-weight="700">ASBR-A</text><text x="761.5" y="207" text-anchor="middle" fill="#a7bad0" font-size="12">coût interne 10</text><rect x="709" y="285" width="105" height="58" rx="13" fill="#302612" stroke="#fbbf24" stroke-width="2"/><text x="761.5" y="311" text-anchor="middle" fill="#edf5ff" font-size="12" font-weight="700">ASBR-B</text><text x="761.5" y="332" text-anchor="middle" fill="#a7bad0" font-size="12">coût interne 25</text><rect x="889" y="220" width="95" height="62" rx="13" fill="#211d37" stroke="#c4b5fd" stroke-width="2"/><text x="936.5" y="246" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">EXT</text><text x="936.5" y="267" text-anchor="middle" fill="#a7bad0" font-size="12">préfixe</text><path d="M647 235 L676 235 L676 189 L709 189" fill="none" stroke="#4ade80" stroke-width="3"/><path d="M647 267 L676 267 L676 314 L709 314" fill="none" stroke="#fbbf24" stroke-width="3"/><path d="M814 189 L854 189 L854 235 L889 235" fill="none" stroke="#4ade80" stroke-width="3"/><path d="M814 314 L854 314 L854 267 L889 267" fill="none" stroke="#fbbf24" stroke-width="3"/><text x="676" y="176" fill="#86efac" font-size="10" text-anchor="middle">interne 10</text><text x="676" y="300" fill="#fcd34d" font-size="10" text-anchor="middle">interne 25</text><text x="854" y="176" fill="#86efac" font-size="10" text-anchor="middle">externe 20</text><text x="854" y="300" fill="#fcd34d" font-size="10" text-anchor="middle">externe 20</text><text x="772" y="373" text-anchor="middle" fill="#ddd6fe" font-size="12" font-weight="700">Métrique externe égale : 20</text><text x="772" y="394" text-anchor="middle" fill="#edf5ff" font-size="11">Le coût interne départage : A gagne (10 &lt; 25).</text><circle r="5" fill="#4ade80" stroke="#edf5ff" stroke-width="1.3"><animateMotion dur="4.5s" repeatCount="indefinite" path="M143 235 L172 235 L172 189 L205 189 L310 189 L350 189 L350 235 L385 235"/></circle><circle r="5" fill="#4ade80" stroke="#edf5ff" stroke-width="1.3"><animateMotion dur="4.5s" begin="-2s" repeatCount="indefinite" path="M647 235 L676 235 L676 189 L709 189 L814 189 L854 189 L854 235 L889 235"/></circle><text x="35" y="466" fill="#a7bad0" font-size="12">Comparaison illustrative : vérifie aussi la préférence entre routes intra-aire, inter-aire et externes avant d’expliquer la RIB.</text><text x="35" y="486" fill="#a7bad0" font-size="12">Les métriques sont des exemples ; la configuration et les règles de sélection effectives doivent être observées sur l’équipement.</text></svg></div>

### 7.1 Pourquoi la solution est fragile

Le virtual link dépend de l’aire de transit : si cette aire ou son routage ne fonctionne plus, le lien logique qui prolonge Area 0 peut échouer. Cela complique le diagnostic, les métriques, la sécurité et les dépendances. Lorsque c’est possible, la meilleure correction à long terme consiste à rétablir une continuité physique/logique correcte du backbone et à rationaliser l’affectation des aires.

Il ne faut pas confondre virtual link OSPF avec un tunnel générique de données ou un VPN utilisateur. Il s’agit d’un mécanisme de contrôle OSPF lié à la topologie logique. Les commandes et contraintes sont dépendantes de l’implémentation ; en laboratoire, documente les Router ID des extrémités, l’aire de transit et l’état exact du virtual link avant de modifier la configuration.

### 7.2 Indices de diagnostic

- Les deux ABR sont-ils bien attachés à Area 0 et à l’aire de transit ?
- Les Router ID configurés sont-ils corrects et uniques ?
- L’aire de transit possède-t-elle des adjacences stables ?
- Les routes nécessaires à l’acheminement du trafic OSPF entre les extrémités existent-elles ?
- La configuration est-elle symétrique aux deux extrémités ?
- Les logs montrent-ils que le lien logique devient `FULL` puis retombe ?


## 8. Séquence entre adjacence et route inter-aire

### Schéma 8 — De FULL à une route O IA

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="520" viewBox="0 0 1040 520" role="img" aria-label="De l’adjacence à la route inter-aire" style="display:block;width:100%;max-width:1040px;height:auto;font-family:Inter,Arial,sans-serif">
<defs>
 <marker id="arrC36" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#43c7f5"/></marker>
 <marker id="arrG36" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#4ade80"/></marker>
 <marker id="arrA36" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/></marker>
 <marker id="arrR36" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fb7185"/></marker>
 <filter id="glow36" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1040" height="520" rx="18" fill="#0b1220"/>
<text x="26" y="32" fill="#edf5ff" font-size="22" font-weight="700">De l’adjacence à la route inter-aire</text>
<text x="27" y="56" fill="#a7bad0" font-size="13">Le voisinage synchronise l’information locale ; l’ABR génère des annonces inter-aires, puis SPF et la RIB déterminent le chemin.</text>
<line x1="26" y1="73" x2="1014" y2="73" stroke="#334960" stroke-width="1.5"/>
<rect x="35" y="185" width="165" height="85" rx="13" fill="#12253a" stroke="#4ade80" stroke-width="2"/><text x="117.5" y="211" text-anchor="middle" fill="#edf5ff" font-size="15" font-weight="700">FULL</text><text x="117.5" y="232" text-anchor="middle" fill="#a7bad0" font-size="12">LSDB locale</text><circle cx="55" cy="168" r="12" fill="#4ade80"/><text x="55" y="172" text-anchor="middle" fill="#08111c" font-size="12" font-weight="700">1</text><rect x="235" y="185" width="165" height="85" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="317.5" y="211" text-anchor="middle" fill="#edf5ff" font-size="15" font-weight="700">ABR</text><text x="317.5" y="232" text-anchor="middle" fill="#a7bad0" font-size="12">résumé Type 3</text><circle cx="255" cy="168" r="12" fill="#43c7f5"/><text x="255" y="172" text-anchor="middle" fill="#08111c" font-size="12" font-weight="700">2</text><rect x="435" y="185" width="165" height="85" rx="13" fill="#12253a" stroke="#60a5fa" stroke-width="2"/><text x="517.5" y="211" text-anchor="middle" fill="#edf5ff" font-size="15" font-weight="700">Area 0</text><text x="517.5" y="232" text-anchor="middle" fill="#a7bad0" font-size="12">diffusion Type 3</text><circle cx="455" cy="168" r="12" fill="#60a5fa"/><text x="455" y="172" text-anchor="middle" fill="#08111c" font-size="12" font-weight="700">3</text><rect x="635" y="185" width="165" height="85" rx="13" fill="#12253a" stroke="#c4b5fd" stroke-width="2"/><text x="717.5" y="211" text-anchor="middle" fill="#edf5ff" font-size="15" font-weight="700">ABR distant</text><text x="717.5" y="232" text-anchor="middle" fill="#a7bad0" font-size="12">LSDB autre aire</text><circle cx="655" cy="168" r="12" fill="#c4b5fd"/><text x="655" y="172" text-anchor="middle" fill="#08111c" font-size="12" font-weight="700">4</text><rect x="835" y="185" width="165" height="85" rx="13" fill="#12253a" stroke="#fbbf24" stroke-width="2"/><text x="917.5" y="211" text-anchor="middle" fill="#edf5ff" font-size="15" font-weight="700">RIB</text><text x="917.5" y="232" text-anchor="middle" fill="#a7bad0" font-size="12">route O IA</text><circle cx="855" cy="168" r="12" fill="#fbbf24"/><text x="855" y="172" text-anchor="middle" fill="#08111c" font-size="12" font-weight="700">5</text><path d="M200 228 L235 228" fill="none" stroke="#43c7f5" stroke-width="3"/><path d="M400 228 L435 228" fill="none" stroke="#43c7f5" stroke-width="3"/><path d="M600 228 L635 228" fill="none" stroke="#43c7f5" stroke-width="3"/><path d="M800 228 L835 228" fill="none" stroke="#43c7f5" stroke-width="3"/><circle r="5" fill="#4ade80" stroke="#edf5ff" stroke-width="1.2"><animateMotion dur="6s" repeatCount="indefinite" path="M200 228 L235 228 L400 228 L435 228 L600 228 L635 228 L800 228 L835 228"/></circle><rect x="60" y="325" width="920" height="100" rx="13" fill="#0d1827" stroke="#334960"/><text x="85" y="353" fill="#edf5ff" font-size="14" font-weight="700">Ce qui change à la frontière</text><text x="85" y="378" fill="#a7bad0" font-size="13">Les routeurs d’une aire ne reçoivent pas la LSDB complète de toutes les autres aires.</text><text x="85" y="400" fill="#a7bad0" font-size="13">Les ABR annoncent les destinations inter-aires avec des LSA de résumé, selon les règles et filtres du domaine.</text><text x="26" y="474" fill="#a7bad0" font-size="12">`O IA` indique une route inter-aire sur Cisco IOS ; une route absente peut venir de la LSA, du type d’aire, du résumé ou de la sélection RIB.</text></svg></div>

Le fait qu’un routeur soit `FULL` avec son voisin signifie que l’adjacence est établie. Pour apprendre un préfixe d’une autre aire, le routeur doit aussi disposer des informations inter-aires attendues, acheminées par un ABR. L’ABR doit connaître le préfixe localement et l’annoncer conformément à la configuration de l’aire et aux règles de portée.

La chaîne de preuve à recueillir est donc :

1. `show ip ospf neighbor` : adjacence et interface ;
2. `show ip ospf database` : LSDB locale, puis détail du Type 3, Type 4 ou Type 5 attendu ;
3. `show ip ospf` et `show ip ospf interface brief` : rôles, aires et processus ;
4. `show ip route <préfixe>` : route installée, source et prochain saut ;
5. test de connectivité du trafic réel et vérification de la route retour.


## 9. Méthode de dépannage multi-aires

### Schéma 9 — Arbre de diagnostic reproductible

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="560" viewBox="0 0 1040 560" role="img" aria-label="Dépannage multi-aires : suivre les preuves" style="display:block;width:100%;max-width:1040px;height:auto;font-family:Inter,Arial,sans-serif">
<defs>
 <marker id="arrC42" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#43c7f5"/></marker>
 <marker id="arrG42" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#4ade80"/></marker>
 <marker id="arrA42" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/></marker>
 <marker id="arrR42" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fb7185"/></marker>
 <filter id="glow42" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1040" height="560" rx="18" fill="#0b1220"/>
<text x="26" y="32" fill="#edf5ff" font-size="22" font-weight="700">Dépannage multi-aires : suivre les preuves</text>
<text x="27" y="56" fill="#a7bad0" font-size="13">Partir du symptôme, vérifier les limites d’aire, puis la LSA attendue et la route installée.</text>
<line x1="26" y1="73" x2="1014" y2="73" stroke="#334960" stroke-width="1.5"/>
<rect x="355" y="100" width="330" height="60" rx="13" fill="#12253a" stroke="#43c7f5" stroke-width="2"/><text x="520.0" y="126" text-anchor="middle" fill="#edf5ff" font-size="16" font-weight="700">Route distante absente</text><text x="520.0" y="147" text-anchor="middle" fill="#a7bad0" font-size="12">Depuis un routeur de l’aire source</text><path d="M520 160 L520 194" fill="none" stroke="#43c7f5" stroke-width="3"/><rect x="355" y="194" width="330" height="60" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="520.0" y="220" text-anchor="middle" fill="#edf5ff" font-size="15" font-weight="700">Voisinage local FULL ?</text><text x="520.0" y="241" text-anchor="middle" fill="#a7bad0" font-size="12">show ip ospf neighbor</text><path d="M355 224 L220 224" fill="none" stroke="#fb7185" stroke-width="3"/><path d="M220 224 L220 258" fill="none" stroke="#fb7185" stroke-width="3"/><rect x="55" y="258" width="330" height="70" rx="13" fill="#2e1a22" stroke="#fb7185" stroke-width="2"/><text x="220.0" y="284" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">NON : résoudre le voisinage</text><text x="220.0" y="305" text-anchor="middle" fill="#a7bad0" font-size="12">interface · aire · timers · auth</text><path d="M520 254 L520 294" fill="none" stroke="#4ade80" stroke-width="3"/><rect x="355" y="294" width="330" height="60" rx="13" fill="#302612" stroke="#fbbf24" stroke-width="2"/><text x="520.0" y="320" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">Préfixe dans la LSDB attendue ?</text><text x="520.0" y="341" text-anchor="middle" fill="#a7bad0" font-size="12">database / type de LSA</text><path d="M355 324 L220 324" fill="none" stroke="#fb7185" stroke-width="3"/><path d="M220 324 L220 370" fill="none" stroke="#fb7185" stroke-width="3"/><rect x="55" y="370" width="330" height="72" rx="13" fill="#302612" stroke="#fbbf24" stroke-width="2"/><text x="220.0" y="396" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">NON : vérifier l’ABR / ASBR</text><text x="220.0" y="417" text-anchor="middle" fill="#a7bad0" font-size="12">type d’aire · filtrage · résumé</text><path d="M685 324 L815 324" fill="none" stroke="#4ade80" stroke-width="3"/><path d="M815 324 L815 370" fill="none" stroke="#4ade80" stroke-width="3"/><rect x="655" y="370" width="330" height="72" rx="13" fill="#13271f" stroke="#4ade80" stroke-width="2"/><text x="820.0" y="396" text-anchor="middle" fill="#edf5ff" font-size="14" font-weight="700">OUI : la route est installée ?</text><text x="820.0" y="417" text-anchor="middle" fill="#a7bad0" font-size="12">show ip route / RIB-FIB</text><path d="M820 442 L820 470" fill="none" stroke="#4ade80" stroke-width="3"/><rect x="655" y="470" width="330" height="54" rx="13" fill="#211d37" stroke="#c4b5fd" stroke-width="2"/><text x="820.0" y="496" text-anchor="middle" fill="#edf5ff" font-size="13" font-weight="700">Tester coût, next-hop et retour</text><text x="820.0" y="517" text-anchor="middle" fill="#a7bad0" font-size="12">puis ACL / MTU / service</text><circle r="5" fill="#43c7f5" stroke="#edf5ff" stroke-width="1.2"><animateMotion dur="5s" repeatCount="indefinite" path="M520 160 L520 194"/></circle><text x="26" y="540" fill="#a7bad0" font-size="11">Ne modifie pas simultanément area type, résumé et métrique : capture l’état initial, isole une hypothèse, puis vérifie.</text></svg></div>

### 9.1 Aucun voisin ne se forme sur le lien d’un ABR

Vérifie d’abord l’état de l’interface, l’adresse et le masque, l’aire associée, les timers Hello/Dead, le type de réseau OSPF, l’authentification et les Router ID. Une connectivité IP possible n’est pas une preuve que le voisinage OSPF doit se former.

### 9.2 Le voisin est FULL, mais aucune route inter-aire n’apparaît

Ne reconfigure pas les timers au hasard. Contrôle les aires de l’ABR, la présence du préfixe dans la LSDB de l’aire source, le Type 3 attendu dans la LSDB de l’aire destinataire, le résumé ou filtrage en place et enfin la table de routage. Une route peut être présente dans la LSDB sans être installée en RIB si une route concurrente est préférée ou si un prochain saut n’est pas valide.

### 9.3 Les routes externes sont absentes

Distingue route de source, redistribution, génération de Type 5/7, translation NSSA, type d’aire et sélection de route. Une aire stub ne reçoit pas une LSA Type 5 comme une aire normale. Une NSSA peut avoir une Type 7 sans Type 5 localement, et un ABR peut ou non réaliser la traduction voulue selon les règles applicables.

### 9.4 Un résumé attire le trafic vers une destination absente

Compare le résumé annoncé avec les préfixes réellement présents dans l’aire source. Vérifie si le préfixe détaillé existe sur l’ABR, si une route de rejet a été installée, si le trafic est reçu par l’ABR, et si l’ABR dispose d’une route valide vers la destination. Corriger peut exiger une plage plus précise, une modification du plan d’adressage ou un traitement de route absente — pas seulement une modification de métrique.

### 9.5 Capture Wireshark

Sur un réseau de laboratoire, un filtre de capture utile est :

```text
ospf
```

Pour IPv4, OSPF utilise le protocole IP 89, pas TCP ni UDP. Dans Wireshark, examine l’Area ID, le Router ID source, les paquets Hello, les DBD, les LSR, les LSU et les LSA transportées. Dans un diagnostic, garde la capture horodatée et compare-la aux sorties CLI. Un extrait visuel ne doit pas être interprété sans tenir compte de la position de capture, du sens du flux et des pertes possibles sur le point d’observation.


## 10. Laboratoires guidés

### Laboratoire 1 — Construire un domaine à trois aires

**But :** créer Area 0 et deux aires locales avec deux ABR.

Topologie conceptuelle : R10 — ABR-A — R0 — ABR-B — R20. Les interfaces R10/ABR-A appartiennent à Area 10 ; ABR-A/R0 et R0/ABR-B appartiennent à Area 0 ; ABR-B/R20 appartiennent à Area 20. Utilise un sous-réseau /30 distinct pour chaque lien et des préfixes LAN non chevauchants pour chaque site.

Étapes :

1. Configure d’abord les adresses IP, les interfaces et les routes connectées.
2. Donne un Router ID unique à chacun des cinq routeurs.
3. Active OSPF sur les interfaces voulues en affectant l’Area ID correct.
4. Vérifie les voisinages au sein de chaque segment.
5. Contrôle la LSDB et les LSA Type 3 aux frontières.
6. Vérifie que R10 apprend le LAN de R20 comme route inter-aire, si la configuration et les annonces le permettent.
7. Lance un test de bout en bout et vérifie aussi la route retour.

Livrables : schéma d’adressage, Router ID, sorties de `show ip ospf neighbor`, extraits de LSDB, routes O IA et résultats de ping ou de test applicatif.

### Laboratoire 2 — Créer une stub et vérifier la route par défaut

1. Sauvegarde toutes les configurations de laboratoire.
2. Choisis une aire non-backbone sans ASBR local et qui n’a pas besoin des routes externes détaillées.
3. Configure la stub sur tous les routeurs concernés, dont l’ABR.
4. Vérifie les adjacences et compare la LSDB avant/après.
5. Vérifie la route par défaut et teste une destination en dehors du domaine.
6. Annule la modification ou restaure la configuration initiale, puis vérifie à nouveau.

Critères : aucun voisinage incohérent, route par défaut expliquée par la conception, connectivité démontrée et état restauré.

### Laboratoire 3 — Agréger quatre /24 en un /22

1. Annonce les sous-réseaux `10.20.0.0/24` à `10.20.3.0/24` depuis l’aire 10.
2. Vérifie leurs routes détaillées depuis un routeur de cette aire.
3. Configure le résumé sur l’ABR correspondant.
4. Vérifie que les autres aires reçoivent le résumé attendu.
5. Simule un sous-réseau qui disparaît en laboratoire et analyse ce que le résumé annonce encore.
6. Documente les trous éventuels et un plan de retour arrière.

Critères : le résumé couvre précisément les réseaux voulus, est aligné, et sa portée est justifiée par le plan d’adressage.

### Laboratoire 4 — Injecter une route externe avec contrôle

1. Crée une route statique de test qui ne perturbe aucun réseau réel.
2. Définis un filtre qui ne permet d’injecter que le préfixe du laboratoire.
3. Redistribue ce préfixe depuis l’ASBR avec métrique et type documentés.
4. Vérifie la LSA externe générée et la route dans une aire normale.
5. Compare un scénario E1 et un scénario E2 en modifiant une seule variable.
6. Supprime la redistribution ou restaure la configuration, puis confirme la disparition attendue de la route.

### Laboratoire 5 — NSSA et traduction Type 7/Type 5

Utilise une aire NSSA contrôlée, un ASBR local et un ABR. Injecte un seul préfixe de test. Confirme la présence de Type 7 dans la NSSA, puis vérifie la traduction éventuelle en Type 5 dans une aire normale. Collecte les LSDB des deux côtés et explique chaque résultat. Ne généralise pas le comportement d’un seul IOS à tous les routeurs.

### Laboratoire 6 — Enquête sur une route absente

Le voisinage entre deux routeurs est FULL, mais le préfixe d’un LAN distant n’apparaît pas dans la table de routage d’un client d’une autre aire.

1. Vérifie l’annonce dans l’aire source.
2. Vérifie la présence de l’ABR dans la bonne aire.
3. Inspecte la LSA de résumé dans la zone destinataire.
4. Contrôle l’Area Type, la plage d’agrégation et les politiques de filtrage.
5. Vérifie les routes concurrentes et le prochain saut.
6. Formule une cause racine appuyée par deux preuves différentes.

### Laboratoire 7 — Auditer une conception mal agrégée

Le site annonce un résumé `10.20.0.0/20`, mais n’utilise que quatre `/24` dans le bloc. Identifie les préfixes couverts en plus, explique le risque de blackhole potentiel et propose une stratégie : préfixes mieux alloués, agrégat plus étroit ou choix explicite de routage. Ne corrige pas sans vérifier les routes détaillées et la portée de l’agrégat.

### Laboratoire 8 — Analyser les paquets OSPF

Capture un voisinage dans une maquette puis observe : Hello, négociation DBD, demandes LSR, mises à jour LSU et accusés LSAck. Pour le scénario multi-aires, compare les informations locales aux annonces de résumé. Le livrable doit expliquer la différence entre le paquet contenant l’information et l’information LSA elle-même.


## 11. Commandes de référence

| Commande | Question à laquelle elle répond |
|---|---|
| `show ip ospf neighbor` | Avec qui ce routeur est-il voisin et dans quel état ? |
| `show ip ospf interface brief` | Quelles interfaces participent à OSPF et à quelles aires ? |
| `show ip ospf` | Quel est l’état général du processus et des aires ? |
| `show ip ospf database` | Quelles LSA figurent dans la LSDB ? |
| `show ip ospf database summary` | Quelles LSA Type 3/4 sont connues, selon la plateforme ? |
| `show ip ospf database external` | Quelles routes externes Type 5 sont présentes ? |
| `show ip ospf database nssa-external` | Quelles LSA Type 7 sont présentes si la commande est prise en charge ? |
| `show ip route ospf` | Quelles routes OSPF sont installées ? |
| `show ip ospf border-routers` | Quels ABR/ASBR sont connus et comment les atteindre ? |
| `show ip protocols` | Quels paramètres et sources de routage sont actifs ? |
| `show running-config` (puis rechercher `router ospf` dans la sortie) | Quelle configuration du processus OSPF est en place ? |

La dernière commande peut dépendre du shell et de la version IOS ; si elle n’est pas prise en charge, consulte le processus OSPF dans la configuration active par la méthode disponible. Ne saisis pas de commande d’affichage supposée prise en charge sans vérifier l’aide CLI.


## 12. Erreurs de conception courantes

### Erreur 1 — Une aire non-backbone n’est raccordée qu’à une autre aire non-backbone

Dans une conception OSPF normale, les aires non-backbone s’appuient sur Area 0 pour l’échange inter-aires. Une chaîne d’aires sans raccordement correct au backbone nécessite de revoir la topologie, ou à défaut d’examiner les mécanismes de transition pris en charge, tels que les virtual links, avec prudence.

### Erreur 2 — Les deux côtés ne s’accordent pas sur le type d’aire

Une configuration stub/NSSA doit être cohérente sur tous les routeurs concernés. Une route par défaut absente ou des voisinages qui ne se forment plus doivent mener à vérifier l’Area Type avant de modifier les métriques.

### Erreur 3 — Un résumé est configuré sans plan d’adressage hiérarchique

L’agrégation peut cacher les sous-réseaux manquants et entraîner des destinations couvertes qui ne sont pas réellement raccordées. Résumer uniquement parce que la commande existe est une mauvaise pratique.

### Erreur 4 — Toutes les routes statiques sont redistribuées

Cela élargit le périmètre des annonces, peut introduire des routes de gestion ou de test, et peut créer des boucles lors d’une redistribution bidirectionnelle. Filtre les préfixes et définis la métrique.

### Erreur 5 — Le diagnostic s’arrête à `FULL`

`FULL` ne prouve pas qu’un préfixe inter-aire a été annoncé ou que la RIB l’a retenu. Compare LSDB et table de routage.


## 13. Évaluation avec corrigés

### Questions

1. Quelle est la différence principale entre un routeur interne, un ABR et un ASBR ?
2. Pourquoi Area 0 est-elle essentielle dans la conception multi-aires ?
3. Quelle information est décrite par une LSA Type 3 ?
4. Pourquoi une route externe de Type 5 n’est-elle pas propagée telle quelle dans une NSSA ?
5. Quelle est la différence entre une Type 7 et une Type 5 ?
6. Pourquoi faut-il que les routeurs d’une stub partagent la même configuration d’aire ?
7. Dans quel cas un résumé /22 peut-il couvrir quatre préfixes /24 ?
8. Quel risque un résumé trop large peut-il créer ?
9. Quelle est la différence entre une route externe E1 et E2 ?
10. Pourquoi les métriques E1 et E2 ne doivent-elles pas être comparées en oubliant le type de route OSPF ?
11. Pourquoi un virtual link doit-il être considéré comme une solution prudente et non comme une option de base ?
12. Un voisinage est FULL mais le préfixe est absent. Quelles preuves recueillir ?
13. Pourquoi la redistribution doit-elle être filtrée ?
14. À quoi sert le Type 4 ?
15. Quelle différence existe entre LSDB, LSA Type 3 et RIB ?

### Corrigés

**1.** Le routeur interne appartient à une seule aire OSPF ; l’ABR relie des aires ; l’ASBR introduit dans OSPF des routes issues d’une autre source. Un routeur peut remplir les deux derniers rôles.

**2.** Le backbone permet la diffusion cohérente des informations inter-aires. Une aire non-backbone doit normalement être raccordée à Area 0 par un ABR pour échanger les routes inter-aires dans une topologie régulière.

**3.** Une Type 3 annonce un préfixe réseau inter-aire depuis un ABR. Elle décrit une destination hors de l’aire courante mais interne au domaine OSPF.

**4.** Une NSSA bloque les Type 5 dans son domaine local. Elle autorise certaines routes externes locales au moyen de Type 7, qui peuvent être traduites par un ABR selon les conditions.

**5.** Type 7 est l’annonce externe utilisée dans une NSSA ; Type 5 est l’annonce externe habituelle dans les aires normales. Leur portée est différente.

**6.** Les paramètres d’aire influencent la compatibilité du voisinage et les types de LSA attendus. Une définition contradictoire peut empêcher la formation correcte des adjacences ou rendre le routage incohérent.

**7.** Quatre préfixes `/24` contigus qui commencent sur une frontière /22, comme `10.20.0.0/24` à `10.20.3.0/24`, sont couverts par `10.20.0.0/22`.

**8.** Des préfixes non utilisés peuvent être couverts par le résumé, ce qui pousse un routeur distant à envoyer les paquets à l’ABR alors qu’aucune route spécifique valide n’aboutit à la destination.

**9.** E1 ajoute le coût interne au coût externe ; E2 compare d’abord la métrique externe, puis utilise le coût interne pour départager les chemins à métrique externe égale selon les règles OSPF.

**10.** OSPF distingue les routes intra-aire, inter-aire et externes. Il faut d’abord appliquer la préférence des types de route, puis comparer les métriques pertinentes et les routes concurrentes.

**11.** Le virtual link dépend du routage d’une aire de transit et ajoute une dépendance logique. Il peut résoudre un problème de connectivité du backbone mais augmente la complexité ; une structure d’Area 0 cohérente est préférable.

**12.** Collecter les voisinages, l’Area ID des interfaces, la LSDB de l’aire source, la Type 3 attendue dans l’aire destinataire, le résumé/filtrage, la route installée et le prochain saut.

**13.** Une redistribution illimitée peut injecter des routes non voulues, provoquer des boucles ou annoncer des routes de test/gestion. Les filtres et métriques rendent le périmètre prévisible.

**14.** La Type 4 permet d’annoncer comment atteindre un ASBR qui se trouve en dehors de l’aire courante, afin de pouvoir calculer certains chemins vers les routes externes qu’il annonce.

**15.** La LSDB contient des LSA décrivant la topologie et les destinations connues ; une Type 3 est une catégorie de LSA de résumé ; la RIB est la table de routage installée après sélection parmi les sources candidates.


## 14. Checklist de changement multi-aires

Avant :
- [ ] Enregistrer la configuration, la version et les Router ID.
- [ ] Dessiner chaque interface OSPF avec son Area ID et son sous-réseau.
- [ ] Vérifier les voisinages, LSDB et routes d’origine.
- [ ] Décrire les LSA attendues à chaque frontière.
- [ ] Calculer les résumés et prouver qu’ils sont alignés.
- [ ] Préparer un test, un critère de réussite et un retour arrière.

Pendant :
- [ ] Modifier une seule variable de routage à la fois.
- [ ] Surveiller les adjacences et changements de base.
- [ ] Confirmer la LSA attendue avant de changer une métrique.
- [ ] Ne pas élargir une redistribution sans filtre explicite.

Après :
- [ ] Comparer LSDB et RIB avec l’état attendu.
- [ ] Tester le chemin aller et le chemin retour.
- [ ] Vérifier les routes de défaut, résumés et routes externes.
- [ ] Conserver les sorties de commande, captures et chronologie.
- [ ] Mettre à jour le diagramme d’architecture et la procédure opérationnelle.


## 15. Glossaire ciblé

| Terme | Définition pratique |
|---|---|
| ABR | Routeur qui relie plusieurs aires OSPF et fournit des informations inter-aires |
| ASBR | Routeur qui introduit dans OSPF des routes issues d’une autre source |
| Area 0 | Backbone OSPF destiné à la diffusion inter-aires |
| LSDB | Base d’état de liens propre à une aire, selon le processus OSPF |
| LSA | Annonce de liens ou de routage décrite par OSPF |
| LSU | Paquet OSPF qui transporte une ou plusieurs LSA |
| Stub | Type d’aire qui ne reçoit pas les LSA externes Type 5 et s’appuie généralement sur une route par défaut |
| NSSA | Aire qui bloque les Type 5 localement mais permet certaines routes externes sous forme de Type 7 |
| Résumé | Préfixe agrégé annoncé à une frontière, représentant un ensemble de préfixes plus spécifiques |
| E1 | Route externe dont le coût tient compte du coût interne vers l’ASBR et du coût externe |
| E2 | Route externe où la métrique externe domine la comparaison, le coût interne pouvant départager |
| Virtual link | Lien logique OSPF qui relie deux ABR au backbone via une aire de transit |
| RIB | Table de routage où les routes candidates retenues sont installées |


## 16. Références techniques

- **RFC 2328 — OSPF Version 2**, spécification du protocole, des aires, des LSA et du calcul SPF : https://www.rfc-editor.org/rfc/rfc2328.html
- **Cisco IOS XE — OSPF Configuration Guide** : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr3-fwd/ospf/ospf-configuration-guide/ospf.html
- **Cisco — Configure OSPF Not-So-Stubby Area (NSSA)** : https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/6208-nssa.html
- **Cisco IOS XE — OSPFv2 NSSA configuration** : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr3-fwd/ospf/ospf-configuration-guide/ospfv2-nssa.html

La RFC décrit le comportement du protocole ; les guides du constructeur sont nécessaires pour valider les commandes, options propriétaires et limites de la version utilisée. Les schémas sont conceptuels et doivent être adaptés à la topologie réelle.


## Préparation au niveau Expert

Le niveau Expert réutilisera le modèle multi-aires, les types de LSA, les rôles ABR/ASBR, l’agrégation, NSSA et E1/E2. Il approfondira l’ingénierie de convergence, l’optimisation et l’analyse des changements d’état de liens, l’authentification et la sécurité opérationnelle, le filtrage avancé, les migrations de protocole et la résolution d’incidents complexes à partir de captures et de preuves.
