# IS-IS — Niveau Expert

## Positionnement dans le parcours

Ce cours prolonge **IS-IS — Niveau Intermédiaire**. Il suppose que vous savez déjà lire un NET, distinguer les niveaux L1 et L2, interpréter les adjacencies, la LSDB, les LSP, les CSNP/PSNP, le DIS, les métriques étendues et les mécanismes de base du route leaking. Le niveau expert se concentre sur la conception et l'exploitation d'un domaine à grande échelle : contrôle fin de la diffusion d'état de liens, protection pendant les maintenances, convergence, ingénierie des métriques, interopérabilité, authentification, extensions multi-topologies et Flex-Algorithm.

> **Cadre des exemples :** les commandes illustratives s'inspirent principalement de Cisco IOS/IOS XE. La syntaxe, la disponibilité des fonctions et leur portée varient selon les plateformes et versions. Certaines commandes liées à Segment Routing, Flex-Algorithm, BFD ou à la limitation du flooding peuvent être différentes, voire absentes, sur un équipement donné. Avant toute application, vérifiez l'aide CLI et la documentation correspondant exactement à l'image logicielle et au matériel du laboratoire. Ce document est un cours de conception et de laboratoire, pas un jeu de commandes à coller directement en production.

## Objectifs du niveau expert

À la fin du cours, vous devez pouvoir :

- concevoir les frontières L1/L2 à partir des objectifs de convergence, de visibilité et de résilience ;
- expliquer les effets des fragments LSP, du bit Overload, du bit Attached, du pseudonœud et des changements de séquence ;
- séparer les causes de convergence lente entre détection, flooding, calcul SPF, programmation RIB/FIB et résolution du prochain saut ;
- construire une stratégie de métriques qui ne repose pas sur des valeurs arbitraires et qui préserve la cohérence du domaine ;
- contrôler les annonces inter-niveaux et éviter les boucles ou chemins sous-optimaux liés au leaking ;
- déployer prudemment IPv6, Multi-Topology, authentification et extensions de trafic ;
- comprendre le principe de Flex-Algorithm et les prérequis d'une intégration Segment Routing ;
- analyser une panne à partir d'hypothèses testables et d'observations provenant de plusieurs routeurs.


## 1. Concevoir le domaine : topologie, frontières et responsabilités

### 1.1 Choisir L1/L2 selon le problème à résoudre

Une conception IS-IS n'est pas « L1 dans les petites zones et L2 partout ailleurs » par réflexe. Il faut d'abord définir ce que chaque niveau doit représenter.

- **L1** limite la connaissance détaillée de la topologie à une aire. Il convient aux domaines où l'on souhaite une visibilité locale et un calcul SPF localisé.
- **L2** forme la topologie d'interconnexion entre les routeurs de niveau 2. Il doit fournir des chemins cohérents entre les aires et être dimensionné pour la taille, la redondance et les changements de cette ossature.
- **L1/L2** relie une aire à l'ossature L2 et participe aux calculs des deux niveaux. Ces routeurs constituent des points structurants : leur disponibilité, leurs politiques et leur charge de contrôle ont un impact plus large.

Le nombre d'aires n'est pas une fin en soi. Multiplier les aires augmente le nombre de frontières et les décisions de distribution des préfixes. Une seule grande aire L2 peut aussi être adaptée à certains réseaux si la topologie et la capacité des routeurs le permettent. La bonne limite est celle qui réduit le coût d'exploitation sans créer une concentration excessive du trafic ou des risques de panne.

### 1.2 Topologie logique et topologie physique

Le graphe de routage ne doit pas être confondu avec le plan de câblage. Deux liaisons physiques ne constituent pas nécessairement deux chemins de routage indépendants si les deux sont soumises au même risque commun : conduit fibre partagé, alimentation unique, même châssis, même site ou même routeur de transit. Inversement, une topologie logique en triangle peut être physiquement vulnérable si deux côtés partagent un seul câble ou équipement.

La conception doit documenter au moins :

1. les liens et interfaces qui portent réellement le trafic ;
2. les dépendances de risque (site, fourreau, énergie, équipement, opérateur) ;
3. les niveaux IS-IS sur chaque lien ;
4. les métriques et chemins de secours attendus ;
5. les routeurs dont la perte ne doit pas rendre une aire isolée.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 370" role="img" aria-labelledby="isis-exp-design-title isis-exp-design-desc">
  <title id="isis-exp-design-title">Exemple d'architecture à deux niveaux</title>
  <desc id="isis-exp-design-desc">Deux aires L1 distinctes sont raccordées à une ossature L2 redondante par des routeurs L1/L2. Le dessin distingue l'étendue des bases L1 et L2.</desc>
  <defs><marker id="isis-exp-design-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3 z" fill="#8293a8"/></marker></defs>
  <rect width="960" height="370" rx="18" fill="#0b1220"/>
  <text x="480" y="32" fill="#f8fafc" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700">Séparer visibilité locale et transit inter-aires</text>
  <rect x="28" y="68" width="280" height="250" rx="14" fill="#10243a" stroke="#60a5fa" stroke-width="1.5" stroke-dasharray="7 5"/>
  <rect x="652" y="68" width="280" height="250" rx="14" fill="#10243a" stroke="#60a5fa" stroke-width="1.5" stroke-dasharray="7 5"/>
  <text x="168" y="93" fill="#93c5fd" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" font-weight="700">Aire L1-A</text>
  <text x="792" y="93" fill="#93c5fd" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" font-weight="700">Aire L1-B</text>
  <g font-family="Arial,sans-serif" font-size="13" text-anchor="middle">
    <rect x="68" y="129" width="82" height="48" rx="9" fill="#1e3a5f" stroke="#60a5fa"/><text x="109" y="158" fill="#dbeafe">A1</text>
    <rect x="188" y="129" width="82" height="48" rx="9" fill="#1e3a5f" stroke="#60a5fa"/><text x="229" y="158" fill="#dbeafe">A2</text>
    <rect x="68" y="218" width="82" height="48" rx="9" fill="#1e3a5f" stroke="#60a5fa"/><text x="109" y="247" fill="#dbeafe">A3</text>
    <path d="M150 153 H188 M109 177 V218 M229 177 V198 H150 V218" stroke="#7dd3fc" stroke-width="2" fill="none"/>
    <rect x="692" y="129" width="82" height="48" rx="9" fill="#1e3a5f" stroke="#60a5fa"/><text x="733" y="158" fill="#dbeafe">B1</text>
    <rect x="812" y="129" width="82" height="48" rx="9" fill="#1e3a5f" stroke="#60a5fa"/><text x="853" y="158" fill="#dbeafe">B2</text>
    <rect x="692" y="218" width="82" height="48" rx="9" fill="#1e3a5f" stroke="#60a5fa"/><text x="733" y="247" fill="#dbeafe">B3</text>
    <path d="M774 153 H812 M733 177 V218 M853 177 V198 H774 V218" stroke="#7dd3fc" stroke-width="2" fill="none"/>
  </g>
  <rect x="350" y="103" width="260" height="180" rx="14" fill="#172c28" stroke="#34d399" stroke-width="1.5"/>
  <text x="480" y="128" fill="#6ee7b7" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" font-weight="700">Ossature L2</text>
  <g font-family="Arial,sans-serif" font-size="13" text-anchor="middle">
    <rect x="378" y="155" width="86" height="50" rx="9" fill="#17483c" stroke="#34d399"/><text x="421" y="175" fill="#d1fae5">C1</text><text x="421" y="192" fill="#a7f3d0" font-size="11">L1/L2</text>
    <rect x="496" y="155" width="86" height="50" rx="9" fill="#17483c" stroke="#34d399"/><text x="539" y="175" fill="#d1fae5">C2</text><text x="539" y="192" fill="#a7f3d0" font-size="11">L1/L2</text>
    <path d="M464 169 H496 M464 192 H496 M421 155 V145 H539 V155" stroke="#6ee7b7" fill="none" stroke-width="2"/>
    <text x="480" y="237" fill="#d1fae5" font-size="12">Chemins L2 redondants</text><text x="480" y="255" fill="#a7f3d0" font-size="11">Calcul et flooding propres au niveau 2</text>
  </g>
  <path d="M308 153 H350 M610 153 H652 M308 245 H378 V205 M582 205 H652" stroke="#fbbf24" stroke-width="2.5" fill="none" marker-end="url(#isis-exp-design-arrow)"/>
  <text x="480" y="346" fill="#cbd5e1" text-anchor="middle" font-family="Arial,sans-serif" font-size="13">Les frontières limitent les détails L1 ; l'ossature L2 assure l'interconnexion.</text>
</svg>

### 1.3 Éviter les frontières fragiles

Dans une aire, un routeur L1 peut utiliser une route par défaut vers un routeur L1/L2 qui annonce l'attribut Attached. Si plusieurs sorties sont possibles, il faut vérifier que le comportement sélectionné correspond au plan d'ingénierie. La meilleure sortie logique n'est pas forcément le meilleur chemin physique pour chaque destination.

Une conception robuste tient compte de :

- **Redondance des frontières** : une aire importante ne devrait pas dépendre d'un seul routeur L1/L2, sauf contrainte clairement acceptée.
- **Cohérence des métriques** : une métrique L1 optimisée localement ne garantit pas un chemin inter-aire optimal si la métrique L2 ou la méthode de sortie diffère.
- **Distribution des préfixes** : la route par défaut simplifie l'aire mais cache la topologie externe ; le leaking de préfixes apporte de la précision au prix d'une LSDB plus chargée et de davantage de règles.
- **Convergence attendue** : la panne d'une frontière peut déplacer simultanément un volume important de trafic, même si la reconvergence locale reste rapide.

### 1.4 L'aire n'est pas un domaine de sécurité

Une aire limite la topologie L1, mais elle n'est pas une frontière de confiance au sens d'un pare-feu. IS-IS propage des informations de routage au sein du niveau et la compromission d'un routeur ayant la capacité d'injecter des LSP peut influencer les décisions de chemin. Utilisez des mécanismes d'authentification, des contrôles d'accès au plan de contrôle, une gestion sûre des identifiants et des pratiques de changement disciplinées.


## 2. LSP avancés : fragments, purge et bit Overload

### 2.1 Pourquoi un routeur peut avoir plusieurs LSP

Le contenu d'état de liens d'un système peut être réparti entre un LSP de base et des fragments numérotés. La taille maximale encodable est contrainte par les formats de PDU, la MTU, les TLV présentes et l'implémentation. Les extensions (par exemple IPv6, informations TE ou Segment Routing) peuvent augmenter le volume annoncé ; une topologie qui fonctionnait avec des LSP peu volumineux peut approcher des limites après ajout d'attributs.

Conséquence opérationnelle : ne vérifiez pas uniquement le premier LSP d'un routeur. Inspectez la liste complète de ses LSP et comparez les fragments, leurs numéros de séquence, leur durée de vie et le contenu des TLV. Un préfixe ou un attribut absent peut se trouver dans un fragment différent, ou avoir été retiré par une mauvaise formation de l'annonce.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 325" role="img" aria-labelledby="isis-exp-frag-title isis-exp-frag-desc">
  <title id="isis-exp-frag-title">Fragmentation du contenu LSP</title>
  <desc id="isis-exp-frag-desc">Les informations d'un routeur sont divisées entre plusieurs fragments. Les voisins conservent chaque LSP selon son identifiant, sa séquence, son checksum et sa durée de vie.</desc>
  <rect width="960" height="325" rx="18" fill="#0b1220"/><text x="480" y="32" fill="#f8fafc" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700">Une identité système, plusieurs fragments LSP</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="48" y="83" width="170" height="78" rx="12" fill="#162a42" stroke="#60a5fa"/><text x="133" y="112" fill="#93c5fd" font-size="16" font-weight="700">R7</text><text x="133" y="136" fill="#e2e8f0" font-size="13">Informations locales</text>
    <path d="M218 122 H273" stroke="#94a3b8" stroke-width="2.5"/>
    <path d="M265 116 L275 122 L265 128" fill="none" stroke="#94a3b8" stroke-width="2.5"/>
    <rect x="283" y="67" width="196" height="56" rx="9" fill="#163a33" stroke="#34d399"/><text x="381" y="89" fill="#a7f3d0" font-size="14" font-weight="700">LSP ID : R7.00-00</text><text x="381" y="108" fill="#d1fae5" font-size="12">Fragment de base</text>
    <rect x="283" y="134" width="196" height="56" rx="9" fill="#163a33" stroke="#34d399"/><text x="381" y="156" fill="#a7f3d0" font-size="14" font-weight="700">LSP ID : R7.00-01</text><text x="381" y="175" fill="#d1fae5" font-size="12">Fragment additionnel</text>
    <rect x="283" y="201" width="196" height="56" rx="9" fill="#163a33" stroke="#34d399"/><text x="381" y="223" fill="#a7f3d0" font-size="14" font-weight="700">LSP ID : R7.00-02</text><text x="381" y="242" fill="#d1fae5" font-size="12">Autres TLV / sous-TLV</text>
    <path d="M479 95 H536 M479 162 H536 M479 229 H536" stroke="#94a3b8" stroke-width="2"/>
    <rect x="540" y="83" width="370" height="174" rx="12" fill="#1b2433" stroke="#64748b"/><text x="725" y="110" fill="#e2e8f0" font-size="16" font-weight="700">Contrôles par LSP</text>
    <text x="725" y="139" fill="#cbd5e1" font-size="13">Identité / numéro de séquence</text><text x="725" y="163" fill="#cbd5e1" font-size="13">Checksum / remaining lifetime</text><text x="725" y="187" fill="#cbd5e1" font-size="13">Contenu TLV et capacité de MTU</text><text x="725" y="220" fill="#fcd34d" font-size="12">Inspecter la collection complète</text><text x="725" y="239" fill="#fcd34d" font-size="12">pas seulement le LSP 00-00</text>
    <text x="480" y="294" fill="#94a3b8" font-size="12">Le suffixe exact des identifiants varie selon la représentation de la plateforme.</text>
  </g>
</svg>

### 2.2 Comprendre une purge

Une purge retire un LSP de la base. Elle ne doit pas être confondue avec un simple rafraîchissement de l'annonce. Les mécanismes de purge et d'identification de l'origine sont importants lors des suppressions de fragments, du retrait d'un routeur ou de la récupération après une anomalie de LSDB. Les règles exactes de réception des purges sont encadrées par les spécifications et extensions d'authentification ; le comportement peut être affecté par des équipements anciens ou non conformes.

En opération, si un préfixe disparaît, vérifiez s'il a été retiré du LSP d'origine, si la nouvelle version a été diffusée, et si une purge a été reçue ou créée. Une simple absence dans une sortie partielle ne permet pas de conclure à une purge : confirmez l'ID de LSP, son niveau, le fragment concerné et l'état de la LSDB.

### 2.3 Bit Overload : un signal de transit, pas un arrêt du routeur

Le **bit Overload (OL)** permet à un système d'indiquer qu'il ne devrait pas être choisi comme route de transit par les calculs qui traitent cette information. Il est utile pendant le démarrage, une maintenance ou lorsqu'un routeur ne peut temporairement pas assurer le transit attendu.

Attention à ce qu'il ne signifie pas :

- il ne coupe pas forcément ses adjacencies ;
- il ne signifie pas automatiquement que tous ses préfixes locaux doivent disparaître ;
- il ne remplace ni une politique de routage, ni un arrêt contrôlé des interfaces, ni un contrôle du plan de transfert ;
- il ne garantit pas qu'aucun paquet ne traversera l'équipement dans toutes les conditions. Le résultat dépend de la façon dont les routeurs calculent les chemins et de la nature de la route.

Une utilisation typique consiste à activer temporairement Overload sur le routeur en maintenance, à vérifier que les autres routeurs ont reçu la nouvelle information, puis à effectuer la maintenance. Au retour, on enlève Overload seulement lorsque le matériel, les interfaces, les adjacencies, la RIB/FIB et les services nécessaires sont réellement prêts.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 355" role="img" aria-labelledby="isis-exp-overload-title isis-exp-overload-desc">
  <title id="isis-exp-overload-title">Usage contrôlé du bit Overload</title>
  <desc id="isis-exp-overload-desc">Dans un triangle, le routeur central est annoncé avec Overload. Les chemins de transit devraient favoriser le trajet via l'autre routeur, tandis que les préfixes locaux du routeur peuvent rester annoncés.</desc>
  <defs><marker id="isis-exp-ol-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3 z" fill="#a5b4c8"/></marker></defs>
  <rect width="960" height="355" rx="18" fill="#0b1220"/><text x="480" y="32" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21" font-weight="700">Réduire le transit par un routeur en maintenance</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <circle cx="220" cy="156" r="44" fill="#163a33" stroke="#34d399" stroke-width="2"/><text x="220" y="151" fill="#d1fae5" font-size="17" font-weight="700">R1</text><text x="220" y="171" fill="#a7f3d0" font-size="12">Source</text>
    <circle cx="480" cy="156" r="48" fill="#442b20" stroke="#fb923c" stroke-width="2.5"/><text x="480" y="148" fill="#ffedd5" font-size="17" font-weight="700">R2</text><text x="480" y="168" fill="#fed7aa" font-size="12">OL = 1</text>
    <circle cx="740" cy="156" r="44" fill="#163a33" stroke="#34d399" stroke-width="2"/><text x="740" y="151" fill="#d1fae5" font-size="17" font-weight="700">R3</text><text x="740" y="171" fill="#a7f3d0" font-size="12">Destination</text>
    <path d="M264 156 H428 M532 156 H696" stroke="#fb923c" stroke-width="2.5" stroke-dasharray="7 6" fill="none"/>
    <path d="M251 124 L705 124" stroke="#34d399" stroke-width="3" fill="none" marker-end="url(#isis-exp-ol-arrow)"/><text x="480" y="105" fill="#6ee7b7" font-size="13" font-weight="700">Chemin de transit alternatif attendu</text>
    <path d="M245 193 Q480 296 715 193" stroke="#34d399" stroke-width="2" stroke-dasharray="5 5" fill="none"/>
    <text x="480" y="257" fill="#cbd5e1" font-size="13">Les préfixes locaux de R2 peuvent rester annoncés</text><text x="480" y="278" fill="#94a3b8" font-size="12">Overload influence le calcul du transit ; vérifier les routes après propagation.</text>
    <rect x="200" y="309" width="560" height="28" rx="7" fill="#30271b" stroke="#fbbf24"/><text x="480" y="328" fill="#fde68a" font-size="12">Ne retirer OL qu'après validation du plan de contrôle et du plan de transfert.</text>
  </g>
</svg>

### 2.4 Overload au démarrage et mise en service

Un mécanisme « overload on startup » peut annoncer l'état Overload au démarrage pendant une durée ou jusqu'à une condition configurée. Il faut toutefois vérifier ce que la fonction couvre réellement. Une minuterie aveugle peut retirer le bit avant que les sessions, la programmation matériel ou les services soient prêts ; une condition contrôlée est préférable lorsqu'elle existe.

Procédure recommandée :

1. définir quels services doivent être opérationnels avant d'autoriser le transit ;
2. activer une protection Overload adaptée à la plateforme ;
3. confirmer la propagation du bit sur les LSP et le recalcul des chemins distants ;
4. effectuer les vérifications locales : liens, voisinages, préfixes, MTU, RIB/FIB, CPU et mémoire ;
5. retirer la protection et valider le retour du trafic sur le chemin attendu ;
6. vérifier qu'aucun voisin ne conserve une information ancienne après la transition.

### 2.5 Bit Attached et route par défaut L1

Dans le fonctionnement à deux niveaux, un routeur L1/L2 peut annoncer l'attribut **Attached (ATT)** à ses voisins L1 pour signaler une connectivité vers d'autres aires via L2. Les routeurs L1 peuvent alors utiliser une route par défaut vers un routeur de sortie, selon les règles et options de l'implémentation. Cela simplifie la base L1, mais ne garantit pas à lui seul le choix d'une sortie optimal pour chaque préfixe ou le meilleur partage de charge.

Lorsqu'une aire dispose de plusieurs sorties, examinez l'ensemble des options : coût vers chaque frontière, annonces par défaut, politiques de préférence, leaking éventuel et état de la topologie L2. Une sortie présente dans la LSDB n'est pas automatiquement équivalente à une sortie fonctionnelle.


## 3. Convergence : détecter, diffuser, calculer, programmer

### 3.1 Décomposer le temps de convergence

Le mot « convergence » regroupe plusieurs délais :

1. **Détection** : le routeur détecte qu'un lien ou un voisin n'est plus opérationnel (perte physique, expiration d'IIH, BFD ou autre mécanisme).
2. **Origination** : le routeur construit une nouvelle information LSP décrivant le changement.
3. **Flooding** : la mise à jour atteint les routeurs concernés et les LSDB convergent.
4. **Calcul** : SPF ou un calcul incrémental recalcule les chemins affectés.
5. **Installation** : la RIB sélectionne les routes, les adjacences de transfert sont résolues et la FIB matérielle est programmée.
6. **Rétablissement du service** : les paquets, applications et chemins retour fonctionnent de nouveau.

Réduire le timer Hello ne résout pas un goulot d'étranglement de flooding, de CPU ou de programmation FIB. À l'inverse, optimiser SPF n'aide pas si la panne du lien n'est détectée qu'après plusieurs secondes. Il faut mesurer chaque phase.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" role="img" aria-labelledby="isis-exp-conv-title isis-exp-conv-desc">
  <title id="isis-exp-conv-title">Chaîne de convergence</title>
  <desc id="isis-exp-conv-desc">Six étapes de la détection de panne au rétablissement du service, chacune avec une mesure opérationnelle associée.</desc>
  <defs><marker id="isis-exp-conv-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3 z" fill="#93a4b8"/></marker></defs>
  <rect width="960" height="360" rx="18" fill="#0b1220"/><text x="480" y="32" fill="#f8fafc" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700">Mesurer les étapes plutôt que parler d'un seul timer</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="24" y="83" width="140" height="96" rx="11" fill="#263043" stroke="#f87171"/><text x="94" y="109" fill="#fecaca" font-size="14" font-weight="700">1. Détection</text><text x="94" y="132" fill="#e2e8f0" font-size="12">Lien / IIH / BFD</text><text x="94" y="154" fill="#fca5a5" font-size="11">Temps de panne</text>
    <rect x="181" y="83" width="140" height="96" rx="11" fill="#1c3046" stroke="#60a5fa"/><text x="251" y="109" fill="#bfdbfe" font-size="14" font-weight="700">2. Origination</text><text x="251" y="132" fill="#e2e8f0" font-size="12">Nouveau LSP</text><text x="251" y="154" fill="#93c5fd" font-size="11">Délai de génération</text>
    <rect x="338" y="83" width="140" height="96" rx="11" fill="#182f3b" stroke="#22d3ee"/><text x="408" y="109" fill="#a5f3fc" font-size="14" font-weight="700">3. Flooding</text><text x="408" y="132" fill="#e2e8f0" font-size="12">LSDB à jour</text><text x="408" y="154" fill="#67e8f9" font-size="11">Propagation</text>
    <rect x="495" y="83" width="140" height="96" rx="11" fill="#233126" stroke="#4ade80"/><text x="565" y="109" fill="#bbf7d0" font-size="14" font-weight="700">4. Calcul</text><text x="565" y="132" fill="#e2e8f0" font-size="12">SPF / incrémental</text><text x="565" y="154" fill="#86efac" font-size="11">Temps CPU</text>
    <rect x="652" y="83" width="140" height="96" rx="11" fill="#362b20" stroke="#fbbf24"/><text x="722" y="109" fill="#fde68a" font-size="14" font-weight="700">5. Installation</text><text x="722" y="132" fill="#e2e8f0" font-size="12">RIB / FIB</text><text x="722" y="154" fill="#fcd34d" font-size="11">Programmation</text>
    <rect x="809" y="83" width="127" height="96" rx="11" fill="#30233a" stroke="#c084fc"/><text x="872" y="109" fill="#e9d5ff" font-size="14" font-weight="700">6. Service</text><text x="872" y="132" fill="#e2e8f0" font-size="12">Trafic rétabli</text><text x="872" y="154" fill="#d8b4fe" font-size="11">Test de bout en bout</text>
    <path d="M164 131 H176 M321 131 H333 M478 131 H490 M635 131 H647 M792 131 H804" stroke="#93a4b8" stroke-width="2" marker-end="url(#isis-exp-conv-arrow)"/>
    <rect x="100" y="225" width="760" height="79" rx="12" fill="#131d2d" stroke="#475569"/><text x="480" y="251" fill="#e2e8f0" font-size="15" font-weight="700">Diagnostic exploitable</text><text x="480" y="275" fill="#cbd5e1" font-size="13">Horodater la perte, la nouvelle LSDB, la route active et le premier paquet réussi.</text><text x="480" y="292" fill="#94a3b8" font-size="12">Un ping seul ne montre pas quelle étape a consommé le temps.</text>
  </g>
</svg>

### 3.2 Timers, throttling et risque d'oscillation

Les timers Hello, l'intervalle de génération LSP, les politiques de throttling SPF et les fonctions de propagation rapide modifient des phases différentes du système. Leur objectif est de trouver un équilibre entre réactivité, charge de calcul et stabilité.

- **Timers de maintien** trop élevés : panne lente à détecter quand la couche physique ne signale pas la perte.
- **Timers trop bas** : sensibilité accrue aux pertes momentanées, à la congestion du contrôle ou à une surcharge du routeur ; davantage de flaps possibles.
- **Throttling de génération LSP** : limite les annonces répétées pendant une rafale de changements, au risque d'allonger la convergence si les délais sont excessifs.
- **Throttling SPF** : évite de recalculer sans cesse pendant un événement instable, mais un délai trop important garde les anciennes routes plus longtemps.
- **Flooding rapide** : peut accélérer la propagation des LSP critiques, mais augmente l'activité du contrôle. La prise en charge et la stratégie doivent être évaluées sur la plateforme.

Ne choisissez pas des timers uniquement parce qu'ils sont « rapides ». Mesurez la fréquence réelle des pannes, le taux de perte, le temps de CPU et le pire scénario de convergence. La configuration doit tolérer un pic de changements sans épuiser les ressources.

### 3.3 BFD : détection rapide avec conditions

BFD (*Bidirectional Forwarding Detection*) peut détecter la perte de connectivité entre voisins à une échelle de temps plus fine que certains mécanismes Hello. IS-IS peut utiliser l'événement BFD pour réagir rapidement lorsque la plateforme prend cette intégration en charge.

BFD n'est pas une garantie universelle de convergence en millisecondes. Le délai effectif dépend de la négociation des intervalles, des multiplicateurs, du matériel, de la charge, du type de session et de la réaction du protocole de routage. Des valeurs extrêmement agressives peuvent provoquer des faux positifs, en particulier sur des plateformes chargées ou des chemins qui partagent le plan de contrôle.

Plan de déploiement conseillé :

1. valider le support BFD sur les deux extrémités et le type de liaison ;
2. démarrer avec des valeurs recommandées pour la plateforme ;
3. observer les sessions et les événements pendant les tests ;
4. provoquer une vraie coupure, mais aussi des conditions de charge ou de perte contrôlées ;
5. comparer les temps de détection, de flooding, de RIB/FIB et de rétablissement applicatif ;
6. garder une procédure de désactivation si BFD génère des instabilités.

### 3.4 Microboucles et convergence asynchrone

Lors d'une panne, tous les routeurs ne mettent pas à jour leur FIB au même instant. Un routeur peut déjà envoyer un paquet vers le nouveau prochain saut alors que ce voisin suit encore l'ancien chemin. Pendant cette fenêtre, des paquets peuvent tourner temporairement entre routeurs : c'est une microboucle.

Les microboucles sont différentes d'une boucle persistante causée par une erreur durable de politique ou d'annonce. Elles résultent de l'ordre et du décalage des mises à jour dans le plan de transfert. Les réseaux sensibles peuvent examiner des mécanismes de convergence ordonnée, des techniques de protection locale ou les fonctions proposées par leur plateforme. Leur disponibilité et leur compatibilité avec IS-IS, la famille d'adresses et le plan de transfert doivent être testées explicitement.

Dans un diagnostic, recherchez une perte transitoire limitée à quelques secondes, des TTL qui diminuent ou des captures montrant un paquet entre les mêmes routeurs. Ne modifiez pas les métriques pour « corriger » une microboucle sans confirmer la cause : un changement de coût peut simplement déplacer le phénomène.

### 3.5 Séparer panne de routage et panne de transfert

Un cas expert classique : la LSDB est cohérente, la commande de route affiche le bon chemin, mais le trafic est perdu. Les hypothèses à tester comprennent :

- FIB matériel non synchronisée avec la RIB ;
- voisin de couche 2 ou résolution ARP/ND manquante ;
- MTU insuffisante ou fragmentation inadaptée ;
- ACL, uRPF, pare-feu ou politique de contrôle ;
- asymétrie du chemin retour ;
- ECMP avec un membre défaillant ;
- limitation du plan de contrôle ou épuisement d'une ressource matérielle.

Validez séparément le chemin aller et le chemin retour, et comparez un flux qui fonctionne à un flux qui échoue. Une capture sur un seul point peut manquer une asymétrie ou un défaut de programmation sur le routeur suivant.


## 4. Ingénierie des métriques : construire une politique cohérente

### 4.1 La métrique est un modèle de préférence, pas une mesure parfaite

La métrique IS-IS exprime une préférence de chemin. Elle ne mesure pas automatiquement la latence, les pertes, le coût commercial ou le débit réel du lien. À moins d'utiliser une extension et une architecture qui exploitent explicitement ces attributs, SPF travaille avec les valeurs diffusées par les routeurs.

Une stratégie de métriques commence par un objectif clair : réduire la latence, privilégier un chemin de capacité élevée, éviter un lien facturé, réserver une route de secours ou répartir le trafic. Il faut ensuite transformer cet objectif en règles stables et documentées.

Mauvaise stratégie : attribuer une métrique faible au lien préféré, puis augmenter au cas par cas toutes les autres valeurs sans plan cohérent. Les valeurs deviennent illisibles et chaque changement local peut avoir des effets globaux inattendus.

Meilleure stratégie :

1. fixer une plage de référence et des classes de chemins ;
2. définir des écarts de métriques significatifs entre chemin primaire et secours ;
3. conserver une marge pour de futurs liens et extensions ;
4. vérifier les sommes de métriques sur les itinéraires complets ;
5. tester les coupures et les changements de topologie ;
6. publier un tableau de référence que les équipes peuvent auditer.

### 4.2 Wide metrics et compatibilité

Les métriques étendues (souvent appelées **wide metrics**) permettent des valeurs plus grandes que les métriques étroites historiques et sont transportées par des TLV étendus. Il est important d'assurer la cohérence de configuration sur tout le domaine utile. Un routeur ancien ou mal configuré qui n'utilise pas la même représentation peut créer une divergence entre les valeurs attendues et les valeurs effectivement utilisées.

Avant une migration :

- inventorier tous les routeurs et leurs versions ;
- confirmer les TLV et formats pris en charge ;
- vérifier la configuration sur les interfaces et niveaux pertinents ;
- comparer les métriques affichées avec celles annoncées dans la LSDB ;
- basculer en fenêtre maîtrisée, avec un plan de retour arrière ;
- contrôler la RIB/FIB et les chemins après chaque étape.

Ne supposez pas qu'une commande « wide metric » globalement présente garantit que toutes les annonces ont été encodées comme attendu. Vérifiez le contenu opérationnel, notamment dans les environnements multi-constructeurs.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="isis-exp-metric-title isis-exp-metric-desc">
  <title id="isis-exp-metric-title">Exemple de calcul et de choix de métrique</title>
  <desc id="isis-exp-metric-desc">Deux chemins entre une source et une destination ont des coûts cumulés différents. Le schéma rappelle qu'une métrique est une politique de préférence et doit être interprétée sur le chemin entier.</desc>
  <rect width="960" height="350" rx="18" fill="#0b1220"/><text x="480" y="32" fill="#f8fafc" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700">Calculer le coût de bout en bout</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <circle cx="92" cy="173" r="31" fill="#1e3a5f" stroke="#60a5fa" stroke-width="2"/><text x="92" y="178" fill="#dbeafe" font-size="14" font-weight="700">SRC</text>
    <circle cx="868" cy="173" r="31" fill="#1e3a5f" stroke="#60a5fa" stroke-width="2"/><text x="868" y="178" fill="#dbeafe" font-size="14" font-weight="700">DST</text>
    <circle cx="355" cy="105" r="30" fill="#183329" stroke="#34d399" stroke-width="2"/><text x="355" y="110" fill="#d1fae5" font-size="14" font-weight="700">P1</text>
    <circle cx="610" cy="105" r="30" fill="#183329" stroke="#34d399" stroke-width="2"/><text x="610" y="110" fill="#d1fae5" font-size="14" font-weight="700">P2</text>
    <circle cx="480" cy="255" r="30" fill="#3a2b20" stroke="#fb923c" stroke-width="2"/><text x="480" y="260" fill="#ffedd5" font-size="14" font-weight="700">S1</text>
    <path d="M121 160 L326 116" stroke="#34d399" stroke-width="3" fill="none"/><path d="M385 105 H580" stroke="#34d399" stroke-width="3"/><path d="M640 116 L838 160" stroke="#34d399" stroke-width="3"/>
    <text x="223" y="122" fill="#6ee7b7" font-size="13">coût 10</text><text x="482" y="91" fill="#6ee7b7" font-size="13">coût 15</text><text x="737" y="122" fill="#6ee7b7" font-size="13">coût 10</text>
    <path d="M110 199 L454 247" stroke="#fb923c" stroke-width="2.5" stroke-dasharray="7 5" fill="none"/><path d="M507 247 L850 199" stroke="#fb923c" stroke-width="2.5" stroke-dasharray="7 5" fill="none"/>
    <text x="253" y="229" fill="#fdba74" font-size="13">coût 30</text><text x="712" y="229" fill="#fdba74" font-size="13">coût 30</text>
    <rect x="280" y="292" width="400" height="35" rx="8" fill="#172b25" stroke="#34d399"/><text x="480" y="314" fill="#d1fae5" font-size="14" font-weight="700">Chemin haut = 10 + 15 + 10 = 35</text>
    <text x="480" y="55" fill="#94a3b8" font-size="12">Le coût complet du chemin est la somme des métriques de ses liens.</text>
  </g>
</svg>

### 4.3 ECMP et limites du partage de charge

L'ECMP (*Equal-Cost Multi-Path*) permet à la FIB d'utiliser plusieurs prochains sauts de coût égal. Il n'implique pas toujours une répartition strictement égale du nombre de paquets ou du débit. Beaucoup de plateformes répartissent par flux pour préserver l'ordre des paquets ; un gros flux peut donc dominer un seul chemin. Les algorithmes de hachage, le nombre maximal de chemins et les mécanismes d'équilibrage varient selon le système.

Les vérifications pertinentes sont :

- la LSDB annonce-t-elle des coûts réellement égaux ?
- la RIB retient-elle tous les chemins possibles ?
- la FIB a-t-elle installé chaque prochain saut ?
- les membres ECMP sont-ils tous physiquement sains ?
- la distribution observée est-elle mesurée par flux, paquets ou débit ?

Ne cherchez pas une distribution parfaite en modifiant les métriques si le but est de répartir les gros flux : cela peut provoquer une asymétrie durable ou supprimer des chemins de secours. Le problème relève parfois du hachage, de la capacité ou de l'architecture de trafic, pas du calcul SPF.

### 4.4 TE et attributs de liens

Les extensions de trafic peuvent transporter des informations supplémentaires sur les liens, telles que des bandes passantes, des groupes administratifs ou d'autres attributs de topologie. Elles permettent à des calculs ou contrôleurs de trafic de considérer davantage que la métrique SPF classique. Ces informations ne font toutefois pas, à elles seules, réserver de la bande passante ni imposer un chemin aux paquets.

La distinction à garder :

- **IS-IS annonce l'état et les attributs** ;
- **le calcul de chemin** décide quel itinéraire répond aux contraintes ;
- **le plan de transfert ou le mécanisme TE** doit ensuite acheminer le trafic le long de cet itinéraire ;
- **la surveillance** confirme que la bande passante, la latence et les contraintes restent satisfaites.


## 5. Route leaking : précision, contrôle et risque de boucle

### 5.1 Le leaking est une décision d'architecture

Le *route leaking* distribue des préfixes entre niveaux, au-delà des informations résumées ou des routes par défaut traditionnellement employées. Le mécanisme peut améliorer le choix de sortie ou réduire des détours, mais augmente les informations visibles, les dépendances et la complexité de la convergence.

Ne faites pas de leaking pour compenser une métrique mal conçue. Commencez par clarifier le symptôme : mauvais point de sortie, détour inter-aire, absence de préfixe précis ou besoin d'isoler certains services. Ensuite, ne diffusez que les routes nécessaires au besoin identifié.

### 5.2 Prévenir boucles et chemins sous-optimaux

Un routeur L1/L2 peut connaître un préfixe par L1 et l'annoncer vers L2, ou recevoir en L2 un préfixe puis le redistribuer dans une aire. Sans contrôles, les informations peuvent revenir par une autre frontière, être préférées de façon inattendue ou entretenir un chemin sous-optimal. Les extensions de distribution de préfixes entre niveaux définissent des contraintes et des attributs, notamment l'indicateur *up/down* utilisé avec les annonces de préfixes étendus.

Une politique de leaking robuste doit documenter :

- les préfixes autorisés et leur propriétaire d'origine ;
- la direction du leaking (L1 vers L2, L2 vers L1) ;
- les attributs ou marquages nécessaires ;
- les filtres qui évitent de réannoncer une route apprise par la même politique ;
- la préférence et les coûts attendus ;
- les tests lors de la panne d'un routeur frontière.

L'indicateur *up/down* est une composante du mécanisme de routage inter-niveaux ; ce n'est pas un substitut à une politique réfléchie. Les détails et les commandes de leaking diffèrent entre constructeurs. La sécurité contre les boucles doit être vérifiée selon le comportement réel de l'implémentation, et pas seulement par la présence d'une commande portant le mot `leak`.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 365" role="img" aria-labelledby="isis-exp-leak-title isis-exp-leak-desc">
  <title id="isis-exp-leak-title">Distribution contrôlée d'un préfixe entre niveaux</title>
  <desc id="isis-exp-leak-desc">Un préfixe d'origine est annoncé dans le niveau d'origine, puis propagé vers un autre niveau sous politique explicite et avec les indicateurs nécessaires. Une annonce de retour non contrôlée est signalée comme risque.</desc>
  <defs><marker id="isis-exp-leak-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3 z" fill="#93a4b8"/></marker></defs>
  <rect width="960" height="365" rx="18" fill="#0b1220"/><text x="480" y="32" fill="#f8fafc" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700">Leaking contrôlé plutôt qu'une redistribution implicite</text>
  <rect x="35" y="72" width="360" height="210" rx="13" fill="#10243a" stroke="#60a5fa" stroke-dasharray="7 5"/><text x="215" y="98" fill="#93c5fd" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700">Niveau L1 — aire A</text>
  <rect x="565" y="72" width="360" height="210" rx="13" fill="#17332b" stroke="#34d399" stroke-dasharray="7 5"/><text x="745" y="98" fill="#6ee7b7" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700">Niveau L2 — ossature</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="72" y="133" width="125" height="62" rx="9" fill="#1e3a5f" stroke="#60a5fa"/><text x="134" y="157" fill="#dbeafe" font-size="14" font-weight="700">Préfixe</text><text x="134" y="176" fill="#dbeafe" font-size="12">10.10.0.0/16</text>
    <rect x="254" y="133" width="106" height="62" rx="9" fill="#24425e" stroke="#60a5fa"/><text x="307" y="157" fill="#dbeafe" font-size="13" font-weight="700">Frontière</text><text x="307" y="176" fill="#bfdbfe" font-size="11">L1/L2</text>
    <rect x="618" y="133" width="254" height="62" rx="9" fill="#17483c" stroke="#34d399"/><text x="745" y="157" fill="#d1fae5" font-size="14" font-weight="700">Annonce L2 selon politique</text><text x="745" y="176" fill="#a7f3d0" font-size="12">Préfixe + attributs appropriés</text>
    <path d="M197 164 H248" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#isis-exp-leak-arrow)"/><path d="M360 164 H612" stroke="#34d399" stroke-width="2.5" marker-end="url(#isis-exp-leak-arrow)"/>
    <path d="M745 195 V231 H307 V197" stroke="#f87171" stroke-width="2.5" stroke-dasharray="7 5" fill="none" marker-end="url(#isis-exp-leak-arrow)"/><text x="527" y="249" fill="#fca5a5" font-size="12" font-weight="700">Annonce de retour à filtrer / contrôler</text>
    <rect x="130" y="302" width="700" height="36" rx="8" fill="#2d2229" stroke="#fb7185"/><text x="480" y="324" fill="#fecdd3" font-size="13">Valider l'origine, le sens, les attributs up/down et les règles anti-boucle.</text>
  </g>
</svg>

### 5.3 Route par défaut ou préfixes spécifiques ?

Une route par défaut réduit le nombre de préfixes qu'un routeur L1 doit traiter, mais tous les trafics non locaux peuvent être envoyés vers une frontière identique ou vers la frontière jugée la meilleure par la politique. Des routes spécifiques peuvent rapprocher le choix de sortie du préfixe destinataire, mais augmentent la quantité de données de routage et les changements à gérer.

Décidez selon :

- nombre de préfixes et fréquence des changements ;
- taille et capacité des routeurs d'accès ;
- coût inter-aire ;
- besoin de sortie différente pour certains services ;
- capacité à tester les pannes de frontières ;
- exigences de stabilité et de simplicité opérationnelle.

### 5.4 Checklist de validation du leaking

Pour chaque préfixe qui doit être fuité :

1. confirmer l'origine et le niveau où il est appris ;
2. vérifier le LSP source et le niveau de destination ;
3. lire la route installée avant et après la politique ;
4. tracer le chemin vers le préfixe depuis au moins deux routeurs représentatifs ;
5. couper une frontière et confirmer que le chemin de secours ne revient pas vers la source du leaking ;
6. rétablir la liaison et vérifier qu'aucune annonce obsolète ne persiste ;
7. documenter le résultat attendu et les commandes d'observation.


## 6. IPv6 et Multi-Topology : choisir le modèle correctement

### 6.1 IPv6 sur IS-IS

IS-IS peut transporter des informations de routage IPv6 au moyen d'extensions spécifiques. Il faut distinguer la formation de l'adjacency IS-IS du transport des préfixes IPv6 : une adjacency peut exister alors que l'annonce IPv6, son niveau ou son installation dans la RIBv6 est incorrecte.

Contrôles pour un service IPv6 :

- l'activation IS-IS pour IPv6 sur la plateforme ;
- l'adresse IPv6 et le préfixe sur l'interface ;
- la prise en charge et la cohérence des TLV IPv6 dans les LSP ;
- la famille d'adresses, le niveau et les politiques ;
- la route IPv6 active et la résolution du prochain saut ;
- le chemin retour et les filtres ICMPv6/ND.

L'absence d'une route IPv6 ne se corrige pas nécessairement en redémarrant l'adjacency. Commencez par vérifier si le préfixe apparaît dans la LSDB et dans la famille de routage adéquate.

### 6.2 Single topology et Multi-Topology

Dans un modèle de topologie unique (*single topology*), les informations IPv4 et IPv6 s'appuient sur une représentation commune de la connectivité selon les règles de l'implémentation. Si les deux familles ne disposent pas de la même connectivité ou si elles doivent utiliser des ensembles de liens différents, il faut vérifier les limites du modèle choisi.

**Multi-Topology IS-IS (MT-ISIS)** permet d'annoncer et calculer des topologies logiques distinctes. Cette approche peut servir, par exemple, lorsque la connectivité IPv6 n'est pas identique à celle d'IPv4 ou que plusieurs topologies ont des périmètres de liens différents. Elle augmente toutefois la complexité : interfaces membres, RIB/FIB séparées, cohérence des topologies, disponibilité des extensions et prise en charge de tous les routeurs doivent être contrôlées.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 355" role="img" aria-labelledby="isis-exp-mt-title isis-exp-mt-desc">
  <title id="isis-exp-mt-title">Topologie unique versus Multi-Topology</title>
  <desc id="isis-exp-mt-desc">À gauche, IPv4 et IPv6 partagent la même topologie logique. À droite, deux topologies distinctes peuvent sélectionner des liens différents, si les routeurs le prennent en charge et si la configuration est cohérente.</desc>
  <rect width="960" height="355" rx="18" fill="#0b1220"/><text x="480" y="32" fill="#f8fafc" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700">Choisir le modèle en fonction de la connectivité réelle</text>
  <rect x="34" y="64" width="425" height="242" rx="13" fill="#12263b" stroke="#60a5fa"/><text x="246" y="91" fill="#93c5fd" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700">Topologie unique</text>
  <rect x="501" y="64" width="425" height="242" rx="13" fill="#182c26" stroke="#34d399"/><text x="713" y="91" fill="#6ee7b7" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700">Multi-Topology</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <g fill="#1e3a5f" stroke="#60a5fa"><circle cx="116" cy="161" r="22"/><circle cx="246" cy="132" r="22"/><circle cx="372" cy="161" r="22"/><circle cx="246" cy="233" r="22"/></g>
    <g stroke="#93c5fd" stroke-width="2.5"><path d="M138 156 L224 137 M268 137 L350 156 M130 181 L229 219 M263 211 L358 177 M246 154 V211" fill="none"/></g>
    <text x="116" y="166" fill="#dbeafe" font-size="11">R1</text><text x="246" y="137" fill="#dbeafe" font-size="11">R2</text><text x="372" y="166" fill="#dbeafe" font-size="11">R3</text><text x="246" y="238" fill="#dbeafe" font-size="11">R4</text>
    <text x="246" y="278" fill="#cbd5e1" font-size="13">Une représentation commune des liens</text>
    <g fill="#17483c" stroke="#34d399"><circle cx="582" cy="161" r="22"/><circle cx="713" cy="132" r="22"/><circle cx="844" cy="161" r="22"/><circle cx="713" cy="233" r="22"/></g>
    <path d="M604 156 L691 137 M735 137 L822 156 M735 211 L824 177" stroke="#6ee7b7" stroke-width="3" fill="none"/>
    <path d="M604 181 L695 220 M691 154 V211" stroke="#67e8f9" stroke-width="3" stroke-dasharray="7 4" fill="none"/>
    <text x="582" y="166" fill="#d1fae5" font-size="11">R1</text><text x="713" y="137" fill="#d1fae5" font-size="11">R2</text><text x="844" y="166" fill="#d1fae5" font-size="11">R3</text><text x="713" y="238" fill="#d1fae5" font-size="11">R4</text>
    <text x="713" y="278" fill="#d1fae5" font-size="13">Deux graphes logiques avec liens différents</text>
    <text x="480" y="330" fill="#94a3b8" font-size="12">MT-ISIS exige une prise en charge cohérente ; ne pas l'activer sans plan d'adressage et de RIB/FIB.</text>
  </g>
</svg>

### 6.3 Migration IPv4/IPv6 : réduire les inconnues

Pour une migration, évitez d'activer en une fois IPv6, MT-ISIS, nouvelles métriques et nouvelles politiques de leaking. Changez un axe à la fois : d'abord annoncer et vérifier les préfixes IPv6, ensuite assurer le service et le retour, puis seulement introduire une topologie distincte si une exigence le justifie.

Conservez des preuves avant/après : sortie d'adjacency, LSP, route IPv6, prochain saut, FIB et tests de trafic. Une table de routes seule ne valide ni la MTU ni la résolution ND, et un ping local ne valide pas l'accessibilité inter-aire.


## 7. Sécurité du plan de contrôle et authentification

### 7.1 Ce que protège l'authentification

IS-IS utilise des informations d'authentification dans les PDU conformément aux mécanismes supportés par l'équipement. Les mécanismes historiques en clair et les méthodes cryptographiques ne fournissent pas le même niveau de protection. Les mécanismes cryptographiques documentés par les RFC doivent être examinés avec les mises à jour, recommandations de l'éditeur et capacités de la version logicielle. Ne considérez pas tous les algorithmes historiquement définis comme équivalents ou préférables.

L'authentification aide à réduire le risque d'acceptation de PDU non autorisées, mais elle n'empêche pas la compromission d'un routeur légitime, une mauvaise configuration, un déni de service sur le lien ou toutes les formes d'attaque de contrôle. Elle doit faire partie d'une défense en profondeur.

### 7.2 Niveau de portée de la clé

Selon la plateforme, une authentification peut s'appliquer à un niveau, à des types précis de PDU, à une interface ou à une combinaison de ces portées. Il faut faire correspondre les réglages : une configuration appliquée à la LSDB peut ne pas être identique à celle nécessaire aux IIH. Une adjacency qui échoue après une modification d'authentification demande de vérifier les compteurs et logs de rejet, puis la portée effective sur chaque extrémité.

### 7.3 Rotation et changement de clé

Une rotation sûre des clés suit un plan coordonné :

1. vérifier les algorithmes et modes supportés des deux côtés ;
2. déterminer si une période avec plusieurs clés ou un mécanisme de transition est disponible ;
3. préparer les secrets dans un canal de gestion sécurisé ;
4. déployer d'abord la capacité nécessaire, puis basculer la clé selon le plan du constructeur ;
5. confirmer l'état des adjacencies et l'acceptation des PDU avant de retirer l'ancienne clé ;
6. enregistrer les preuves et la date de retrait de l'ancien secret.

Ne copiez pas des clés de production dans des captures, des scripts partagés ou des dépôts Git. Dans les exemples de laboratoire, utilisez des valeurs fictives.

### 7.4 Sécuriser le périmètre opérationnel

- restreindre l'accès d'administration et employer des identifiants individuels ;
- protéger les ports inutilisés et éviter de relier un segment non contrôlé à une interface IS-IS active ;
- surveiller les changements inattendus de voisins, de System ID, de LSP ou de métriques ;
- configurer l'authentification et les mécanismes de contrôle compatibles sur l'ensemble du périmètre ;
- journaliser les événements tout en synchronisant les horloges ;
- sauvegarder les configurations et préparer un retour arrière ;
- tester l'interopérabilité des fonctions cryptographiques avant une mise à niveau.

L'authentification des PDU ne remplace pas les restrictions de gestion, la segmentation, les contrôles de couche 2 ni une surveillance de l'état de routage.


## 8. Extensions modernes : Segment Routing et Flex-Algorithm

### 8.1 Rôle d'IS-IS dans Segment Routing

Dans une architecture Segment Routing, IS-IS peut distribuer des informations de capacité et des identifiants associés aux chemins (par exemple des Prefix-SID ou des informations de nœud, selon la famille et le mode SR). IS-IS demeure un protocole de diffusion d'informations ; la seule présence d'une annonce de capacité ne garantit pas que tous les routeurs de transit, les interfaces et le plan de transfert sont prêts à utiliser les segments.

Avant le déploiement, vérifiez :

- le support SR exact (SR-MPLS, SRv6 ou sous-ensemble supporté) ;
- la plage de labels ou d'identifiants, leur unicité et leur portée ;
- les capacités annoncées dans les LSP et leur réception sur les routeurs concernés ;
- la programmation du plan de transfert et la disponibilité de la fonction sur les cartes ;
- les chemins de secours et le comportement lors du retrait d'une capacité ;
- l'interopérabilité des versions et les procédures de restauration.

Le protocole de routage peut annoncer le chemin théorique, mais une panne de label, de SID ou de programmation ne sera pas nécessairement visible comme une absence d'adjacency IS-IS.

### 8.2 Flex-Algorithm : plusieurs calculs selon une définition commune

L'algorithme SPF classique choisit principalement les chemins selon la métrique IGP. **Flex-Algorithm** permet de définir des calculs de chemin alternatifs selon un type de calcul, un type de métrique et un ensemble de contraintes (par exemple exclure des liens identifiés par un groupe administratif). Des routeurs participants annoncent et utilisent une définition commune de l'algorithme.

L'identifiant de Flex-Algorithm, dans le cadre standard défini par RFC 9350, se situe dans la plage 128–255. La définition doit être cohérente pour les routeurs qui participent au même calcul : si deux nœuds donnent une signification différente au même identifiant, ils ne calculent pas la même topologie logique et le transfert peut devenir incorrect. Les mises à jour de la spécification et les options prises en charge doivent être vérifiées dans la documentation et les registres actuels.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 365" role="img" aria-labelledby="isis-exp-flex-title isis-exp-flex-desc">
  <title id="isis-exp-flex-title">Deux calculs sur une même topologie physique</title>
  <desc id="isis-exp-flex-desc">Une topologie physique offre plusieurs chemins. SPF classique sélectionne le coût métrique le plus faible, tandis qu'un Flex-Algorithm peut exclure certains liens via des contraintes partagées, si tous les routeurs participants appliquent la même définition.</desc>
  <rect width="960" height="365" rx="18" fill="#0b1220"/><text x="480" y="32" fill="#f8fafc" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700">Flex-Algorithm : une définition, un calcul cohérent</text>
  <rect x="40" y="65" width="880" height="182" rx="13" fill="#111e30" stroke="#475569"/>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <circle cx="145" cy="154" r="27" fill="#1e3a5f" stroke="#60a5fa"/><text x="145" y="159" fill="#dbeafe" font-size="13" font-weight="700">S</text>
    <circle cx="365" cy="103" r="27" fill="#17372e" stroke="#34d399"/><text x="365" y="108" fill="#d1fae5" font-size="13" font-weight="700">A</text>
    <circle cx="365" cy="205" r="27" fill="#3c2920" stroke="#fb923c"/><text x="365" y="210" fill="#ffedd5" font-size="13" font-weight="700">B</text>
    <circle cx="600" cy="103" r="27" fill="#17372e" stroke="#34d399"/><text x="600" y="108" fill="#d1fae5" font-size="13" font-weight="700">C</text>
    <circle cx="600" cy="205" r="27" fill="#17372e" stroke="#34d399"/><text x="600" y="210" fill="#d1fae5" font-size="13" font-weight="700">D</text>
    <circle cx="815" cy="154" r="27" fill="#1e3a5f" stroke="#60a5fa"/><text x="815" y="159" fill="#dbeafe" font-size="13" font-weight="700">T</text>
    <path d="M171 148 L339 109 M392 103 H573 M627 109 L789 148" stroke="#34d399" stroke-width="3" fill="none"/>
    <path d="M171 160 L339 199 M392 205 H573 M627 199 L789 160" stroke="#fb923c" stroke-width="3" stroke-dasharray="7 5" fill="none"/>
    <text x="260" y="114" fill="#6ee7b7" font-size="11">métrique 5</text><text x="482" y="91" fill="#6ee7b7" font-size="11">groupe vert</text><text x="705" y="114" fill="#6ee7b7" font-size="11">métrique 5</text>
    <text x="260" y="204" fill="#fdba74" font-size="11">métrique 8</text><text x="482" y="230" fill="#fdba74" font-size="11">lien exclu dans l'exemple</text><text x="705" y="204" fill="#fdba74" font-size="11">métrique 8</text>
    <rect x="90" y="270" width="350" height="62" rx="10" fill="#163a33" stroke="#34d399"/><text x="265" y="294" fill="#a7f3d0" font-size="14" font-weight="700">SPF classique</text><text x="265" y="314" fill="#d1fae5" font-size="12">Choix selon la métrique IGP</text>
    <rect x="520" y="270" width="350" height="62" rx="10" fill="#3a2b20" stroke="#fb923c"/><text x="695" y="294" fill="#fed7aa" font-size="14" font-weight="700">Flex-Algorithm</text><text x="695" y="314" fill="#ffedd5" font-size="12">Calcul selon contraintes partagées</text>
    <text x="480" y="351" fill="#94a3b8" font-size="11">Schéma conceptuel : la sélection exacte dépend de la définition annoncée et des liens admissibles.</text>
  </g>
</svg>

### 8.3 Déploiement progressif d'un Flex-Algorithm

1. définir l'objectif mesurable : éviter certains liens, choisir une métrique alternative ou utiliser une topologie contrainte ;
2. identifier les routeurs, les liens et les familles d'adresses participants ;
3. définir un identifiant, un type de métrique, un type de calcul et les contraintes exactes ;
4. confirmer que tous les routeurs participants supportent le même modèle et annoncent la définition attendue ;
5. vérifier les informations de capacité et de participation dans la LSDB ;
6. contrôler les routes calculées et les prochains sauts propres à l'algorithme ;
7. vérifier le transfert réel avec des outils adaptés au plan SR ;
8. tester la perte d'un lien admissible et d'un lien non admissible ;
9. préparer le retrait de l'algorithme et l'effet sur les flux qui l'utilisent.

Ne déduisez pas la réussite de Flex-Algorithm à partir du seul fait que les adjacencies standard sont Up. Les voisins peuvent être opérationnels tout en ayant une définition ou une capacité Flex-Algorithm absente, incompatible ou inutilisable par la FIB.

### 8.4 Notions TE à ne pas confondre

- **Métrique IGP classique** : base du calcul SPF standard.
- **Attributs TE** : informations distribuées pouvant être consommées par un calculateur ou une fonction TE.
- **Flex-Algorithm** : définition commune d'un calcul alternatif au sein d'un IGP, avec des contraintes annoncées.
- **Segment Routing** : mécanisme de transfert qui permet de représenter ou d'imposer certains chemins au travers de segments.

Ces éléments peuvent se combiner, mais ne sont pas synonymes. Le design doit préciser quel composant calcule le chemin et lequel le programme dans le plan de transfert.


## 9. Interopérabilité et TLV : raisonner au niveau des données annoncées

### 9.1 Pourquoi un voisin peut accepter un LSP sans utiliser toutes ses informations

IS-IS a été conçu pour évoluer avec des TLV et sous-TLV. Un routeur peut recevoir un LSP contenant une extension qu'il ne comprend pas et ignorer l'information concernée tout en conservant la validité du PDU, selon les règles applicables. Ainsi, l'acceptation du LSP n'implique pas que chaque attribut ou fonction est utilisé sur tous les routeurs.

C'est un point crucial lors de l'ajout d'attributs TE, IPv6, Multi-Topology, Segment Routing ou Flex-Algorithm. Vérifiez non seulement que le LSP est visible, mais aussi que l'équipement reconnaît, expose et exploite le TLV ou la sous-structure nécessaire.

### 9.2 Cas d'un LSP divergent ou partiellement interprété

Une incompatibilité peut se manifester à plusieurs niveaux :

- l'émetteur n'annonce pas l'information souhaitée ;
- l'information est annoncée dans le mauvais niveau ou mauvais fragment ;
- le récepteur ne prend pas en charge le TLV ou la variante ;
- le TLV est reçu mais l'interface, la famille d'adresses ou la capacité de transfert ne l'utilise pas ;
- la RIB choisit un autre chemin, même si l'attribut est visible ;
- une différence de versions entraîne un comportement divergent ou un défaut de traitement.

Capturez ou inspectez la LSDB depuis plusieurs routeurs. Une seule sortie peut être trompeuse : la LSDB locale de l'émetteur confirme son annonce, mais ne prouve pas qu'elle a été propagée ou interprétée comme attendu chez les récepteurs.

### 9.3 TLV invalides et robustesse

La spécification RFC 8918 clarifie des règles de traitement des TLV invalides ou non autorisés selon le type de PDU. Le principe général d'extensibilité est que des TLV inconnus doivent être traités selon les règles prévues, et que l'erreur dans un TLV ne doit pas entraîner arbitrairement le rejet complet d'un LSP valide lorsque les spécifications imposent de conserver le PDU. Des versions qui gèrent ces cas différemment peuvent créer des difficultés d'interopérabilité.

En cas de suspicion :

1. noter le type de PDU et la provenance ;
2. identifier le TLV ou sous-TLV qui pose problème ;
3. comparer le comportement aux RFC et aux notes de version ;
4. vérifier la LSDB après réception sur des routeurs distincts ;
5. éviter les changements massifs avant d'avoir reproduit le défaut en laboratoire ;
6. collecter les journaux, versions et captures utiles pour l'escalade éditeur.

### 9.4 Politique d'interopérabilité

Maintenez une matrice qui associe chaque plateforme à sa version, sa famille IP, les extensions utilisées et les limites connues. Lors d'une mise à jour, testez au minimum : adjacency L1/L2, échange et purge LSP, IPv4/IPv6, auth, wide metrics, ECMP, BFD, MTU, et chaque extension réellement activée. Les fonctions simplement disponibles dans le CLI mais non utilisées dans le domaine ne nécessitent pas toutes le même niveau de test ; les fonctions qui changent le chemin de trafic, elles, doivent être traitées comme critiques.


## 10. Méthode experte de dépannage

### 10.1 Formuler des hypothèses mesurables

Un bon diagnostic ne commence pas par changer tous les paramètres. Il commence par un énoncé que l'on peut confirmer ou réfuter : « le préfixe est absent parce qu'il n'est pas dans le LSP L2 », ou « la route existe mais le prochain saut de la FIB ne répond pas ». Chaque hypothèse devrait avoir une commande ou une observation qui permette de la tester.

### 10.2 Ordre d'investigation

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" role="img" aria-labelledby="isis-exp-diag-title isis-exp-diag-desc">
  <title id="isis-exp-diag-title">Arbre de diagnostic de routage IS-IS</title>
  <desc id="isis-exp-diag-desc">Le dépannage commence par la portée de la panne, puis suit interface, adjacency, LSDB, calcul de route, FIB et service applicatif.</desc>
  <defs><marker id="isis-exp-diag-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3 z" fill="#93a4b8"/></marker></defs>
  <rect width="960" height="390" rx="18" fill="#0b1220"/><text x="480" y="32" fill="#f8fafc" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700">Diagnostic : remonter du symptôme à la couche fautive</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="300" y="54" width="360" height="43" rx="9" fill="#202b3c" stroke="#94a3b8"/><text x="480" y="81" fill="#e2e8f0" font-size="14" font-weight="700">1. Quelle portée ? Un lien, une aire, tout le domaine ?</text>
    <path d="M480 97 V114" stroke="#93a4b8" stroke-width="2" marker-end="url(#isis-exp-diag-arrow)"/>
    <rect x="300" y="119" width="360" height="43" rx="9" fill="#3a2528" stroke="#f87171"/><text x="480" y="146" fill="#fecaca" font-size="14" font-weight="700">2. Interface et adjacencies</text>
    <path d="M480 162 V179" stroke="#93a4b8" stroke-width="2" marker-end="url(#isis-exp-diag-arrow)"/>
    <rect x="300" y="184" width="360" height="43" rx="9" fill="#172d42" stroke="#60a5fa"/><text x="480" y="211" fill="#dbeafe" font-size="14" font-weight="700">3. LSP / niveau / fragments / fraîcheur</text>
    <path d="M480 227 V244" stroke="#93a4b8" stroke-width="2" marker-end="url(#isis-exp-diag-arrow)"/>
    <rect x="300" y="249" width="360" height="43" rx="9" fill="#173329" stroke="#34d399"/><text x="480" y="276" fill="#d1fae5" font-size="14" font-weight="700">4. SPF / route active / ECMP / politiques</text>
    <path d="M480 292 V309" stroke="#93a4b8" stroke-width="2" marker-end="url(#isis-exp-diag-arrow)"/>
    <rect x="300" y="314" width="360" height="43" rx="9" fill="#352b1b" stroke="#fbbf24"/><text x="480" y="341" fill="#fef3c7" font-size="14" font-weight="700">5. FIB / ARP-ND / MTU / ACL / trajet retour</text>
    <text x="100" y="143" fill="#fca5a5" font-size="12">Voisin absent</text><text x="100" y="159" fill="#94a3b8" font-size="11">Liaison / auth / niveaux</text>
    <text x="750" y="207" fill="#93c5fd" font-size="12">Préfixe absent</text><text x="750" y="223" fill="#94a3b8" font-size="11">Annonce / flooding / niveau</text>
    <text x="750" y="276" fill="#86efac" font-size="12">Route non retenue</text><text x="750" y="292" fill="#94a3b8" font-size="11">Métrique / préférence</text>
  </g>
</svg>

### 10.3 Commandes d'observation de type Cisco

Les commandes ci-dessous sont des exemples usuels, à adapter à la version et au modèle. Les variantes exactes peuvent différer.

```text
show isis neighbors
show isis neighbors detail
show isis database
show isis database detail
show isis topology
show isis route
show ip route isis
show ipv6 route isis
show interfaces
show logging
show bfd neighbors details
```

Pour une investigation spécifique, complétez avec les commandes de la plateforme pour examiner la FIB, les adjacences de transfert, les compteurs de drops et les détails Segment Routing/Flex-Algorithm. Certains systèmes emploient une forme `show isis ...`, d'autres une forme différente ou un mode propre au constructeur.

### 10.4 Tableau symptôme → hypothèse → preuve

| Symptôme | Hypothèse à tester | Preuve à rechercher | Action prudente |
|---|---|---|---|
| Voisin absent | Interface, niveaux, aire ou authentification incompatibles | État interface, Hello, logs, paramètres des deux côtés | Corriger un seul paramètre puis observer |
| Adjacency Up, route absente | Préfixe non annoncé ou mauvais niveau | LSP complet, niveau, TLV de préfixe | Corriger l'annonce ou la politique |
| Route dans LSDB, pas dans RIB | Route concurrente, politique ou famille mal configurée | RIB complète, préférence, table IPv6 le cas échéant | Ajuster la politique après confirmation |
| Route présente, trafic en échec | FIB, voisin L2, MTU, ACL ou retour | FIB, ARP/ND, compteur drop, trace aller/retour | Isoler le prochain saut fautif |
| Flaps répétés | Perte physique, timers agressifs ou charge | Logs horodatés, compteurs d'erreurs, BFD/IIH | Stabiliser la cause, ne pas seulement rallonger les timers |
| Chemin sous-optimal | Métriques ou frontière inter-aire incorrectes | Coûts complets, ATT/default, leaking | Refaire le calcul sur papier puis laboratoire |
| Extension visible mais inutilisée | Fonction non supportée ou plan de transfert non prêt | Détails TLV, capacité, route calculée, FIB | Valider la chaîne complète de la fonction |

### 10.5 Capturer le bon événement

Une capture utile devrait être liée à un événement clairement horodaté : déconnexion du lien, expiration du voisinage, nouvelle séquence LSP, changement de prochain saut dans la RIB/FIB puis premier paquet réussi. Sans synchronisation de l'horloge, les timestamps issus de plusieurs routeurs peuvent donner un ordre faux.

Pour une comparaison multi-routeurs, collectez les données suivantes avant et après :

- heure et description de la panne ;
- état interface/voisin ;
- ID de LSP et séquence du routeur concerné ;
- LSDB de deux points distincts ;
- route active, coût et prochain saut ;
- FIB/adjacence de transfert ;
- test de trafic et chemin retour ;
- CPU, mémoire, erreurs physiques et journaux.


## 11. Laboratoire expert : maintenance, Overload et validation de convergence

### 11.1 Objectif

Mettre en place une petite topologie L2 redondante afin de simuler une maintenance contrôlée, d'observer l'effet du bit Overload et de mesurer la convergence. Le laboratoire est volontairement centré sur des comportements que l'on peut observer sans activer en même temps toutes les extensions avancées.

### 11.2 Topologie

```text
          10.0.12.0/30
      R1 ------------- R2
       |                 |
       |                 | 10.0.24.0/30
       |                 |
       |               R4 ---- LAN test 192.0.2.0/24
       |                 |
       |                 |
       +------ R3 -------+
         liens de secours
```

Plan d'adressage indicatif :

| Lien | R1 | R2/R3/R4 |
|---|---|---|
| R1–R2 | 10.0.12.1/30 | R2 : 10.0.12.2/30 |
| R1–R3 | 10.0.13.1/30 | R3 : 10.0.13.2/30 |
| R2–R4 | 10.0.24.1/30 | R4 : 10.0.24.2/30 |
| R3–R4 | 10.0.34.1/30 | R4 : 10.0.34.2/30 |
| LAN de test | — | R4 : 192.0.2.1/24 |

Les adresses et les noms sont fictifs. Adaptez-les aux interfaces réellement disponibles dans votre simulateur. Le bloc `192.0.2.0/24` est réservé à la documentation et sert ici de préfixe de laboratoire ; ne l'utilisez pas comme adresse publique sur Internet.

### 11.3 Configuration de base illustrative

Exemple de style Cisco IOS/IOS XE pour R1. Configurez les interfaces de la même façon sur les autres routeurs avec leur System ID/NET et leurs adresses appropriées.

```text
router isis CORE
 net 49.0001.0000.0000.0001.00
 is-type level-2-only
 metric-style wide
!
interface GigabitEthernet0/0
 description Vers-R2
 ip address 10.0.12.1 255.255.255.252
 ip router isis CORE
 isis circuit-type level-2-only
!
interface GigabitEthernet0/1
 description Vers-R3
 ip address 10.0.13.1 255.255.255.252
 ip router isis CORE
 isis circuit-type level-2-only
```

**Important :** les noms d'interface, les commandes d'activation IS-IS sur l'interface, la configuration NET et les commandes de métrique peuvent différer. Utilisez un NET unique par routeur, vérifiez que les interfaces sont bien dans le domaine et validez la syntaxe disponible avec l'aide du CLI. Ne copiez pas le NET de R1 sur les autres routeurs.

Sur R4, annoncez le préfixe de test selon la méthode prise en charge par votre plateforme : activer IS-IS sur l'interface LAN si cela est souhaité, ou utiliser une annonce adaptée au design du laboratoire. Dans un réseau réel, une interface de LAN utilisateur ne doit pas devenir un segment IS-IS de voisinage sans décision explicite. Lorsque le constructeur fournit un mode passif, utilisez-le pour annoncer le préfixe sans former d'adjacencies sur cette interface.

### 11.4 Vérification initiale

Avant la première expérience :

1. confirmer que chaque lien est `up/up` ;
2. vérifier toutes les adjacencies L2 prévues ;
3. inspecter la LSDB et les LSP des quatre routeurs ;
4. confirmer que `192.0.2.0/24` apparaît dans le bon niveau ;
5. vérifier les routes et les prochains sauts depuis R1, R2 et R3 ;
6. lancer un ping et une trace vers la cible de test ;
7. noter la topologie de départ et le coût de chaque chemin.

Si le préfixe du LAN n'est pas présent dans la LSDB, ne passez pas à la partie Overload. Corrigez d'abord l'annonce du préfixe et la topologie de base.

### 11.5 Expérience A — augmenter un coût

1. relever les métriques des liens R1–R2 et R1–R3 ;
2. augmenter temporairement une métrique de lien dans le sens et la portée prévus par votre implémentation ;
3. observer le LSP actualisé, la séquence et les routes sur les autres routeurs ;
4. confirmer que le chemin change uniquement si le coût total devient préférable via l'autre route ;
5. revenir à la valeur de départ et contrôler la convergence inverse.

Selon la plateforme, la métrique de lien est annoncée par l'extrémité et peut nécessiter une configuration sur un seul côté ou sur les deux côtés pour établir une politique symétrique. Ne présumez pas qu'un changement local change automatiquement le coût dans les deux directions.

### 11.6 Expérience B — Overload pendant la maintenance

1. sauvegarder les sorties de la LSDB et des routes ;
2. activer le bit Overload sur R2 selon la commande documentée par la plateforme ;
3. vérifier que le bit est visible dans le LSP pertinent ;
4. attendre que les routeurs distants recalculent leur chemin ;
5. contrôler qu'un transit alternatif est utilisé si la topologie et les métriques le permettent ;
6. vérifier que la route vers les préfixes directement connectés à R2 se comporte comme prévu ;
7. réaliser la maintenance simulée sans retirer plus de liens que nécessaire ;
8. retirer Overload après validation et mesurer le retour au chemin normal.

Ne cherchez pas une commande identique sur toutes les plateformes. Certains systèmes configurent Overload avec une commande propre au processus IS-IS ; d'autres proposent une option temporaire ou au démarrage. Le but pédagogique est le comportement observé dans la LSDB et la FIB, non la mémorisation d'une syntaxe isolée.

### 11.7 Expérience C — simuler un défaut de lien

Coupez un lien redondant et horodatez : perte physique, disparition ou changement d'adjacency, changement de LSP, changement de route, programmation de la FIB et succès du trafic. Répétez l'essai sur un lien différent, car tous les défauts n'affectent pas le même ensemble de chemins. Comparez les résultats plutôt que d'évaluer uniquement le premier ping manqué.

### 11.8 Fiche de compte rendu

| Mesure | Avant | Pendant l'événement | Après convergence |
|---|---|---|---|
| Adjacencies |  |  |  |
| LSP modifiés |  |  |  |
| Route active / métrique |  |  |  |
| Prochain saut / FIB |  |  |  |
| Perte de paquets |  |  |  |
| Durée de rétablissement |  |  |  |
| CPU / erreurs physiques |  |  |  |

Le laboratoire est réussi lorsque vous pouvez expliquer pourquoi le chemin a changé, avec des éléments provenant de la LSDB, de la RIB/FIB et du test de trafic.


## 12. Études de cas expertes

### Cas 1 — La LSDB est cohérente, le trafic tombe après le basculement

**Observation :** après une coupure, les tables de routage montrent le nouvel itinéraire, mais plusieurs sessions TCP se bloquent.

**Hypothèses :** un membre ECMP défaillant est encore dans la FIB ; le prochain saut n'est pas résolu ; un pare-feu voit une asymétrie ; le chemin retour n'a pas convergé ; ou les applications attendent une session expirée.

**Démarche :** vérifier d'abord la FIB et les adjacences matérielles. Tester ensuite plusieurs flux et comparer leur hash/chemin. Contrôler séparément aller et retour. Comparer les journaux réseau aux timestamps de convergence et vérifier si le rétablissement du service suit ou non le rétablissement du routage.

**Conclusion attendue :** « la route IS-IS est correcte » ne signifie pas automatiquement « tous les flux fonctionnent ». Le point fautif doit être localisé au niveau du prochain saut, du plan de transfert ou de la politique.

### Cas 2 — Un nouveau TLV est visible sur un routeur, mais pas sur un autre

**Observation :** l'équipement source montre les informations TE ou Flex-Algorithm ; un routeur distant affiche le LSP mais pas l'information utile.

**Hypothèses :** le LSP observé n'est pas le même fragment ou niveau, l'extension est mal propagée, le récepteur ne prend pas en charge le TLV, ou sa sortie CLI ne l'affiche pas.

**Démarche :** confirmer l'ID de LSP, son numéro de séquence, le niveau et le fragment. Inspecter depuis deux points. Vérifier la version logicielle et la documentation des TLV. Enfin confirmer que la fonction est présente dans la LSDB et exploitable par le calcul et le plan de transfert.

**Conclusion attendue :** un LSP accepté peut contenir des TLV que le récepteur ignore. La présence de l'adjacency ne démontre pas la prise en charge de toutes les extensions.

### Cas 3 — Le routeur L1 choisit une sortie d'aire inattendue

**Observation :** deux frontières sont opérationnelles, mais le trafic sort par la frontière qui paraît la plus éloignée.

**Hypothèses :** les coûts L1 vers les sorties sont différents de ce qui a été supposé ; l'attribut ATT et la route par défaut déterminent le comportement ; un leaking introduit une route spécifique ; ou une route concurrente est préférée.

**Démarche :** comparer la RIB et la LSDB L1, les métriques vers les frontières et les routes spécifiques ou par défaut. Calculer le coût total sur papier. Tester les chemins après une coupure, puis ajuster la politique seulement après avoir établi quel mécanisme contrôle le choix.

**Conclusion attendue :** la topologie physique n'indique pas à elle seule la préférence de la route. Il faut suivre les annonces et les coûts utilisés par le calcul réel.

### Cas 4 — L'activation de BFD cause des coupures courtes mais répétées

**Observation :** les adjacencies IS-IS tombent brièvement sous charge depuis l'activation BFD.

**Hypothèses :** délais BFD trop agressifs pour le matériel, sessions traitées dans un contexte chargé, pertes sur le lien, asymétrie ou interaction non prise en charge.

**Démarche :** rapprocher les timestamps des sessions BFD, interfaces, CPU et logs IS-IS. Réduire la complexité du test, utiliser les valeurs recommandées pour la plateforme et reproduire sous charge contrôlée. Ne pas conclure à une panne IS-IS si la session BFD est l'événement déclencheur.

**Conclusion attendue :** une détection plus rapide peut produire un réseau moins stable si les paramètres dépassent les capacités réelles du chemin ou de l'équipement.


## 13. Quiz expert avec corrigé

### Questions

**1.** Pourquoi l'expression « convergence IS-IS = timer Hello » est-elle incorrecte ?

**2.** Que permet le bit Overload et quelles sont deux choses qu'il ne garantit pas ?

**3.** Pourquoi faut-il inspecter tous les fragments LSP d'un routeur ?

**4.** Un préfixe apparaît dans la LSDB L2 mais pas dans la RIB IPv4. Citez trois hypothèses et une preuve pour chacune.

**5.** Pourquoi des métriques cohérentes sont-elles plus importantes qu'une série d'ajustements locaux intuitifs ?

**6.** Quelle différence existe entre les attributs TE, Flex-Algorithm et Segment Routing ?

**7.** Pourquoi la cohérence de définition entre participants est-elle essentielle à Flex-Algorithm ?

**8.** Quelles différences opérationnelles distingueriez-vous entre une route absente et un paquet perdu malgré une route active ?

**9.** Comment pouvez-vous valider un leaking sans vous contenter de voir le préfixe dans la table ?

**10.** Pourquoi l'authentification IS-IS n'est-elle pas une sécurité complète du routage ?

**11.** Un LSP contient un TLV inconnu. Pourquoi ne faut-il pas supposer que tout le LSP sera rejeté ?

**12.** Décrivez une mesure de convergence reproductible de bout en bout.

### Corrigé

**1.** La détection n'est qu'une phase. La génération et le flooding LSP, le calcul SPF, la sélection RIB, la programmation FIB et le rétablissement applicatif contribuent aussi au délai total.

**2.** Overload signale qu'un routeur ne doit pas être préféré comme transit par les calculs compatibles. Il ne coupe pas obligatoirement les adjacencies et ne garantit pas que tous ses préfixes locaux disparaissent ou qu'aucun paquet ne passera par lui dans toutes les conditions.

**3.** Les informations peuvent être réparties entre plusieurs fragments, en particulier quand les extensions augmentent la taille des annonces. Un contrôle du seul LSP de base peut omettre un préfixe ou un attribut.

**4.** Hypothèses : le préfixe n'est pas réellement dans le fragment attendu (preuve : détail LSDB) ; le préfixe est annoncé dans le mauvais niveau ou sous une famille différente (preuve : niveau/TLV) ; une route plus préférée ou une politique empêche l'installation (preuve : RIB détaillée et comparaison des routes candidates).

**5.** Les métriques influencent les chemins complets. Une modification locale peut déplacer du trafic, casser l'équilibrage ou rendre un chemin de secours moins bon. Une politique documentée permet de prévoir les résultats et de tester les pannes.

**6.** Les attributs TE décrivent des propriétés de lien ; Flex-Algorithm définit un calcul IGP alternatif selon des contraintes communes ; Segment Routing fournit des mécanismes de transfert par segments. Ils peuvent fonctionner ensemble mais ne sont pas synonymes.

**7.** Les routeurs doivent calculer la même topologie admissible. Des définitions différentes derrière le même identifiant produiraient des chemins incompatibles et pourraient compromettre le transfert.

**8.** Pour une route absente, inspecter annonce, LSDB, niveau, calcul et RIB. Pour un paquet perdu malgré une route active, examiner la FIB, le prochain saut, ARP/ND, MTU, ACL, ECMP et chemin retour.

**9.** Confirmer le propriétaire du préfixe, la direction du leaking, les informations dans les LSP des deux niveaux, la route et le prochain saut depuis plusieurs points, puis couper une frontière pour vérifier l'absence de boucle et le comportement de secours.

**10.** Elle réduit certains risques d'acceptation de PDU non autorisées, mais ne protège pas d'un routeur légitime compromis, d'une erreur de configuration, de tous les dénis de service ni des défaillances du plan de transfert. Il faut une défense en profondeur.

**11.** IS-IS utilise des TLV extensibles. Les règles de protocole peuvent imposer d'ignorer une TLV inconnue ou invalide sans rejeter un PDU valide. Il faut appliquer la spécification et la version concernées.

**12.** Horodater la panne ; mesurer la détection ; observer l'origine et le flooding des LSP ; relever la route et la FIB ; enfin, enregistrer le premier paquet réussi dans les deux sens. Répéter le même scénario et conserver les sorties avant/après.


## 14. Checklist opérationnelle avant changement en production

### Conception

- [ ] Les rôles L1, L2 et L1/L2 sont documentés.
- [ ] Les dépendances physiques et les risques partagés sont identifiés.
- [ ] Les routes par défaut et les politiques de leaking ont un objectif clair.
- [ ] Les métriques sont cohérentes et les chemins de secours ont été calculés.

### Protocole et interopérabilité

- [ ] Les System ID/NET sont uniques et les niveaux correspondent à l'architecture.
- [ ] Les versions et fonctions supportées sont vérifiées pour tous les équipements concernés.
- [ ] Les LSP et leurs fragments ont été examinés aux deux extrémités et depuis un point distant.
- [ ] Les options IPv6, MT-ISIS, wide metrics, authentification, BFD, SR ou Flex-Algorithm sont testées séparément.

### Convergence et transfert

- [ ] Les phases de convergence sont mesurées avec des horloges synchronisées.
- [ ] Les chemins aller et retour ont été testés.
- [ ] La RIB et la FIB ont été comparées.
- [ ] L'ECMP et les prochains sauts ont été validés.
- [ ] La perte d'un lien et d'une frontière a été simulée.
- [ ] Les effets sur la CPU, les journaux et le contrôle sont acceptables.

### Changement

- [ ] Une sauvegarde et un retour arrière existent.
- [ ] Le changement ne combine pas plusieurs axes de conception inutiles.
- [ ] La commande exacte a été validée sur la version cible.
- [ ] Des critères de succès et d'arrêt sont connus avant l'intervention.
- [ ] Le trafic de production est surveillé après le changement, pas uniquement l'état des voisins.


## 15. Glossaire expert

| Terme | Sens opérationnel |
|---|---|
| ATT / Attached | Attribut utilisé dans l'architecture à deux niveaux pour signaler une connectivité inter-aire via L2. |
| BFD | Mécanisme de détection rapide de défaillance de chemin ou de voisin, pouvant être intégré à IS-IS. |
| CSNP | PDU qui résume les LSP de la base afin d'aider à la synchronisation. |
| ECMP | Utilisation de plusieurs prochains sauts de coût égal. |
| FIB | Base utilisée par le plan de transfert pour envoyer les paquets. |
| Flex-Algorithm | Définition partagée d'un calcul IGP alternatif avec une métrique et des contraintes. |
| Flooding | Propagation des informations LSP dans la portée de niveau appropriée. |
| L1/L2 | Routeur participant aux deux niveaux et assurant une fonction de frontière. |
| LSP | PDU d'état de liens qui porte l'identité, les voisins, les préfixes et des TLV. |
| LSDB | Base des LSP connue pour un niveau et une topologie donnée. |
| MT-ISIS | Extensions IS-IS permettant de maintenir plusieurs topologies logiques. |
| NET | Adresse de couche réseau utilisée pour identifier le système IS-IS et l'aire. |
| OL / Overload | Bit indiquant qu'un routeur ne devrait pas être utilisé comme transit par les calculs qui respectent ce signal. |
| Prefix-SID | Identifiant de segment associé à un préfixe dans certains déploiements Segment Routing. |
| PSNP | PDU partielle employée dans l'échange de numéros de séquence, notamment pour demande ou acquittement ciblé. |
| RIB | Base des routes candidates et sélectionnées par le système de routage. |
| SPF | Calcul du plus court chemin sur le graphe de topologie connu. |
| TLV / sub-TLV | Structure Type-Length-Value et structure imbriquée portant des informations de protocole ou des attributs. |
| Wide metrics | Format de métrique étendue permettant notamment des valeurs plus grandes que les métriques étroites historiques. |


## 16. Références techniques

Les références ci-dessous permettent de retrouver les spécifications et les limites normatives des mécanismes étudiés. Les commandes de constructeur restent à vérifier dans le guide correspondant à la version utilisée.

1. **RFC 1195 — Use of OSI IS-IS for routing in TCP/IP and dual environments** : https://www.rfc-editor.org/rfc/rfc1195
2. **RFC 5302 — Domain-Wide Prefix Distribution with Two-Level IS-IS** : https://www.rfc-editor.org/rfc/rfc5302
3. **RFC 5304 — IS-IS Cryptographic Authentication** : https://www.rfc-editor.org/rfc/rfc5304
4. **RFC 5305 — IS-IS Extensions for Traffic Engineering** : https://www.rfc-editor.org/rfc/rfc5305
5. **RFC 5308 — Routing IPv6 with IS-IS** : https://www.rfc-editor.org/rfc/rfc5308
6. **RFC 5120 — Multi-Topology (MT) Routing in IS-IS** : https://www.rfc-editor.org/rfc/rfc5120
7. **RFC 8918 — Invalid TLV Handling in IS-IS** : https://www.rfc-editor.org/rfc/rfc8918
8. **RFC 9350 — IGP Flexible Algorithm** : https://www.rfc-editor.org/rfc/rfc9350

> **Note de version :** les RFC et l'implémentation évoluent. Pour une mise en œuvre concrète de l'authentification, IPv6, TE, Segment Routing ou Flex-Algorithm, consultez la version courante des spécifications liées ainsi que les notes de version et guides de configuration de votre constructeur. Les schémas de ce cours sont conceptuels et servent à raisonner sur les mécanismes ; ils ne remplacent pas les sorties d'un équipement réel.


## Conclusion

Le niveau expert d'IS-IS consiste moins à mémoriser des commandes qu'à maîtriser la chaîne complète entre topologie physique, annonces LSP, LSDB, calcul de chemin et transfert effectif. Une conception robuste utilise des frontières justifiées, des métriques explicables, une politique de leaking contrôlée et des mécanismes de convergence mesurés. Les extensions comme Multi-Topology, les attributs TE, Segment Routing ou Flex-Algorithm ajoutent des capacités, mais également des conditions de cohérence et d'interopérabilité.

En exploitation, la règle reste la même : **formuler une hypothèse, recueillir la preuve au bon niveau, modifier un paramètre à la fois, puis vérifier le comportement réel du trafic**. C'est cette discipline qui permet de passer d'un réseau simplement opérationnel à un réseau prévisible, résilient et maintenable.
