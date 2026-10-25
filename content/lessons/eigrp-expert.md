# EIGRP — Niveau Expert
## Architecture, convergence, DUAL et exploitation avancée

**Niveau :** Expert  
**Durée indicative :** 8 à 12 heures, selon les laboratoires  
**Prérequis :** maîtriser `eigrp-debutant.md` et `eigrp-intermediaire.md`, notamment la formation des voisins, les K-values, la métrique composite, la condition de faisabilité, DUAL, FD/RD, successor, feasible successor, résumés, variance, mode nommé, EIGRP Stub, redistribution et premiers diagnostics SIA.

**Environnement recommandé :** une maquette Cisco IOS/IOS XE ou un simulateur prenant en charge les fonctions étudiées. Pour les laboratoires de panne, utilise uniquement une topologie isolée. Les noms d’interfaces, commandes et capacités exactes varient selon la plateforme et la version.

Ce cours constitue le troisième niveau de la série EIGRP. Il prolonge les deux précédents sans réexpliquer intégralement les bases. Son objectif est de développer une méthode d’ingénierie et d’investigation permettant d’expliquer le comportement réel d’EIGRP lors d’une panne, d’un changement de métrique, d’une redistribution ou d’une perte de voisinage.

> **Principe fondamental :** un réseau EIGRP robuste ne se limite pas à des voisins stables. Il doit maintenir des chemins sans boucle, limiter la portée des calculs diffusés, contrôler l’introduction de routes et permettre un diagnostic reproductible lorsque la convergence ne suit pas le scénario prévu.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :

- analyser le fonctionnement de DUAL à partir d’une chronologie d’événements et d’une table topologique ;
- distinguer un changement de successeur local d’une computation diffusée ;
- expliquer FD, RD, successor, feasible successor, PASSIVE et ACTIVE lors d’un incident complexe ;
- rechercher les causes plausibles d’un état *Stuck-in-Active* (SIA) sans se limiter aux timers ;
- concevoir une topologie qui limite les domaines de requêtes tout en conservant les chemins nécessaires ;
- vérifier les effets de la summarization et du mode Stub sur la convergence et la visibilité des routes ;
- exploiter les métriques étendues lorsqu’elles sont prises en charge ;
- construire une politique de redistribution avec métriques explicites, filtres et tags ;
- distinguer les symptômes du plan de contrôle des problèmes de RIB, FIB et service ;
- produire un rapport d’incident contenant des preuves, des causes probables et un plan de correction.

## Progression de la série

| Niveau | Acquis ou objectif |
|---|---|
| Débutant | Voisins, AS, métrique, DUAL, FD/RD, successeur et condition de faisabilité |
| Intermédiaire | Résumés, variance, mode nommé, Stub, redistribution et premiers diagnostics SIA |
| Expert | Ingénierie des domaines de panne, analyse des computations, métriques avancées, sécurité des frontières et diagnostic multi-cause |

Les trois niveaux forment une progression continue. Les bases sont rappelées lorsqu’elles sont nécessaires à une analyse, sans être réenseignées intégralement à chaque section.

## Comment utiliser les schémas

Les neuf schémas SVG sont intégrés directement dans ce fichier Markdown. Aucun dossier d’images externe ni moteur Mermaid n’est nécessaire. Les marqueurs animés illustrent des échanges ou des chemins précis ; ils ne mesurent pas le temps réel de convergence. Si le lecteur désactive l’animation SVG, les connecteurs et les libellés restent informatifs.

Pour chaque laboratoire : capture l’état initial, modifie une seule variable majeure, collecte les sorties après modification puis explique le résultat. Les tests de panne, de redistribution et de convergence doivent être effectués dans une maquette isolée.


## 1. Concevoir EIGRP comme un système de convergence

Dans un petit laboratoire, il suffit souvent de vérifier que les routes apparaissent et que les pings réussissent. Dans un réseau étendu, ce contrôle est insuffisant : plusieurs routeurs peuvent dépendre d’une même destination, les chemins de secours peuvent partager un défaut physique et une panne peut provoquer une computation diffusée sur une partie importante du domaine.

L’ingénierie avancée doit répondre à quatre questions :

1. Quel événement est susceptible de rendre une route invalide ?
2. Quel mécanisme détecte cet événement ?
3. Quels routeurs doivent participer à la convergence ?
4. Quelle preuve confirme que les chemins et services sont rétablis ?

### Schéma 1 — Architecture EIGRP à plusieurs niveaux

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 510" role="img" aria-label="Architecture EIGRP avec cœur, distribution, branches et frontière de redistribution" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="510" rx="16" fill="#0d1420"/>
<text x="26" y="34" fill="#eef4fb" font-size="22" font-weight="700">Architecture EIGRP : domaines de convergence</text>
<text x="26" y="58" fill="#adbdcf" font-size="13">Les frontières représentent des rôles et des politiques ; EIGRP ne possède pas d’aires OSPF.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="40" y="105" width="580" height="335" rx="15" fill="#111c2a" stroke="#34475d" stroke-width="1.5"/>
<text x="56" y="130" fill="#45c7f5" font-size="14" font-weight="700">Domaine EIGRP — AS 100</text>
<rect x="80" y="160" width="160" height="66" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2.2"/>
<text x="160" y="186" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R-CORE</text><text x="160" y="207" text-anchor="middle" fill="#adbdcf" font-size="12">Cœur de routage</text>
<rect x="350" y="160" width="175" height="66" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2.2"/>
<text x="437.5" y="186" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R-DIST</text><text x="437.5" y="207" text-anchor="middle" fill="#adbdcf" font-size="12">Distribution / résumé</text>
<path d="M 240 193 L 350 193" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><text x="295" y="180" text-anchor="middle" fill="#adbdcf" font-size="11">Transit</text>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.5"><animateMotion path="M 240 193 L 350 193" dur="2.7s" repeatCount="indefinite"/></circle>
<rect x="78" y="292" width="175" height="66" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2.2"/>
<text x="165.5" y="318" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">R-BRANCH-A</text><text x="165.5" y="339" text-anchor="middle" fill="#adbdcf" font-size="12">Branch / Stub possible</text>
<path d="M 160 226 L 160 292" fill="none" stroke="#4ade80" stroke-width="3.5" stroke-linecap="round"/><text x="175" y="261" fill="#4ade80" font-size="11">Lien local</text>
<rect x="350" y="292" width="175" height="66" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2.2"/>
<text x="437.5" y="318" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">R-BRANCH-B</text><text x="437.5" y="339" text-anchor="middle" fill="#adbdcf" font-size="12">Chemin alternatif</text>
<path d="M 437.5 226 L 437.5 292" fill="none" stroke="#fbbf24" stroke-width="3.5" stroke-linecap="round"/><text x="452" y="262" fill="#fbbf24" font-size="11">Lien local</text>
<rect x="670" y="160" width="245" height="80" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.2"/>
<text x="792.5" y="188" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R-BORDER</text><text x="792.5" y="210" text-anchor="middle" fill="#c4b5fd" font-size="12">Frontière de redistribution</text><text x="792.5" y="227" text-anchor="middle" fill="#adbdcf" font-size="11">EIGRP ↔ OSPF / routes externes</text>
<path d="M 525 193 L 670 193" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/>
<circle r="5" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.5"><animateMotion path="M 525 193 L 670 193" dur="2.7s" begin="1.1s" repeatCount="indefinite"/></circle>
<rect x="685" y="310" width="215" height="70" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2.2"/>
<text x="792.5" y="337" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Domaine OSPF</text><text x="792.5" y="358" text-anchor="middle" fill="#adbdcf" font-size="12">Politique séparée</text>
<path d="M 792.5 240 L 792.5 310" fill="none" stroke="#c4b5fd" stroke-width="3.5" stroke-dasharray="7 5"/>
<rect x="40" y="456" width="875" height="34" rx="8" fill="#111c2a" stroke="#34475d" stroke-width="1"/>
<text x="477.5" y="478" text-anchor="middle" fill="#eef4fb" font-size="12">Évalue les dépendances communes, la portée des changements et les politiques aux frontières.</text>
</svg>
</div>

Le schéma représente des rôles architecturaux, pas une topologie universelle. Le routeur de distribution peut être un point de résumé, mais EIGRP ne possède pas le modèle d’aires d’OSPF. La frontière de redistribution doit être traitée comme un endroit sensible : c’est là que les métriques, les tags et les politiques doivent être vérifiés.

### 1.1. Domaine de panne et dépendances communes

Deux routes présentes dans la table topologique ne constituent pas nécessairement une vraie redondance. Elles peuvent emprunter des câbles dans le même conduit, dépendre du même équipement de distribution ou atteindre le même routeur amont.

Pour évaluer une architecture, dessine les routeurs et interfaces réellement utilisés, les liens physiques, les préfixes originés, les points de résumé, les voisinages attendus, les routes importées et les dépendances communes. La distinction entre « deux voisins » et « deux chemins indépendants » est essentielle : une topologie peut présenter plusieurs voisins tout en restant vulnérable à une panne commune.

### 1.2. Les quatre niveaux de preuve

| Niveau | Question | Preuve à rechercher |
|---|---|---|
| Adjacence | Les voisins EIGRP sont-ils établis ? | Table des voisins, journaux et compteurs |
| Topologie / DUAL | Quels chemins sont connus et retenus ? | Table topologique, FD/RD, successor, état |
| RIB / FIB | Le prochain saut est-il installé et exploitable ? | Table de routage, résolution du next-hop, forwarding |
| Service | L’application est-elle réellement accessible ? | Test applicatif, route retour et mesures de perte |

Une adjacency stable ne prouve pas que toutes les routes sont annoncées. Une route installée ne prouve pas que l’application fonctionne. Il faut franchir les quatre niveaux.


## 2. DUAL : raisonner sur une machine à états

DUAL calcule des chemins sans boucle et coordonne les recalculs lorsque les informations topologiques changent. L’état est suivi pour chaque destination. Il est donc possible qu’un routeur conserve une route stable pour un préfixe tout en lançant une computation pour un autre.

### Schéma 2 — Machine à états DUAL par destination

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 520" role="img" aria-label="États DUAL PASSIVE et ACTIVE avec branche de feasible successor" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="520" rx="16" fill="#0d1420"/><text x="26" y="34" fill="#eef4fb" font-size="22" font-weight="700">DUAL : transitions par destination</text><text x="26" y="58" fill="#adbdcf" font-size="13">L’état dépend des chemins admissibles, pas simplement de la présence d’un voisin.</text><line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="60" y="125" width="250" height="76" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.2"/><text x="185" y="155" text-anchor="middle" fill="#4ade80" font-size="18" font-weight="700">PASSIVE</text><text x="185" y="178" text-anchor="middle" fill="#eef4fb" font-size="12">Route stable, successor retenu</text>
<rect x="360" y="125" width="230" height="76" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.2"/><text x="475" y="155" text-anchor="middle" fill="#fbbf24" font-size="16" font-weight="700">Événement topologique</text><text x="475" y="178" text-anchor="middle" fill="#eef4fb" font-size="12">Successeur perdu / coût changé</text><path d="M 310 163 L 360 163" fill="none" stroke="#fbbf24" stroke-width="3.5"/><circle r="4.5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.4"><animateMotion path="M 310 163 L 360 163" dur="2.2s" repeatCount="indefinite"/></circle>
<path d="M 475 201 L 475 238 L 245 238 L 245 275" fill="none" stroke="#4ade80" stroke-width="3.5"/><text x="357" y="228" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">RD du candidat &lt; FD de référence</text>
<rect x="60" y="275" width="370" height="70" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2.2"/><text x="245" y="303" text-anchor="middle" fill="#4ade80" font-size="16" font-weight="700">Successeur de remplacement</text><text x="245" y="325" text-anchor="middle" fill="#eef4fb" font-size="12">Bascule sans computation diffusée nécessaire</text>
<path d="M 475 201 L 475 238 L 710 238 L 710 275" fill="none" stroke="#fb7185" stroke-width="3.5"/><text x="600" y="228" text-anchor="middle" fill="#fb7185" font-size="11" font-weight="700">Pas de chemin admissible</text>
<rect x="540" y="275" width="340" height="70" rx="12" fill="#301b25" stroke="#fb7185" stroke-width="2.2"/><text x="710" y="303" text-anchor="middle" fill="#fb7185" font-size="18" font-weight="700">ACTIVE</text><text x="710" y="325" text-anchor="middle" fill="#eef4fb" font-size="12">Computation diffusée / attente de réponses</text>
<path d="M 710 345 L 710 382" fill="none" stroke="#fb7185" stroke-width="3.5"/><rect x="540" y="382" width="340" height="65" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2"/><text x="710" y="408" text-anchor="middle" fill="#fbbf24" font-size="15" font-weight="700">QUERY / REPLY</text><text x="710" y="428" text-anchor="middle" fill="#adbdcf" font-size="12">Résolution coordonnée du changement</text>
<rect x="60" y="382" width="370" height="65" rx="12" fill="#111c2a" stroke="#34475d" stroke-width="1.5"/><text x="245" y="408" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Retour vers PASSIVE</text><text x="245" y="428" text-anchor="middle" fill="#adbdcf" font-size="12">Un chemin valide a été établi</text>
<text x="480" y="486" text-anchor="middle" fill="#adbdcf" font-size="12">Schéma conceptuel : les transitions exactes dépendent de l’état antérieur et des réponses des voisins.</text>
</svg>
</div>

Le schéma présente deux possibilités après une modification topologique. Si un chemin admissible existe, DUAL peut sélectionner un autre successor. Si aucune route ne passe la condition de faisabilité, une computation diffusée peut être nécessaire.

### 2.1. FD et RD : éviter la simplification incorrecte

- **RD (Reported Distance)** : métrique annoncée par un voisin pour atteindre une destination.
- **FD (Feasible Distance)** : référence locale conservée par DUAL selon l’historique de la destination, notamment depuis la dernière transition appropriée d’ACTIVE à PASSIVE.
- **Successor** : voisin retenu pour le transfert vers la destination.
- **Feasible successor** : voisin qui satisfait `RD < FD` et fournit ainsi une preuve de chemin sans boucle selon le test de faisabilité.

La condition de faisabilité est **suffisante mais pas nécessaire** pour établir qu’un chemin est sans boucle. Une route peut être sans boucle sans être qualifiée de feasible successor. Il ne faut donc pas conclure qu’un chemin est forcément en boucle simplement parce qu’il ne satisfait pas la condition.

### 2.2. Une computation DUAL concerne une destination

Une panne de lien peut affecter plusieurs destinations, mais DUAL suit des états pour chaque route. Certaines destinations peuvent basculer immédiatement grâce à un chemin de secours admissible, tandis que d’autres entrent en ACTIVE.

Quand tu examines `show ip eigrp topology`, ne te limite pas au premier préfixe visible. Identifie les destinations affectées et recherche si elles partagent un voisin, une liaison ou une route de sortie commune.

### 2.3. Chronologie reproductible d’un incident

| Instant | Observation attendue | Question |
|---|---|---|
| T0 | Lien ou voisin défaillant | Quel événement a déclenché le changement ? |
| T1 | Route du successor invalidée | Un feasible successor était-il disponible ? |
| T2 | Bascule locale ou passage en ACTIVE | Quelle branche DUAL a été suivie ? |
| T3 | Query éventuelles et attentes de Reply | Quels voisins ont été interrogés ? |
| T4 | Route de nouveau PASSIVE ou incident SIA | Quel événement a permis ou empêché la fin du calcul ? |
| T5 | RIB/FIB et test de service | Le service a-t-il réellement récupéré ? |

Les temps exacts doivent être mesurés sur l’équipement. Une animation pédagogique ou une valeur de timer ne constitue pas une mesure de convergence.


## 3. Portée des Query et maîtrise du domaine de convergence

Quand DUAL doit réaliser une computation diffusée, les requêtes ne sont pas arbitrairement envoyées à tous les routeurs du réseau. Leur propagation dépend de la topologie, des routes annoncées, de l’état des destinations et des mécanismes tels que Stub ou les résumés.

### Schéma 3 — Query, Reply et frontière d’une branche Stub

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="Portée possible d'une requête EIGRP et branche Stub" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="500" rx="16" fill="#0d1420"/><text x="26" y="34" fill="#eef4fb" font-size="22" font-weight="700">Query / Reply : limiter les dépendances</text><text x="26" y="58" fill="#adbdcf" font-size="13">Topologie illustrative ; la portée effective dépend de la destination et des routes connues.</text><line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="135" width="170" height="72" rx="12" fill="#301b25" stroke="#fb7185" stroke-width="2.2"/><text x="130" y="163" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R1</text><text x="130" y="185" text-anchor="middle" fill="#fb7185" font-size="12">Route ACTIVE</text>
<rect x="300" y="135" width="170" height="72" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2.2"/><text x="385" y="163" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R2</text><text x="385" y="185" text-anchor="middle" fill="#adbdcf" font-size="12">Transit EIGRP</text>
<rect x="555" y="135" width="170" height="72" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2.2"/><text x="640" y="163" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R3</text><text x="640" y="185" text-anchor="middle" fill="#adbdcf" font-size="12">Voisin interrogé</text>
<rect x="765" y="300" width="160" height="72" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2.2"/><text x="845" y="328" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R4</text><text x="845" y="350" text-anchor="middle" fill="#4ade80" font-size="12">Branche Stub</text>
<path d="M 215 171 L 300 171" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round"/><text x="257.5" y="156" text-anchor="middle" fill="#fbbf24" font-size="12" font-weight="700">QUERY</text><circle r="5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.5"><animateMotion path="M 215 171 L 300 171" dur="2s" repeatCount="indefinite"/></circle>
<path d="M 470 171 L 555 171" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round"/><text x="512.5" y="156" text-anchor="middle" fill="#fbbf24" font-size="12" font-weight="700">QUERY</text><circle r="5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.5"><animateMotion path="M 470 171 L 555 171" dur="2s" begin="0.7s" repeatCount="indefinite"/></circle>
<path d="M 640 207 L 640 250 L 390 250 L 390 207" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 5"/><text x="515" y="241" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="700">REPLY</text>
<path d="M 640 207 L 640 258 L 845 258 L 845 300" fill="none" stroke="#5d7189" stroke-width="3" stroke-dasharray="5 6"/><text x="745" y="246" text-anchor="middle" fill="#adbdcf" font-size="11">Branche distincte</text>
<rect x="55" y="310" width="640" height="90" rx="12" fill="#111c2a" stroke="#34475d" stroke-width="1.5"/><text x="75" y="337" fill="#eef4fb" font-size="14" font-weight="700">Lecture opérationnelle</text><text x="75" y="360" fill="#adbdcf" font-size="12">• Suivre les routeurs qui reçoivent réellement les Query.</text><text x="75" y="379" fill="#adbdcf" font-size="12">• Vérifier si les voisins ont une route admissible ou doivent interroger plus loin.</text>
<text x="480" y="446" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">Stub et résumé peuvent limiter certaines dépendances, sans remplacer le plan de routage.</text><text x="480" y="468" text-anchor="middle" fill="#adbdcf" font-size="12">Une branche Stub n’est pas une aire Stub : les deux mécanismes sont différents.</text>
</svg>
</div>

Ce schéma est illustratif. Il ne signifie pas que chaque route en ACTIVE déclenche une Query sur tous les liens. Les messages réellement envoyés doivent être vérifiés dans les journaux ou les captures disponibles sur la plateforme.

### 3.1. Les mécanismes de réduction de portée

- **Summarization** : annoncer des préfixes agrégés lorsque le plan d’adressage le permet. Cela peut empêcher les détails de certains changements d’être visibles au-delà de la frontière du résumé, mais peut masquer un préfixe absent.
- **EIGRP Stub** : signaler que le routeur joue un rôle de branche et n’est pas un routeur de transit général. Cela peut limiter certaines requêtes en direction du Stub.
- **Plan d’adressage hiérarchique** : éviter les préfixes dispersés qui empêchent des agrégations propres.
- **Topologie maîtrisée** : éviter les dépendances transitives inutiles et vérifier les rôles des routeurs de branche.
- **Filtrage** : contrôler les annonces à une frontière avec des règles explicites et en vérifiant les effets sur la visibilité des routes.

Aucun mécanisme ne doit être appliqué uniquement pour faire disparaître un log SIA. Il faut comprendre quelles routes sont concernées et quelle visibilité doit être conservée.

### 3.2. Stub n’est pas synonyme de « aucune Query »

Le comportement dépend des routes annoncées, de la topologie et de l’implémentation. Un routeur Stub signale un rôle précis ; il ne remplace pas une conception correcte des routes. Vérifie les types de routes annoncés, les chemins de transit attendus et la portée des requêtes observées.


## 4. SIA : Stuck-in-Active et analyse chronologique

SIA correspond à une computation DUAL qui n’arrive pas à se terminer dans le délai prévu par l’implémentation. Un routeur peut alors retirer le voisin qui n’a pas fourni la réponse nécessaire. Dans une topologie importante, l’incident peut être dû à une instabilité distante, une requête qui traverse plusieurs routeurs, une réponse bloquée ou retardée, ou une surcharge.

### Schéma 4 — Chronologie illustrative d’un incident SIA

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" role="img" aria-label="Chronologie d'une Query EIGRP, SIA Query et résolution ou timeout" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="480" rx="16" fill="#0d1420"/><text x="26" y="34" fill="#eef4fb" font-size="22" font-weight="700">SIA : mesurer les événements, ne pas deviner</text><text x="26" y="58" fill="#adbdcf" font-size="13">Chronologie illustrative ; les temporisations exactes doivent être confirmées sur la plateforme.</text><line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<line x1="100" y1="180" x2="875" y2="180" stroke="#5d7189" stroke-width="4" stroke-linecap="round"/><circle cx="120" cy="180" r="9" fill="#fbbf24" stroke="#eef4fb" stroke-width="2"/><circle cx="430" cy="180" r="9" fill="#45c7f5" stroke="#eef4fb" stroke-width="2"/><circle cx="720" cy="180" r="9" fill="#fb7185" stroke="#eef4fb" stroke-width="2"/><circle cx="865" cy="180" r="9" fill="#c4b5fd" stroke="#eef4fb" stroke-width="2"/>
<text x="120" y="147" text-anchor="middle" fill="#fbbf24" font-size="16" font-weight="700">T0</text><text x="120" y="207" text-anchor="middle" fill="#eef4fb" font-size="12">QUERY envoyée</text><text x="120" y="226" text-anchor="middle" fill="#adbdcf" font-size="11">Route ACTIVE</text>
<text x="430" y="147" text-anchor="middle" fill="#45c7f5" font-size="16" font-weight="700">T1</text><text x="430" y="207" text-anchor="middle" fill="#eef4fb" font-size="12">SIA-QUERY éventuelle</text><text x="430" y="226" text-anchor="middle" fill="#adbdcf" font-size="11">Voisin encore en ACTIVE ?</text>
<text x="720" y="147" text-anchor="middle" fill="#fb7185" font-size="16" font-weight="700">T2</text><text x="720" y="207" text-anchor="middle" fill="#eef4fb" font-size="12">Aucune réponse utile</text><text x="720" y="226" text-anchor="middle" fill="#adbdcf" font-size="11">Timeout / SIA possible</text>
<text x="865" y="147" text-anchor="middle" fill="#c4b5fd" font-size="16" font-weight="700">T3</text><text x="865" y="207" text-anchor="middle" fill="#eef4fb" font-size="12">Fin de traitement</text><text x="865" y="226" text-anchor="middle" fill="#adbdcf" font-size="11">Route ou voisin réévalué</text>
<path d="M 120 180 L 430 180" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round"/><circle r="5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.5"><animateMotion path="M 120 180 L 430 180" dur="2.8s" repeatCount="indefinite"/></circle>
<rect x="50" y="280" width="410" height="100" rx="12" fill="#111c2a" stroke="#45c7f5" stroke-width="1.6"/><text x="70" y="307" fill="#45c7f5" font-size="14" font-weight="700">À confirmer dans les preuves</text><text x="70" y="330" fill="#adbdcf" font-size="12">• Route et état ACTIVE concernés</text><text x="70" y="350" fill="#adbdcf" font-size="12">• Voisins interrogés et réponses reçues</text><text x="70" y="370" fill="#adbdcf" font-size="12">• Logs horodatés, événements et compteurs</text>
<rect x="490" y="280" width="420" height="100" rx="12" fill="#301b25" stroke="#fb7185" stroke-width="1.6"/><text x="510" y="307" fill="#fb7185" font-size="14" font-weight="700">Ne pas conclure trop vite</text><text x="510" y="330" fill="#adbdcf" font-size="12">• Un SIA n’implique pas toujours un lien local coupé.</text><text x="510" y="350" fill="#adbdcf" font-size="12">• Une SIA-REPLY indique l’état, pas la fin de la Query.</text><text x="510" y="370" fill="#adbdcf" font-size="12">• Une suppression de voisin est un symptôme d’incident.</text>
<text x="480" y="428" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">La valeur d’un timer ne localise pas la cause : reconstruis le chemin de la Query.</text><text x="480" y="450" text-anchor="middle" fill="#adbdcf" font-size="11">Les délais montrés sont des jalons conceptuels, pas un chronométrage universel.</text>
</svg>
</div>

Dans les implémentations Cisco courantes, la gestion SIA peut utiliser des messages SIA-QUERY et SIA-REPLY avant l’expiration de la période globale. La SIA-REPLY indique que le voisin reste concerné par une computation en cours ; elle ne remplace pas la réponse finale à la Query initiale. Les délais précis doivent être interprétés selon la plateforme et sa version.

### 4.1. Méthode d’investigation d’une SIA

1. Identifier le préfixe exact devenu ACTIVE.
2. Relever l’heure du changement et le voisin dont la réponse est attendue.
3. Collecter la table des routes ACTIVE et la table topologique.
4. Vérifier la présence et la stabilité de chaque voisin sur le chemin de Query.
5. Comparer les logs de tous les routeurs concernés avec la même chronologie.
6. Rechercher les erreurs d’interface, pertes de paquets, instabilités de voisinage ou latences de traitement.
7. Déterminer si la portée des Query est cohérente avec l’architecture.
8. Corriger la cause probable, puis reproduire le test en maquette.

### 4.2. Commandes de diagnostic

Selon la version IOS/IOS XE, les commandes disponibles peuvent inclure :

```cisco
show ip eigrp neighbors
show ip eigrp topology active
show ip eigrp topology
show ip eigrp traffic
show ip eigrp events
show logging
show interfaces
```

Les syntaxes exactes et la disponibilité des commandes diffèrent. Ne lance pas de débogage intensif sans connaître l’impact sur le processeur et la charge de l’équipement. Dans un laboratoire, les captures et sorties horodatées sont préférables à une interprétation fondée sur un seul message de log.

### 4.3. Causes à distinguer

| Hypothèse | Preuve recherchée | Correction possible |
|---|---|---|
| Lien instable | Compteurs d’erreurs, transitions d’interface | Résoudre la couche physique |
| Voisin non réactif | État adjacency, logs, réponses absentes | Localiser l’instabilité distante |
| Portée des Query excessive | Topologie et route concernée | Réévaluer résumés, Stub et architecture |
| Congestion ou traitement lent | Mesures de charge, files, logs | Réduire la charge ou traiter la cause |
| Problème logiciel | Version, symptômes reproductibles, bug connu | Vérifier les avis et mises à jour du constructeur |
| Route mal conçue | Résumé, filtre ou chemin alternatif incohérent | Corriger la conception et tester le retour arrière |


## 5. Résumés, Null0 et visibilité des pannes

La summarization peut limiter le nombre de routes annoncées au-delà d’une frontière. Elle peut également masquer la disparition d’un préfixe plus spécifique si l’agrégat continue d’être annoncé.

### Schéma 5 — Agrégat et préfixe manquant

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="Résumé EIGRP avec route Null0 et sous-préfixe absent" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="500" rx="16" fill="#0d1420"/><text x="26" y="34" fill="#eef4fb" font-size="22" font-weight="700">Résumé EIGRP : un agrégat ne prouve pas tous les sous-réseaux</text><text x="26" y="58" fill="#adbdcf" font-size="13">Exemple : les préfixes /24 sont résumés en 10.10.0.0/22.</text><line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="55" y="125" width="190" height="75" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2.2"/><text x="150" y="153" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R-DIST</text><text x="150" y="176" text-anchor="middle" fill="#4ade80" font-size="12">Résumé /22</text>
<rect x="365" y="125" width="230" height="75" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2.2"/><text x="480" y="153" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R-CORE</text><text x="480" y="176" text-anchor="middle" fill="#adbdcf" font-size="12">Routeur amont</text>
<rect x="710" y="125" width="195" height="75" rx="12" fill="#201b35" stroke="#c4b5fd" stroke-width="2.2"/><text x="807.5" y="153" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R-DEST</text><text x="807.5" y="176" text-anchor="middle" fill="#adbdcf" font-size="12">Destination</text>
<path d="M 245 162 L 365 162" fill="none" stroke="#fbbf24" stroke-width="4"/><text x="305" y="147" text-anchor="middle" fill="#fbbf24" font-size="12" font-weight="700">10.10.0.0/22</text><circle r="5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.5"><animateMotion path="M 245 162 L 365 162" dur="2.6s" repeatCount="indefinite"/></circle><path d="M 595 162 L 710 162" fill="none" stroke="#45c7f5" stroke-width="4"/>
<rect x="55" y="260" width="850" height="82" rx="12" fill="#111c2a" stroke="#34475d" stroke-width="1.5"/><text x="75" y="286" fill="#eef4fb" font-size="14" font-weight="700">Préfixes spécifiques appartenant au résumé</text><text x="480" y="314" text-anchor="middle" fill="#adbdcf" font-size="13">10.10.0.0/24 | 10.10.1.0/24 | 10.10.2.0/24 | 10.10.3.0/24</text>
<rect x="55" y="370" width="400" height="70" rx="12" fill="#301b25" stroke="#fb7185" stroke-width="2"/><text x="255" y="397" text-anchor="middle" fill="#fb7185" font-size="15" font-weight="700">10.10.2.0/24 absent</text><text x="255" y="419" text-anchor="middle" fill="#adbdcf" font-size="12">La route plus spécifique disparaît</text>
<rect x="505" y="370" width="400" height="70" rx="12" fill="#2a2619" stroke="#fbbf24" stroke-width="2"/><text x="705" y="397" text-anchor="middle" fill="#fbbf24" font-size="15" font-weight="700">L’agrégat peut persister</text><text x="705" y="419" text-anchor="middle" fill="#adbdcf" font-size="12">Le trafic peut atteindre un rejet Null0</text><path d="M 455 405 L 505 405" fill="none" stroke="#fb7185" stroke-width="3.5"/>
<text x="480" y="486" text-anchor="middle" fill="#adbdcf" font-size="12">La route de rejet limite certaines boucles, mais ne garantit pas la joignabilité du sous-réseau absent.</text>
</svg>
</div>

### 5.1. Exemple de contrôle avant et après

Avant la modification, relève les routes spécifiques, le résumé configuré, la route de rejet éventuelle, les routes présentes sur le routeur amont et les tests de connectivité de chaque sous-réseau.

Ensuite, dans un laboratoire, retire un sous-préfixe et observe si le résumé continue d’être annoncé. Contrôle le point où le trafic destiné au sous-réseau absent est rejeté. Restaure ensuite le préfixe et vérifie que la route plus précise redevient disponible.

Une route Null0 peut éviter le renvoi circulaire du trafic qui correspond à l’agrégat mais ne dispose d’aucune route plus précise. En revanche, ce mécanisme peut provoquer un rejet intentionnel pour une destination manquante. Il faut donc documenter ce comportement au lieu de le considérer comme un succès automatique.

### 5.2. Résumé ou filtrage : décision d’architecture

Un résumé est pertinent si les préfixes appartiennent à un bloc cohérent et que le domaine amont peut raisonnablement traiter ce bloc comme une unité. Un filtre est pertinent pour contrôler les annonces qui traversent une frontière. Les deux mécanismes ne sont pas interchangeables.

Le choix doit être évalué selon la visibilité désirée des changements, la nécessité de distinguer les sous-préfixes, la présence d’autres routes vers le bloc, la possibilité d’une destination absente couverte par le résumé et les dépendances communes.


## 6. Métrique étendue et réseaux à haut débit

Les métriques EIGRP classiques sont généralement calculées en 32 bits. La fonctionnalité **EIGRP Wide Metrics**, lorsqu’elle est prise en charge, utilise des calculs en 64 bits et un mécanisme de mise à l’échelle pour la RIB. Dans la documentation Cisco IOS XE, cette fonctionnalité est liée au mode nommé ; les capacités doivent être vérifiées pour la plateforme et la version utilisées.

### Schéma 6 — Métrique classique et métrique étendue

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 510" role="img" aria-label="Comparaison de métrique EIGRP classique et wide metrics pour les hauts débits" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="510" rx="16" fill="#0d1420"/><text x="26" y="34" fill="#eef4fb" font-size="22" font-weight="700">EIGRP : calcul de métrique et échelle de débit</text><text x="26" y="58" fill="#adbdcf" font-size="13">Comparer la capacité de calcul et la compatibilité, pas seulement un nombre affiché.</text><line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="115" width="410" height="255" rx="14" fill="#111c2a" stroke="#fbbf24" stroke-width="2"/><text x="250" y="146" text-anchor="middle" fill="#fbbf24" font-size="17" font-weight="700">Métrique classique</text><text x="250" y="173" text-anchor="middle" fill="#eef4fb" font-size="14">Calcul 32 bits</text><rect x="90" y="205" width="320" height="48" rx="9" fill="#2a2619" stroke="#fbbf24" stroke-width="1.4"/><text x="250" y="235" text-anchor="middle" fill="#eef4fb" font-size="13">Bande passante / délai et K-values</text><path d="M 250 253 L 250 283" fill="none" stroke="#fbbf24" stroke-width="3"/><rect x="90" y="283" width="320" height="50" rx="9" fill="#172333" stroke="#34475d" stroke-width="1.5"/><text x="250" y="304" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">RIB / sélection de route</text><text x="250" y="322" text-anchor="middle" fill="#adbdcf" font-size="11">Limites de mise à l’échelle selon le débit</text>
<rect x="505" y="115" width="410" height="255" rx="14" fill="#111c2a" stroke="#4ade80" stroke-width="2"/><text x="710" y="146" text-anchor="middle" fill="#4ade80" font-size="17" font-weight="700">Wide Metrics</text><text x="710" y="173" text-anchor="middle" fill="#eef4fb" font-size="14">Calcul 64 bits, selon prise en charge</text><rect x="550" y="205" width="320" height="48" rx="9" fill="#142a24" stroke="#4ade80" stroke-width="1.4"/><text x="710" y="235" text-anchor="middle" fill="#eef4fb" font-size="13">Métriques étendues et délais mieux scalés</text><path d="M 710 253 L 710 283" fill="none" stroke="#4ade80" stroke-width="3"/><rect x="550" y="283" width="320" height="50" rx="9" fill="#172333" stroke="#34475d" stroke-width="1.5"/><text x="710" y="304" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">RIB avec mise à l’échelle</text><text x="710" y="322" text-anchor="middle" fill="#adbdcf" font-size="11">Vérifier mode nommé et support plateforme</text>
<rect x="45" y="395" width="870" height="68" rx="12" fill="#172333" stroke="#34475d" stroke-width="1.5"/><text x="65" y="421" fill="#eef4fb" font-size="13" font-weight="700">Contrôles obligatoires</text><text x="65" y="444" fill="#adbdcf" font-size="12">Version et matériel • mode EIGRP • K-values • métriques d’interface • comportement RIB • interopérabilité</text><text x="480" y="488" text-anchor="middle" fill="#adbdcf" font-size="11">Ce schéma présente les différences de capacité ; ce n’est pas un calcul numérique de métrique.</text>
</svg>
</div>

La documentation Cisco décrit les métriques étendues comme un moyen de traiter plus précisément les interfaces à haut débit et les agrégats de liens. La disponibilité, le format des métriques et leur mise à l’échelle dépendent de l’IOS/IOS XE et des fonctions activées. Référence : https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-routing/b-ip-routing/m_ire-wid-met.html

### 6.1. Pourquoi le débit ne suffit pas à définir le meilleur chemin

Une métrique EIGRP dépend des valeurs d’interface et des K-values. Il ne faut pas comparer les chiffres de deux équipements avant d’avoir confirmé qu’ils utilisent des paramètres compatibles et une méthode de calcul identique.

Procédure de validation :

1. identifier la version, le mode et les fonctions prises en charge ;
2. relever les paramètres des interfaces ;
3. vérifier les K-values des voisins ;
4. relever la métrique annoncée et la métrique calculée localement ;
5. observer le chemin réellement sélectionné ;
6. tester le comportement lors d’une panne contrôlée.

Évite de changer les K-values pour obtenir arbitrairement une préférence. Une modification de ces coefficients affecte la compatibilité et la comparaison des routes.


## 7. Variance, chemins multiples et capacité résiduelle

La variance autorise l’installation de certains chemins admissibles dont la métrique est supérieure à celle du meilleur chemin. Elle ne supprime pas la condition de faisabilité et ne garantit pas une distribution uniforme du trafic.

### Schéma 7 — Vérifier un chemin de variance

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 510" role="img" aria-label="Variance EIGRP avec deux chemins, faisabilité et seuil de métrique" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="510" rx="16" fill="#0d1420"/><text x="26" y="34" fill="#eef4fb" font-size="22" font-weight="700">Variance : vérifier chaque condition</text><text x="26" y="58" fill="#adbdcf" font-size="13">Exemple pédagogique : métriques cohérentes pour illustrer faisabilité et seuil.</text><line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="150" width="150" height="76" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2.2"/><text x="120" y="179" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R1</text><text x="120" y="201" text-anchor="middle" fill="#adbdcf" font-size="12">FD = 100</text>
<rect x="340" y="105" width="170" height="76" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2.2"/><text x="425" y="134" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R2</text><text x="425" y="156" text-anchor="middle" fill="#4ade80" font-size="12">RD = 80</text>
<rect x="340" y="260" width="170" height="76" rx="12" fill="#2a2619" stroke="#fbbf24" stroke-width="2.2"/><text x="425" y="289" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R3</text><text x="425" y="311" text-anchor="middle" fill="#fbbf24" font-size="12">RD = 90</text>
<rect x="730" y="165" width="180" height="76" rx="12" fill="#201b35" stroke="#c4b5fd" stroke-width="2.2"/><text x="820" y="194" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Destination D</text><text x="820" y="216" text-anchor="middle" fill="#adbdcf" font-size="12">Préfixe distant</text>
<path d="M 195 165 L 260 165 L 260 143 L 340 143" fill="none" stroke="#4ade80" stroke-width="4"/><path d="M 510 143 L 625 143 L 625 187 L 730 187" fill="none" stroke="#4ade80" stroke-width="4"/><circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.5"><animateMotion path="M 195 165 L 260 165 L 260 143 L 340 143 L 510 143 L 625 143 L 625 187 L 730 187" dur="3.1s" repeatCount="indefinite"/></circle>
<path d="M 195 210 L 260 210 L 260 298 L 340 298" fill="none" stroke="#fbbf24" stroke-width="4"/><path d="M 510 298 L 625 298 L 625 219 L 730 219" fill="none" stroke="#fbbf24" stroke-width="4"/><circle r="5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.5"><animateMotion path="M 195 210 L 260 210 L 260 298 L 340 298 L 510 298 L 625 298 L 625 219 L 730 219" dur="3.6s" begin="1s" repeatCount="indefinite"/></circle>
<text x="273" y="129" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">Coût local 20</text><text x="273" y="283" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="700">Coût local 50</text><text x="635" y="128" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">Total 100</text><text x="635" y="321" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="700">Total 140</text>
<rect x="45" y="380" width="415" height="70" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2"/><text x="252.5" y="407" text-anchor="middle" fill="#4ade80" font-size="14" font-weight="700">Chemin via R2</text><text x="252.5" y="429" text-anchor="middle" fill="#eef4fb" font-size="12">Meilleur coût : 100</text>
<rect x="500" y="380" width="415" height="70" rx="12" fill="#2a2619" stroke="#fbbf24" stroke-width="2"/><text x="707.5" y="407" text-anchor="middle" fill="#fbbf24" font-size="14" font-weight="700">Chemin via R3</text><text x="707.5" y="429" text-anchor="middle" fill="#eef4fb" font-size="12">140 ≤ 2 × 100 et RD 90 &lt; FD 100</text>
<text x="480" y="480" text-anchor="middle" fill="#adbdcf" font-size="12">Variance 2 : chemin dans le seuil ET faisabilité satisfaite. Le forwarding décide ensuite du partage.</text>
</svg>
</div>

Dans cet exemple, le coût du meilleur chemin est 100. La borne métrique avec `variance 2` est 200. Le chemin alternatif, avec une métrique totale de 140, reste dans cette borne. Il satisfait également `RD < FD` avec `90 < 100`. Les nombres sont illustratifs : dans un réseau réel, utilise les valeurs produites par l’équipement.

### 7.1. Trois conditions, pas une seule

Un chemin à coût inégal doit satisfaire au minimum :

1. les règles d’admissibilité sans boucle de DUAL ;
2. le seuil de métrique autorisé par la variance ;
3. les autres contraintes de validité et d’installation de la plateforme.

Le fait que la métrique d’un chemin soit inférieure au seuil ne suffit pas. Le chemin peut échouer à la condition de faisabilité et ne pas être admissible comme feasible successor.

### 7.2. Partage de charge et plan de transfert

EIGRP décide quelles routes sont admissibles ; la répartition des paquets est effectuée par la table de transfert et les mécanismes de la plateforme. Une distribution de charge ne sera pas nécessairement égale entre interfaces.

Pour valider le partage, teste plusieurs flux et pas seulement une conversation. Mesure la capacité disponible après la perte d’un chemin, le délai, les pertes et l’asymétrie éventuelle. Une route peut rester installée alors que le service subit de la congestion sur le chemin restant.


## 8. Redistribution contrôlée et prévention des réinjections

La redistribution est une frontière de contrôle particulièrement sensible. Une route importée dans un protocole peut revenir au protocole d’origine par un autre chemin si les politiques ne l’empêchent pas. Les conséquences peuvent être des boucles, une route inattendue ou une instabilité persistante.

### Schéma 8 — Tags de routes et contrôles dans les deux sens

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 530" role="img" aria-label="Redistribution bidirectionnelle EIGRP et OSPF avec tags anti-boucle" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="530" rx="16" fill="#0d1420"/><text x="26" y="34" fill="#eef4fb" font-size="22" font-weight="700">Redistribution : contrôler le sens et le retour des routes</text><text x="26" y="58" fill="#adbdcf" font-size="13">Les tags marquent une route ; des politiques sont nécessaires pour empêcher son retour.</text><line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="135" width="220" height="88" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.2"/><text x="155" y="164" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Domaine EIGRP</text><text x="155" y="187" text-anchor="middle" fill="#adbdcf" font-size="12">Routes internes / AS 100</text>
<rect x="370" y="135" width="220" height="88" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.2"/><text x="480" y="164" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">R-BORDER</text><text x="480" y="187" text-anchor="middle" fill="#fbbf24" font-size="12">Politique de redistribution</text>
<rect x="695" y="135" width="220" height="88" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.2"/><text x="805" y="164" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Domaine OSPF</text><text x="805" y="187" text-anchor="middle" fill="#adbdcf" font-size="12">Routes internes / Area 0</text>
<path d="M 265 160 L 370 160" fill="none" stroke="#4ade80" stroke-width="4"/><text x="317.5" y="146" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">EIGRP → OSPF</text><circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.5"><animateMotion path="M 265 160 L 370 160" dur="2.2s" repeatCount="indefinite"/></circle>
<path d="M 590 160 L 695 160" fill="none" stroke="#4ade80" stroke-width="4"/><circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.5"><animateMotion path="M 590 160 L 695 160" dur="2.2s" begin="0.6s" repeatCount="indefinite"/></circle>
<path d="M 695 205 L 590 205" fill="none" stroke="#c4b5fd" stroke-width="4"/><text x="642.5" y="244" text-anchor="middle" fill="#c4b5fd" font-size="11" font-weight="700">OSPF → EIGRP</text><path d="M 370 205 L 265 205" fill="none" stroke="#c4b5fd" stroke-width="4"/>
<rect x="45" y="290" width="420" height="105" rx="12" fill="#111c2a" stroke="#4ade80" stroke-width="1.8"/><text x="65" y="319" fill="#4ade80" font-size="14" font-weight="700">Sens EIGRP vers OSPF</text><text x="65" y="344" fill="#eef4fb" font-size="12">1. Import autorisé et métrique définie.</text><text x="65" y="365" fill="#adbdcf" font-size="12">2. Tag 100 appliqué aux routes redistribuées.</text><text x="65" y="384" fill="#adbdcf" font-size="12">3. Le retour portant le tag 100 est refusé.</text>
<rect x="495" y="290" width="420" height="105" rx="12" fill="#111c2a" stroke="#c4b5fd" stroke-width="1.8"/><text x="515" y="319" fill="#c4b5fd" font-size="14" font-weight="700">Sens OSPF vers EIGRP</text><text x="515" y="344" fill="#eef4fb" font-size="12">1. Import autorisé et métrique définie.</text><text x="515" y="365" fill="#adbdcf" font-size="12">2. Tag 200 appliqué aux routes redistribuées.</text><text x="515" y="384" fill="#adbdcf" font-size="12">3. Le retour portant le tag 200 est refusé.</text>
<rect x="45" y="420" width="870" height="62" rx="12" fill="#301b25" stroke="#fb7185" stroke-width="1.5"/><text x="480" y="446" text-anchor="middle" fill="#fb7185" font-size="14" font-weight="700">Le tag seul ne protège pas la route.</text><text x="480" y="466" text-anchor="middle" fill="#adbdcf" font-size="12">Politiques inverses, métriques, filtres et tests doivent être vérifiés dans les deux sens.</text>
<text x="480" y="508" text-anchor="middle" fill="#adbdcf" font-size="11">Schéma de politique : les commandes dépendent des protocoles et versions utilisés.</text>
</svg>
</div>

### 8.1. Construire une politique vérifiable

Une politique de redistribution doit répondre explicitement à ces questions : quelles routes sont autorisées à entrer, quels préfixes doivent rester internes, quelle métrique est appliquée, quel tag est ajouté, quelle politique empêche le retour et quels tests démontrent que les routes autorisées passent et que les routes interdites sont bloquées.

Les tags sont des conventions. Leur valeur ne protège aucune route par elle-même. La protection provient des politiques qui vérifient les tags et contrôlent l’importation et l’exportation.

### 8.2. Éviter la redistribution générale non filtrée

Redistribuer toutes les routes connectées, statiques ou dynamiques peut introduire des préfixes de gestion, des routes de test ou des informations qui n’étaient pas destinées à traverser la frontière.

Dans une configuration de production, la redistribution doit être précédée d’une liste de préfixes attendus, d’une politique explicitement attachée et d’une validation avant/après. Si une route apparaît de manière inattendue, recherche son origine et le chemin de redistribution avant de modifier sa métrique.


## 9. Sécurité opérationnelle et intégrité du plan de contrôle

La sécurité d’EIGRP ne repose pas uniquement sur l’authentification. Il faut aussi protéger les interfaces participantes, maîtriser les annonces, documenter les voisins autorisés et contrôler les changements de configuration.

Les mécanismes disponibles varient selon le mode et la plateforme, notamment pour les options d’authentification. Vérifie la prise en charge et les restrictions de version avant de choisir une méthode.

### 9.1. Contrôles essentiels

- limiter les adjacences aux interfaces et voisins attendus ;
- utiliser des interfaces passives là où aucune adjacency n’est requise ;
- protéger l’administration des routeurs et limiter les privilèges de modification ;
- documenter les méthodes d’authentification prises en charge ;
- contrôler les routes annoncées et les redistributions ;
- journaliser les changements et conserver une configuration de référence ;
- tester la coexistence des fonctions après une migration ou une mise à niveau.

### 9.2. K-values et authentification ne sont pas des réglages d’optimisation

Les K-values influencent le calcul de métrique et doivent être compatibles entre voisins. Une authentification incorrectement configurée peut empêcher le voisinage. Ces deux sujets doivent être diagnostiqués séparément.

Ne modifie pas les K-values pour forcer un chemin dans un réseau en production. Prépare un laboratoire, compare les configurations et vérifie les routes résultantes avant tout changement.


## 10. Méthode de diagnostic expert

### Schéma 9 — Du plan de contrôle au service

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 490" role="img" aria-label="Diagnostic en cinq niveaux, du voisinage EIGRP au service applicatif" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="490" rx="16" fill="#0d1420"/><text x="26" y="34" fill="#eef4fb" font-size="22" font-weight="700">Diagnostic expert : localiser la première preuve en échec</text><text x="26" y="58" fill="#adbdcf" font-size="13">Ne modifie pas le protocole avant d’avoir identifié l’étape en échec.</text><line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="35" y="135" width="160" height="90" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="115" y="164" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">1. Voisins</text><text x="115" y="187" text-anchor="middle" fill="#adbdcf" font-size="11">Adjacence EIGRP</text><text x="115" y="205" text-anchor="middle" fill="#adbdcf" font-size="10.5">AS / interface / K</text>
<rect x="220" y="135" width="160" height="90" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/><text x="300" y="164" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">2. DUAL</text><text x="300" y="187" text-anchor="middle" fill="#adbdcf" font-size="11">Topologie / FD / RD</text><text x="300" y="205" text-anchor="middle" fill="#adbdcf" font-size="10.5">PASSIVE / ACTIVE</text>
<rect x="405" y="135" width="160" height="90" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2"/><text x="485" y="164" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">3. RIB</text><text x="485" y="187" text-anchor="middle" fill="#adbdcf" font-size="11">Route retenue</text><text x="485" y="205" text-anchor="middle" fill="#adbdcf" font-size="10.5">Métrique / next-hop</text>
<rect x="590" y="135" width="160" height="90" rx="12" fill="#2a2619" stroke="#fbbf24" stroke-width="2"/><text x="670" y="164" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">4. FIB</text><text x="670" y="187" text-anchor="middle" fill="#adbdcf" font-size="11">Forwarding</text><text x="670" y="205" text-anchor="middle" fill="#adbdcf" font-size="10.5">Interface / adjacency</text>
<rect x="775" y="135" width="150" height="90" rx="12" fill="#301b25" stroke="#fb7185" stroke-width="2"/><text x="850" y="164" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">5. Service</text><text x="850" y="187" text-anchor="middle" fill="#adbdcf" font-size="11">Route retour</text><text x="850" y="205" text-anchor="middle" fill="#adbdcf" font-size="10.5">Application réelle</text>
<path d="M 195 180 L 220 180 M 380 180 L 405 180 M 565 180 L 590 180 M 750 180 L 775 180" fill="none" stroke="#5d7189" stroke-width="3"/>
<rect x="45" y="290" width="420" height="95" rx="12" fill="#111c2a" stroke="#fb7185" stroke-width="1.6"/><text x="65" y="318" fill="#fb7185" font-size="14" font-weight="700">Si le voisinage échoue</text><text x="65" y="341" fill="#adbdcf" font-size="12">Interface, AS, K-values, paramètres d’adjacence,</text><text x="65" y="361" fill="#adbdcf" font-size="12">authentification et filtrage de contrôle.</text>
<rect x="495" y="290" width="420" height="95" rx="12" fill="#111c2a" stroke="#fbbf24" stroke-width="1.6"/><text x="515" y="318" fill="#fbbf24" font-size="14" font-weight="700">Si le voisinage est stable</text><text x="515" y="341" fill="#adbdcf" font-size="12">Topologie DUAL, RIB/FIB, route retour, filtres,</text><text x="515" y="361" fill="#adbdcf" font-size="12">résumés et service final.</text>
<text x="480" y="426" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">La bonne correction traite la première preuve en échec.</text><text x="480" y="448" text-anchor="middle" fill="#adbdcf" font-size="12">Collecte les états avant et après ; ne change qu’une variable majeure à la fois.</text>
</svg>
</div>

### 10.1. Arbre de diagnostic

Commence par la question la plus simple : le voisinage est-il établi ?

**Si non :**
1. vérifie l’interface et l’adressage ;
2. vérifie l’AS EIGRP et les interfaces participantes ;
3. compare les K-values ;
4. examine l’authentification et les filtres ;
5. collecte les journaux.

**Si oui, mais qu’une route manque :**
1. contrôle l’existence du préfixe sur le routeur d’origine ;
2. vérifie les annonces, résumés et filtres ;
3. examine la table topologique ;
4. contrôle le successeur et l’état DUAL ;
5. compare la table topologique à la RIB.

**Si la route est installée mais que le service échoue :**
1. vérifie le prochain saut et l’interface de sortie ;
2. examine la résolution de voisinage au niveau IP ;
3. vérifie le chemin retour ;
4. contrôle les ACL, pare-feu et dépendances applicatives ;
5. teste depuis une source représentative de l’utilisateur.

### 10.2. Rapport d’incident attendu

| Élément | Contenu attendu |
|---|---|
| Symptôme | Préfixe, utilisateurs et services affectés |
| Chronologie | Horodatages des premiers symptômes et changements d’état |
| Topologie | Routeurs, interfaces, voisins et frontières de politique |
| Preuves | Commandes, logs, captures et tests de trafic |
| Hypothèse | Cause technique la plus probable et raisons |
| Correction | Changement appliqué et effets attendus |
| Validation | Route, chemin retour et service fonctionnels |
| Prévention | Mesures de conception ou de supervision pour réduire le risque |

Une hypothèse n’est pas une cause confirmée. Le rapport doit distinguer ce qui a été observé de ce qui reste supposé.


## 11. Laboratoires avancés

Tous les scénarios de panne doivent être exécutés dans une maquette isolée. Les manipulations qui peuvent provoquer une convergence étendue, une perte de route ou une réinjection sont à éviter sur un réseau partagé sans validation préalable.

### Laboratoire 1 — Convergence avec un feasible successor

**Objectif :** distinguer une bascule locale d’une computation diffusée.

1. Construis une topologie comportant deux chemins vers une destination.
2. Collecte la table topologique et note FD, RD, successor et feasible successor.
3. Désactive le lien du successor dans le laboratoire.
4. Observe si un feasible successor est sélectionné.
5. Compare la chronologie de DUAL, la RIB et le test de service.
6. Répète après avoir modifié la topologie afin que la condition de faisabilité ne soit plus satisfaite.
7. Explique pourquoi les deux scénarios ont des comportements différents.

**Livrable :** chronologie avant/après, sorties de commande et justification du chemin retenu.

### Laboratoire 2 — Analyse d’un incident ACTIVE/SIA

1. Prépare une topologie isolée de plusieurs routeurs.
2. Relève les voisins et les routes topologiques dans l’état stable.
3. Provoque une perte de chemin dans la maquette.
4. Collecte les états ACTIVE, les requêtes et les réponses disponibles.
5. Identifie les voisins qui doivent fournir une réponse.
6. Corrèle les logs avec la topologie.
7. Explique si le problème vient d’une panne physique, d’une instabilité, d’une portée de requêtes ou d’un autre défaut.
8. Restaure la topologie et répète le test.

Ne cherche pas à provoquer artificiellement une longue SIA sur un réseau de production. Le but est de comprendre la chronologie et de relier chaque observation à une hypothèse.

### Laboratoire 3 — Résumé et route plus spécifique manquante

1. Configure plusieurs préfixes contigus.
2. Active le résumé vers un routeur amont.
3. Vérifie les routes plus spécifiques avant le changement.
4. Retire un sous-préfixe en laboratoire.
5. Observe si l’agrégat continue d’être annoncé.
6. Teste le trafic vers le sous-préfixe retiré.
7. Vérifie si le trafic est rejeté localement ou envoyé vers un autre chemin.
8. Restaure le préfixe et confirme le retour à l’état normal.

**Livrable :** plan d’adressage, routes avant/après et analyse du risque de trou noir.

### Laboratoire 4 — Variance et perte d’un chemin

1. Crée deux chemins admissibles vers un préfixe.
2. Relève les métriques et vérifie la condition de faisabilité.
3. Configure une variance adaptée dans une maquette.
4. Observe la RIB et le comportement du forwarding.
5. Mesure plusieurs flux plutôt qu’un seul.
6. Désactive un chemin et mesure la capacité résiduelle.
7. Documente les variations de pertes et de latence.

**Critère de réussite :** démontrer la différence entre route installée et trafic effectivement distribué.

### Laboratoire 5 — Redistribution contrôlée EIGRP/OSPF

1. Construis deux domaines de routage de laboratoire.
2. Identifie les préfixes autorisés à franchir la frontière.
3. Configure la redistribution dans un seul sens.
4. Définis la métrique nécessaire et applique un tag.
5. Vérifie la route résultante et son tag.
6. Ajoute le filtre du sens inverse.
7. Introduis une route non autorisée dans le laboratoire et confirme qu’elle est bloquée.
8. Répète pour l’autre sens avec une politique distincte.
9. Vérifie qu’aucune route n’est réinjectée sans contrôle.

**Livrable :** tableau des préfixes originés, redistribués, filtrés et rejetés.

### Laboratoire 6 — Métrique étendue et compatibilité

1. Vérifie les fonctions prises en charge par l’image IOS/IOS XE utilisée.
2. Compare le mode EIGRP classique et le mode nommé si l’environnement le permet.
3. Relève les valeurs de métrique et les paramètres des interfaces.
4. Vérifie les K-values et la compatibilité des voisins.
5. Compare le chemin sélectionné dans les deux configurations prises en charge.
6. Documente les différences de sortie et les limites de simulation.

Ne transpose pas une configuration Wide Metrics à un équipement dont la prise en charge n’a pas été vérifiée.

### Laboratoire 7 — Route présente, application indisponible

1. Maintiens le voisinage EIGRP opérationnel.
2. Introduis un défaut contrôlé dans le chemin retour ou le filtrage applicatif.
3. Vérifie la table topologique et la RIB.
4. Teste le service depuis le client.
5. Compare les preuves de routage et les preuves applicatives.
6. Corrige le défaut et démontre le rétablissement du service.

Le but est de prouver qu’un protocole de routage ne peut pas, à lui seul, valider toutes les dépendances applicatives.

### Laboratoire 8 — Rapport d’incident multi-cause

Prépare une topologie comprenant une branche, un résumé et une frontière de redistribution. Introduis un seul défaut à la fois parmi les suivants : perte d’interface, route spécifique absente, filtre trop strict, métrique de redistribution incorrecte ou route retour absente.

Produis un rapport contenant la topologie, l’état initial, l’événement déclencheur, les sorties de commande, la première preuve en échec, la cause confirmée, la correction et les vérifications de non-régression.


## 12. Évaluation avec corrigés

**1. DUAL calcule-t-il un seul état global pour toutes les destinations ?**  
Non. Les états et computations sont suivis par destination. Une panne peut affecter plusieurs routes, chacune ayant son propre ensemble de voisins et de chemins candidats.

**2. Pourquoi un chemin peut-il être sans boucle sans être feasible successor ?**  
Parce que la condition de faisabilité est suffisante, mais pas nécessaire. Un chemin qui ne la satisfait pas n’est pas prouvé comme feasible successor par ce test, même s’il peut être sans boucle.

**3. Un voisin EIGRP actif garantit-il que le service fonctionne ?**  
Non. Le voisinage prouve seulement l’état de l’adjacence. Il faut examiner la topologie, la RIB, le prochain saut et le service réel.

**4. Pourquoi une route peut-elle rester en ACTIVE ?**  
Une computation peut attendre les réponses de voisins interrogés. Une instabilité distante, une réponse absente ou une topologie complexe peut prolonger le calcul.

**5. Une SIA-REPLY termine-t-elle la Query d’origine ?**  
Non. Elle indique notamment que le voisin est encore concerné par la computation. Elle ne remplace pas la réponse finale attendue à la Query.

**6. Pourquoi un résumé peut-il provoquer un trou noir ?**  
Un agrégat peut rester annoncé alors qu’un préfixe plus spécifique a disparu. Le trafic peut atteindre le routeur de résumé puis être rejeté, ou être envoyé vers un autre chemin inattendu.

**7. La variance suffit-elle pour installer n’importe quel chemin de métrique inférieure au seuil ?**  
Non. Le chemin doit aussi satisfaire les conditions de faisabilité et les autres règles d’admissibilité du protocole et de la plateforme.

**8. Les routes installées avec variance produisent-elles nécessairement une distribution égale ?**  
Non. La distribution dépend de la plateforme et du mécanisme de forwarding. Il faut mesurer plusieurs flux et vérifier le comportement réel.

**9. Un tag anti-boucle empêche-t-il par lui-même une route de revenir ?**  
Non. Une politique doit utiliser le tag pour accepter ou rejeter la route dans le bon sens.

**10. Pourquoi une SIA peut-elle apparaître alors qu’un voisinage local paraît stable ?**  
La réponse manquante peut concerner un voisin plus éloigné ou une computation qui s’étend au-delà du lien local. Il faut reconstruire le chemin des Query et examiner les journaux correspondants.

**11. Pourquoi comparer RIB et table topologique ?**  
La table topologique contient des chemins connus et des informations pour DUAL. La RIB reflète les routes retenues par le système. Une route connue n’est pas forcément installée comme chemin utilisé.

**12. Pourquoi les K-values ne doivent-elles pas être modifiées au hasard ?**  
Elles influencent le calcul de métrique et la compatibilité des voisins. Une modification non maîtrisée peut changer des décisions de chemin ou empêcher le voisinage de fonctionner.

**13. Quelle est la différence entre une métrique et une distance administrative ?**  
La métrique compare les chemins selon les règles EIGRP. La distance administrative est un mécanisme local à la plateforme qui permet de départager des sources de routage concurrentes.

**14. Pourquoi les fonctions Wide Metrics doivent-elles être vérifiées sur la plateforme ?**  
Les versions, modes et capacités ne sont pas identiques partout. Les calculs étendus, leur mise à l’échelle et leur disponibilité dépendent des fonctions prises en charge.

**15. Quelle preuve confirme la fin d’un incident de routage ?**  
Il faut vérifier le voisinage, la table topologique, la RIB/FIB et le service de bout en bout, puis consigner les résultats après le rétablissement.


## 13. Runbook de changement

### Avant le changement

- [ ] Sauvegarder la configuration et relever la version.
- [ ] Dessiner la topologie et identifier les dépendances communes.
- [ ] Relever les voisins et routes avant changement.
- [ ] Cartographier les résumés, tags, filtres et frontières de redistribution.
- [ ] Définir les tests, les critères de réussite et le retour arrière.
- [ ] Confirmer les commandes et fonctionnalités prises en charge.

### Pendant le changement

- [ ] Modifier une seule variable majeure à la fois.
- [ ] Enregistrer les événements horodatés.
- [ ] Surveiller les voisins et les changements d’état DUAL.
- [ ] Vérifier les routes spécifiques et les résumés.
- [ ] Contrôler les routes importées et les tags à chaque frontière.
- [ ] Interrompre l’intervention si des symptômes hors périmètre apparaissent.

### Après le changement

- [ ] Vérifier les routes dans la table topologique et la RIB.
- [ ] Vérifier le prochain saut et le forwarding.
- [ ] Tester les chemins aller et retour.
- [ ] Contrôler le service depuis une source représentative.
- [ ] Comparer les résultats avec l’état initial.
- [ ] Mettre à jour les schémas et la documentation opérationnelle.


## 14. Glossaire expert

| Terme | Définition |
|---|---|
| DUAL | Algorithme de convergence EIGRP qui calcule des chemins sans boucle |
| FD | Feasible Distance, référence locale de distance conservée par DUAL selon l’historique de la destination |
| RD | Reported Distance, distance annoncée par un voisin |
| Successor | Voisin utilisé pour le transfert vers une destination |
| Feasible successor | Chemin qui satisfait la condition `RD < FD` |
| PASSIVE | État stable d’une destination, sans computation diffusée en cours |
| ACTIVE | État dans lequel DUAL effectue une computation coordonnée |
| QUERY | Requête utilisée dans une computation diffusée |
| REPLY | Réponse à une Query |
| SIA | Stuck-in-Active, computation qui ne se termine pas dans les délais attendus |
| Summarization | Agrégation de plusieurs préfixes en une route plus générale |
| Null0 | Destination de rejet utilisée dans certains mécanismes de résumé |
| Variance | Facteur de métrique permettant certains chemins à coût inégal |
| Route tag | Marqueur utilisé par les politiques de redistribution |
| Wide Metrics | Fonction EIGRP permettant des calculs de métrique étendus sur les plateformes prises en charge |
| RIB | Base de routes retenues par le système |
| FIB | Structure de transfert des paquets |


## Références techniques

- **RFC 7868 — Cisco’s Enhanced Interior Gateway Routing Protocol (EIGRP)** : https://www.rfc-editor.org/rfc/rfc7868.html — description informative sur DUAL, la condition de faisabilité, les tables et les messages EIGRP.
- **Cisco — Troubleshoot EIGRP Common Issues** : https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/118974-technote-eigrp-00.html — symptômes SIA, commandes de diagnostic et pistes d’investigation.
- **Cisco IOS XE — EIGRP Wide Metrics** : https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-routing/b-ip-routing/m_ire-wid-met.html — métriques étendues, mise à l’échelle et dépendances de plateforme.
- **Cisco — EIGRP Configuration Guide** : https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_eigrp/configuration/15-2s/config-eigrp.html — référence de configuration à adapter au système utilisé.

La RFC 7868 est une spécification informative et non une norme Internet Standards Track. Les commandes et fonctions réelles doivent être vérifiées pour l’équipement, la version et le mode EIGRP utilisés.

## Conclusion

Un EIGRP expert ne se définit pas par le nombre de commandes mémorisées, mais par la capacité à expliquer un changement de route, mesurer une convergence, limiter la propagation d’un incident et corriger une cause démontrée.

La règle opérationnelle demeure :

1. observer ;
2. formuler une hypothèse ;
3. collecter les preuves ;
4. isoler une variable ;
5. appliquer une correction contrôlée ;
6. vérifier la route, le forwarding et le service ;
7. documenter le résultat et le retour arrière.

Après maîtrise de ce cours, construis une campagne automatisée de validation EIGRP afin de contrôler les routes attendues, les changements de topologie, les frontières de redistribution et le comportement en cas de panne.
