# OSPF — Niveau Expert : ingénierie, convergence et exploitation à grande échelle

**Durée indicative :** 6 à 10 heures, selon les laboratoires et le matériel disponible.  
**Prérequis :** maîtrise de `ospf-debutant.md` et `ospf-intermediaire.md` : formation des voisinages, LSDB, SPF, aires, ABR/ASBR, types de LSA, stub/NSSA, agrégation, coûts, routes externes et diagnostic multi-aires.  
**Environnement :** maquette IOS/IOS XE ou simulateur pour la configuration ; Wireshark pour les captures ; si disponible, un environnement qui permet d'observer BFD, ECMP, graceful restart et la programmation du forwarding. Certaines fonctions avancées ne sont pas entièrement simulées par Packet Tracer.

Ce cours est la troisième étape de la série. Il ne réexplique pas pas à pas les fondamentaux ni les configurations multi-aires. Le niveau Expert se concentre sur les décisions de conception, les comportements en cas d'incident, les risques de convergence, la sécurité du plan de contrôle, l'intégration avec d'autres protocoles et la preuve de rétablissement. **L'expertise OSPF consiste à pouvoir prévoir un comportement, à le vérifier sur l'équipement réel et à limiter l'impact d'un changement.**

> **Cadre technique :** les exemples sont principalement orientés OSPFv2 sur Cisco IOS/IOS XE. Les commandes, valeurs par défaut et fonctionnalités diffèrent selon le modèle, le matériel de transfert et la version logicielle. Les schémas sont des modèles conceptuels, pas des captures d'un équipement réel. Valider toute commande sur la version cible avant une mise en production.

## Objectifs de niveau Expert

À la fin du cours, tu dois pouvoir :

- concevoir une architecture OSPF dimensionnée en tenant compte de la portée des LSA, de la charge de calcul et de la stabilité des frontières ;
- distinguer détection de panne, convergence OSPF, programmation de la FIB et rétablissement applicatif ;
- analyser ECMP et les possibilités de fast reroute sans confondre chemin candidat et chemin effectivement installé ;
- évaluer BFD et les paramètres de convergence sans créer de faux positifs ;
- expliquer graceful restart, les rôles helper et les conditions dans lesquelles la continuité du forwarding peut être conservée ;
- concevoir une redistribution filtrée et traçable entre OSPF et d'autres sources de routes ;
- planifier une rotation d'authentification, un changement de métrique ou une migration sans perdre la maîtrise du domaine ;
- produire un diagnostic multi-cause fondé sur des captures, des journaux, la LSDB, la RIB/FIB et des tests de bout en bout ;
- rédiger une procédure de changement, de validation et de retour arrière reproductible.

## Comment utiliser le cours

Lis dans l'ordre les sections de conception et les schémas. Pour chaque laboratoire, capture l'état initial, forme une hypothèse unique, applique un seul changement principal, mesure son effet et compare le résultat à l'attendu. Les animations des SVG indiquent un chemin ou une séquence logique ; elles ne représentent pas la durée exacte d'un protocole ni une garantie de délai.


## 1. Penser OSPF comme un système distribué

### 1.1 Des routeurs autonomes, une topologie calculée

OSPF est un IGP à état de liens : chaque routeur maintient une base d'informations sur la topologie de son périmètre, puis exécute un calcul SPF local. Les routeurs ne partagent pas une unique table de routage centrale. Ils échangent des annonces, synchronisent une LSDB selon les règles de portée, puis chaque routeur sélectionne ses propres routes et programme son plan de transfert.

Cette distinction est fondamentale pendant un incident. Une LSA peut être présente dans la LSDB sans que le préfixe soit installé dans la RIB. Une route peut être présente dans la RIB sans que les paquets soient correctement acheminés dans la FIB. Et une FIB correcte ne garantit pas que la destination applicative, son chemin retour, son ACL ou son DNS fonctionne.

### 1.2 Cinq états à observer séparément

| Couche d'observation | Question experte | Exemples de preuves |
|---|---|---|
| Interface et transport | Le lien porte-t-il les paquets et sans erreur ? | `show interfaces`, compteurs, optique, VLAN, capture |
| Adjacence OSPF | Les voisins sont-ils dans l'état attendu ? | `show ip ospf neighbor`, logs, Hello/DBD |
| LSDB | Les LSA attendues existent-elles avec la bonne portée ? | `show ip ospf database`, âge, séquence, checksum |
| RIB/FIB | Le préfixe et le prochain saut sont-ils installés ? | `show ip route`, commande de FIB propre à la plate-forme |
| Service de bout en bout | Le flux utile marche-t-il dans les deux sens ? | ping ciblé, TCP/UDP applicatif, capture, test transactionnel |

### 1.3 Plan de contrôle et plan de transfert

Un routeur peut continuer de transférer des paquets pendant un redémarrage de son plan de contrôle si le matériel conserve une FIB valide et si les mécanismes de continuité sont conçus pour ce cas. À l'inverse, un processus OSPF peut être actif alors que la FIB est obsolète ou qu'un prochain saut n'est plus joignable. Toujours identifier le composant défaillant : processus de routage, CPU de contrôle, lien, ASIC de transfert, next-hop ou service distant.

### Schéma 1 — Plans de contrôle et de transfert

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg width="1000" height="510" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 510" role="img" aria-label="OSPF à grande échelle : séparer les plans"><rect x="0" y="0" width="1000" height="510" rx="16" fill="#0c1420"/><text x="28" y="35" fill="#edf4fb" font-size="23" font-weight="700">OSPF à grande échelle : séparer les plans</text><text x="28" y="60" fill="#adbdcf" font-size="13">Le contrôle OSPF construit des routes ; le plan de transfert exécute les décisions installées.</text><line x1="28" y1="79" x2="972" y2="79" stroke="#34475d" stroke-width="1.5"/><rect x="45" y="125" width="270" height="105" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="180.0" y="152" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Plan de contrôle</text><text x="180.0" y="174" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Hello · LSDB · SPF</text><rect x="365" y="125" width="270" height="105" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="500.0" y="152" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">RIB / sélection</text><text x="500.0" y="174" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">OSPF vs autres sources</text><rect x="685" y="125" width="270" height="105" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="820.0" y="152" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">FIB / transfert</text><text x="820.0" y="174" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Prochain saut installé</text><line x1="315" y1="178" x2="365" y2="178" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><circle r="5" fill="#45c7f5" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 315 178 L 365 178" dur="2.8s" begin="0s" repeatCount="indefinite"/></circle><line x1="635" y1="178" x2="685" y2="178" stroke="#4ade80" stroke-width="4" stroke-linecap="round"/><circle r="5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 635 178 L 685 178" dur="2.8s" begin="1s" repeatCount="indefinite"/></circle><rect x="75" y="315" width="245" height="82" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="197.5" y="342" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Événement réseau</text><text x="197.5" y="364" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">lien down / LSA nouvelle</text><rect x="378" y="315" width="245" height="82" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="500.5" y="342" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Recalcul contrôlé</text><text x="500.5" y="364" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">SPF + règles de sélection</text><rect x="680" y="315" width="245" height="82" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="802.5" y="342" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Validation du service</text><text x="802.5" y="364" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">route + retour + application</text><path d="M 197 315 L 197 230" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 6"/><path d="M 500 230 L 500 270 L 500 315" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 6"/><path d="M 623 356 L 680 356" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><circle r="5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 623 356 L 680 356" dur="2.2s" begin="0s" repeatCount="indefinite"/></circle><text x="500" y="440" text-anchor="middle" fill="#edf4fb" font-size="14" font-weight="700">Une adjacence FULL ne prouve pas à elle seule que la route est dans la FIB.</text><text x="500" y="465" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Inspecter séparément voisinage, LSDB, RIB/FIB, puis tester le flux utilisateur.</text></svg>
</div>

**À retenir :** aucune commande unique ne valide à elle seule le service. `show ip ospf neighbor` indique l'état des adjacences ; `show ip ospf database` indique l'information topologique connue ; `show ip route` et les commandes de transfert montrent les décisions installées. Le test applicatif démontre enfin si le service attendu fonctionne.


## 2. Concevoir une hiérarchie OSPF qui reste exploitable

### 2.1 Aire, frontière et portée de l'information

Une architecture multi-aires est utile lorsque la portée des annonces, la taille de la LSDB, les frontières administratives et les besoins de résumé justifient la complexité. Ajouter des aires sans plan de préfixes, sans besoin de limiter la topologie ni sans compréhension des frontières ne constitue pas une optimisation automatique.

Dans une conception classique, l'Area 0 joue le rôle de backbone. Les aires non-backbone doivent être raccordées au backbone par une conception OSPF valide. Les ABR participent à plusieurs aires et échangent les informations inter-aires prévues par le protocole. Les ASBR introduisent des routes provenant d'autres sources. Le même routeur peut cumuler des rôles, mais le schéma logique doit toujours montrer les frontières et les responsabilités sans ambiguïté.

### Schéma 2 — Architecture multi-aires et rôles de frontière

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg width="1000" height="590" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 590" role="img" aria-label="Topologie multi-aires : frontières et portée"><rect x="0" y="0" width="1000" height="590" rx="16" fill="#0c1420"/><text x="28" y="35" fill="#edf4fb" font-size="23" font-weight="700">Topologie multi-aires : frontières et portée</text><text x="28" y="60" fill="#adbdcf" font-size="13">Les ABR relient les aires ; Area 0 reste le backbone logique d’une conception OSPF classique.</text><line x1="28" y1="79" x2="972" y2="79" stroke="#34475d" stroke-width="1.5"/><rect x="34" y="105" width="932" height="130" rx="16" fill="#172332" stroke="#c4b5fd" stroke-width="1.8"/><text x="70" y="128" text-anchor="start" fill="#c4b5fd" font-size="13" font-weight="700">AREA 0 · BACKBONE</text><rect x="35" y="267" width="430" height="215" rx="16" fill="#132a35" stroke="#45c7f5" stroke-width="1.8"/><text x="68" y="291" text-anchor="start" fill="#45c7f5" font-size="13" font-weight="700">AREA 10 · UTILISATEURS</text><rect x="535" y="267" width="430" height="215" rx="16" fill="#2b2433" stroke="#fbbf24" stroke-width="1.8"/><text x="568" y="291" text-anchor="start" fill="#fbbf24" font-size="13" font-weight="700">AREA 20 · SERVICES / NSSA POSSIBLE</text><rect x="85" y="145" width="150" height="60" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="160.0" y="172" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-Core-1</text><text x="160.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">RID 1.1.1.1</text><rect x="400" y="145" width="150" height="60" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="475.0" y="172" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-Core-2</text><text x="475.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">RID 2.2.2.2</text><line x1="235" y1="175" x2="400" y2="175" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/><text x="317" y="160" text-anchor="middle" fill="#c4b5fd" font-size="12" font-weight="500">Backbone link</text><circle r="5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 235 175 L 400 175" dur="3s" begin="0s" repeatCount="indefinite"/></circle><rect x="105" y="337" width="150" height="62" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="180.0" y="364" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-ABR-10</text><text x="180.0" y="386" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Area 0 / 10</text><rect x="315" y="337" width="115" height="62" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="372.5" y="364" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-10</text><text x="372.5" y="386" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">interne</text><line x1="255" y1="368" x2="315" y2="368" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><line x1="180" y1="205" x2="180" y2="337" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/><text x="197" y="265" text-anchor="middle" fill="#c4b5fd" font-size="12" font-weight="500">ABR</text><rect x="585" y="337" width="150" height="62" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="660.0" y="364" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-ABR-20</text><text x="660.0" y="386" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Area 0 / 20</text><rect x="795" y="337" width="120" height="62" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="855.0" y="364" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-ASBR</text><text x="855.0" y="386" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">route externe</text><line x1="735" y1="368" x2="795" y2="368" stroke="#fbbf24" stroke-width="4" stroke-linecap="round"/><line x1="475" y1="205" x2="475" y2="240" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/><path d="M 475 240 L 660 240 L 660 337" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><text x="555" y="226" text-anchor="middle" fill="#c4b5fd" font-size="12" font-weight="500">ABR</text><rect x="760" y="416" width="180" height="65" rx="13" fill="#311e2a" stroke="#fb7185" stroke-width="2.4"/><text x="850.0" y="443" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Domaine externe</text><text x="850.0" y="465" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">BGP / statique</text><line x1="855" y1="399" x2="855" y2="416" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/><text x="500" y="524" text-anchor="middle" fill="#edf4fb" font-size="14" font-weight="700">Les routeurs internes ne partagent pas automatiquement une LSDB complète de toutes les aires.</text><text x="500" y="547" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Les annonces inter-aires et externes traversent les frontières selon les règles de LSA et le type d’aire.</text></svg>
</div>

### 2.2 Choisir des frontières qui ont du sens

Les critères de placement d'une frontière comprennent :

- la stabilité des liens et la fréquence des changements topologiques ;
- la taille de la LSDB et le nombre de préfixes à annoncer ;
- la cohérence du plan d'adressage avec un résumé non ambigu ;
- la capacité de diagnostic et de supervision sur chaque ABR/ASBR ;
- les besoins de routage externe, de filtrage et de politiques de sécurité ;
- le comportement souhaité lors de la perte d'un ABR ou d'une liaison vers Area 0.

Une frontière qui résume peut rendre la table plus compacte, mais elle peut aussi cacher des préfixes manquants. Un ABR dual-homed peut réduire le risque de panne unique, mais ne supprime pas automatiquement les défaillances communes des alimentations, des châssis, des liens ou de la configuration. Il faut documenter ce qui est redondant et ce qui demeure partagé.

### 2.3 Dimensionner selon les symptômes, pas seulement le nombre de routeurs

Le nombre de routeurs n'est qu'un indicateur. La charge OSPF dépend notamment du nombre de LSA, du taux de changement, des dépendances entre liens, du nombre d'instances, de la fréquence des événements, du matériel de contrôle et de la fréquence des calculs SPF. Un domaine modeste mais instable peut être plus difficile à exploiter qu'un domaine plus grand et stable.

Indicateurs à suivre : nombre et variation des LSA par type, fréquence des recalculs SPF, changements d'adjacence, origine des événements, temps entre réception de la LSA et installation de la route, CPU, mémoire, temps de convergence observé et pertes applicatives. Établir une ligne de base permet de reconnaître un comportement anormal.

### 2.4 Pourquoi l'agrégation ne résout pas toutes les difficultés

L'agrégation inter-aire masque certains détails de préfixes au-delà de la frontière ; elle ne réduit pas nécessairement tous les LSA intra-aire de l'aire d'origine. Un résumé valide doit correspondre à une allocation hiérarchique et à la politique de reachability réellement voulue. Éviter un résumé trop large qui couvre des réseaux absents, des réseaux d'une autre organisation ou des destinations avec un chemin indépendant.

Avant de modifier le résumé, calculer le préfixe agrégé, lister tous les préfixes spécifiques couverts, examiner les routes plus précises, vérifier la route de rejet éventuelle et déterminer le comportement attendu lorsque l'un des sous-réseaux disparaît. Un résumé peut être sain du point de vue de la table tout en attirant le trafic vers une destination indisponible si sa portée a été mal choisie.


## 3. LSA : identité, portée, vieillissement et cohérence

### 3.1 Lire une LSA comme un objet d'état versionné

Une LSA possède notamment un type, un Link State ID, un Advertising Router, un numéro de séquence, un âge et un checksum. Ces champs permettent de distinguer les objets, de déterminer quelle instance est la plus récente et de vérifier leur intégrité. Le Link State ID n'est pas systématiquement équivalent au préfixe annoncé ; sa signification dépend du type de LSA.

Une augmentation inattendue des LSA ne signifie pas automatiquement une attaque. Elle peut être causée par une instabilité d'interface, une boucle de redistribution, un changement de route, une configuration qui se répète ou un comportement logiciel. L'investigation doit comparer l'origine, les séquences, les âges, les interfaces et l'horodatage des changements.

### 3.2 Portée et règles de propagation

Les Types 1 et 2 décrivent la topologie d'une aire ; les Types 3 et 4 portent des informations inter-aires ; le Type 5 annonce typiquement des routes externes dans les aires qui les acceptent ; le Type 7 décrit des routes externes dans une NSSA et peut être traduit par un ABR selon les règles. Il faut éviter de traiter toutes les LSA comme des objets librement floodés partout.

### Schéma 3 — Portée des LSA et comportement des aires

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg width="1000" height="600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600" role="img" aria-label="Portée des LSA : topologie locale, inter-aires et routes externes"><rect x="0" y="0" width="1000" height="600" rx="16" fill="#0c1420"/><text x="28" y="35" fill="#edf4fb" font-size="23" font-weight="700">Portée des LSA : topologie locale, inter-aires et routes externes</text><text x="28" y="60" fill="#adbdcf" font-size="13">Une frontière OSPF ne copie pas toutes les LSA : portée et origine dépendent du type et de l’aire.</text><line x1="28" y1="79" x2="972" y2="79" stroke="#34475d" stroke-width="1.5"/><rect x="35" y="105" width="275" height="180" rx="14" fill="#132a35" stroke="#45c7f5" stroke-width="2"/><text x="172" y="132" text-anchor="middle" fill="#45c7f5" font-size="14" font-weight="700">AIRE 10 · SOURCE</text><rect x="65" y="165" width="215" height="72" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="172.5" y="192" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Routeur interne</text><text x="172.5" y="214" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Type 1 / Type 2 locaux</text><rect x="405" y="165" width="190" height="72" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="500.0" y="192" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">ABR</text><text x="500.0" y="214" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">génère Type 3 / 4</text><rect x="690" y="105" width="275" height="180" rx="14" fill="#172332" stroke="#c4b5fd" stroke-width="2"/><text x="827" y="132" text-anchor="middle" fill="#c4b5fd" font-size="14" font-weight="700">AIRE 20 · NORMALE</text><rect x="720" y="165" width="215" height="72" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="827.5" y="192" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">LSDB cible</text><text x="827.5" y="214" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Type 3 / 4 selon besoin</text><line x1="310" y1="201" x2="405" y2="201" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><line x1="595" y1="201" x2="720" y2="201" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/><circle r="5" fill="#45c7f5" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 310 201 L 405 201" dur="2.7s" begin="0s" repeatCount="indefinite"/></circle><circle r="5" fill="#c4b5fd" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 595 201 L 720 201" dur="2.7s" begin="1s" repeatCount="indefinite"/></circle><text x="500" y="313" text-anchor="middle" fill="#edf4fb" font-size="12" font-weight="700">Les Type 1 / 2 décrivent la topologie de leur aire ; l’ABR construit les annonces inter-aires.</text><rect x="35" y="350" width="420" height="175" rx="14" fill="#2a2433" stroke="#fbbf24" stroke-width="2"/><text x="245" y="377" text-anchor="middle" fill="#fbbf24" font-size="14" font-weight="700">NSSA · ROUTE EXTERNE LOCALE</text><rect x="65" y="410" width="155" height="70" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="142.5" y="437" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">ASBR NSSA</text><text x="142.5" y="459" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">origine Type 7</text><rect x="285" y="410" width="140" height="70" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="355.0" y="437" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">ABR NSSA</text><text x="355.0" y="459" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">traduction possible</text><line x1="220" y1="445" x2="285" y2="445" stroke="#fbbf24" stroke-width="4" stroke-linecap="round"/><circle r="5" fill="#fbbf24" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 220 445 L 285 445" dur="2.4s" begin="0s" repeatCount="indefinite"/></circle><rect x="545" y="350" width="420" height="175" rx="14" fill="#172332" stroke="#4ade80" stroke-width="2"/><text x="755" y="377" text-anchor="middle" fill="#4ade80" font-size="13" font-weight="700">AIRE NORMALE · APRÈS TRADUCTION</text><rect x="650" y="410" width="250" height="70" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="775.0" y="437" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">LSDB de l’aire cible</text><text x="775.0" y="459" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Type 5 traduit, si applicable</text><path d="M 425 445 L 490 445 L 490 492 L 620 492 L 620 445 L 650 445" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 5"/><circle r="5" fill="#c4b5fd" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 425 445 L 490 445 L 490 492 L 620 492 L 620 445 L 650 445" dur="3s" begin="0.8s" repeatCount="indefinite"/></circle><text x="500" y="566" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">La traduction Type 7 → Type 5 dépend des règles OSPF et du rôle de l’ABR ; elle n’est pas universelle.</text></svg>
</div>

### 3.3 Vieillissement, rafraîchissement et changements fréquents

Un âge de LSA doit être interprété avec le numéro de séquence, le checksum, l'origine et l'historique. Une seule capture ne permet pas d'affirmer qu'une LSA « boucle ». Collecter plusieurs observations horodatées depuis des routeurs pertinents. Comparer les mêmes identifiants de LSA sur plusieurs nœuds et vérifier les compteurs de flooding, les changements de topologie ainsi que les événements de routage à la source.

Un volume élevé d'annonces peut augmenter le travail de synchronisation et la charge du plan de contrôle. Rechercher le déclencheur plutôt que tenter de masquer le symptôme en augmentant arbitrairement les temporisateurs. Les mécanismes d'atténuation de flooding, d'optimisation ou de suppression de préfixes sont dépendants des implémentations et doivent être activés seulement après analyse de leur effet fonctionnel.

### 3.4 Prefix suppression : utile, mais à justifier

La suppression de certains préfixes de transit peut réduire les annonces de réseaux qui servent uniquement à relier des routeurs, dans un design qui n'exige pas leur annonce comme destination. Elle n'est pas une commande générique à activer partout : vérifier quelles adresses doivent rester joignables, les exigences de gestion, les interfaces passives et le comportement de la plate-forme. La documentation Cisco décrit les conditions de la fonction OSPF prefix suppression pour IOS/IOS XE ; sa disponibilité dépend de la version.


## 4. Coût, ECMP et sélection des chemins

### 4.1 Coût total et sensibilité à la métrique

La métrique OSPF est calculée à partir des coûts d'interface selon l'implémentation. Dans un chemin, les coûts s'additionnent ; une modification locale peut donc changer les chemins retenus par de nombreux routeurs. Ne déduis pas le chemin de la vitesse nominale du lien sans inspecter le coût configuré et la valeur effective.

Avant de changer un coût, calculer les chemins candidats et ceux qui seront éliminés, prévoir les routes retour, mesurer la capacité restante et vérifier les interactions avec les politiques externes. Une modification globale de référence de bande passante peut changer les coûts effectifs de plusieurs interfaces : le plan de changement doit estimer son impact avant la commande.

### 4.2 ECMP : plusieurs next-hops valides

Quand plusieurs chemins de même coût et de validité compatible existent, OSPF peut installer des chemins à coût égal, dans les limites de la plate-forme et des paramètres de maximum-paths. Le routeur peut répartir les flux en fonction d'un hachage de champs de paquet. Une répartition inégale n'est donc pas automatiquement un défaut de protocole : un petit nombre de flux ou un hachage déséquilibré peut concentrer le trafic sur un membre.

### Schéma 4 — ECMP et coûts cumulés

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg width="1000" height="560" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 560" role="img" aria-label="Chemins de coût égal : ECMP"><rect x="0" y="0" width="1000" height="560" rx="16" fill="#0c1420"/><text x="28" y="35" fill="#edf4fb" font-size="23" font-weight="700">Chemins de coût égal : ECMP</text><text x="28" y="60" fill="#adbdcf" font-size="13">Exemple pédagogique : deux chemins vers 10.60.0.0/16 ont le même coût total.</text><line x1="28" y1="79" x2="972" y2="79" stroke="#34475d" stroke-width="1.5"/><rect x="55" y="250" width="135" height="70" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="122.5" y="277" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R1</text><text x="122.5" y="299" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">source</text><rect x="310" y="140" width="145" height="70" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="382.5" y="167" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R2</text><text x="382.5" y="189" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">coût 10 depuis R1</text><rect x="310" y="355" width="145" height="70" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="382.5" y="382" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R3</text><text x="382.5" y="404" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">coût 10 depuis R1</text><rect x="570" y="140" width="145" height="70" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="642.5" y="167" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R4</text><text x="642.5" y="189" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">coût 10 depuis R2</text><rect x="570" y="355" width="145" height="70" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="642.5" y="382" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R5</text><text x="642.5" y="404" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">coût 10 depuis R3</text><rect x="820" y="250" width="135" height="70" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="887.5" y="277" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">LAN cible</text><text x="887.5" y="299" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">10.60.0.0/16</text><line x1="190" y1="275" x2="310" y2="175" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><line x1="190" y1="295" x2="310" y2="390" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><line x1="455" y1="175" x2="570" y2="175" stroke="#4ade80" stroke-width="4" stroke-linecap="round"/><line x1="455" y1="390" x2="570" y2="390" stroke="#4ade80" stroke-width="4" stroke-linecap="round"/><line x1="715" y1="175" x2="820" y2="265" stroke="#4ade80" stroke-width="4" stroke-linecap="round"/><line x1="715" y1="390" x2="820" y2="305" stroke="#4ade80" stroke-width="4" stroke-linecap="round"/><text x="240" y="213" text-anchor="middle" fill="#45c7f5" font-size="13" font-weight="500">10</text><text x="240" y="355" text-anchor="middle" fill="#45c7f5" font-size="13" font-weight="500">10</text><text x="512" y="160" text-anchor="middle" fill="#4ade80" font-size="13" font-weight="500">10</text><text x="512" y="375" text-anchor="middle" fill="#4ade80" font-size="13" font-weight="500">10</text><text x="770" y="207" text-anchor="middle" fill="#4ade80" font-size="13" font-weight="500">5</text><text x="770" y="365" text-anchor="middle" fill="#4ade80" font-size="13" font-weight="500">5</text><circle r="5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 190 275 L 310 175 L 455 175 L 570 175 L 715 175 L 820 265" dur="3s" begin="0s" repeatCount="indefinite"/></circle><circle r="5" fill="#fbbf24" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 190 295 L 310 390 L 455 390 L 570 390 L 715 390 L 820 305" dur="3s" begin="1s" repeatCount="indefinite"/></circle><text x="500" y="465" text-anchor="middle" fill="#edf4fb" font-size="15" font-weight="700">Coût total de chaque chemin = 25 (10 + 10 + 5).</text><text x="500" y="490" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Si les préfixes et coûts installés le permettent, le routeur peut installer plusieurs next-hops.</text><text x="500" y="515" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">ECMP distribue généralement par flux selon l’implémentation, pas forcément paquet par paquet.</text></svg>
</div>

### 4.3 Vérifier le résultat de la décision

Sur Cisco IOS/IOS XE, commandes potentielles :

```text
show ip route <prefixe>
show ip ospf route
show ip ospf interface brief
show ip ospf database
show ip cef <destination>
```

La disponibilité et les paramètres de ces commandes varient selon la plate-forme. Si `show ip ospf route` ou une variante CEF n'est pas prise en charge, utiliser la commande d'inspection équivalente dans la documentation locale. Distinguer la route candidate, la route installée, la résolution du next-hop et les chemins réellement utilisés par le plan de transfert.

### 4.4 ECMP et sécurité opérationnelle

Un chemin à coût égal ne garantit pas des latences identiques, des capacités identiques ou la même politique de sécurité. Vérifier les contraintes de firewall stateful, les chemins asymétriques, les NAT, la QoS et les différences d'accès. Si un flux traverse un nœud stateful dans un sens mais l'évite dans l'autre, il peut échouer même si le routage paraît cohérent.


## 5. Convergence : ne pas confondre rapidité et stabilité

### 5.1 Les délais viennent de plusieurs mécanismes

Le rétablissement observé est la somme d'étapes qui peuvent se chevaucher : détection physique ou logique, traitement de l'événement, mise à jour OSPF, inondation et acceptation de LSA, calcul SPF, sélection de route, programmation FIB et reprise applicative. Le protocole le plus rapide n'est pas forcément le seul facteur dominant.

### Schéma 5 — Détection et convergence avec BFD

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg width="1000" height="540" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" role="img" aria-label="Convergence : détection, calcul et programmation"><rect x="0" y="0" width="1000" height="540" rx="16" fill="#0c1420"/><text x="28" y="35" fill="#edf4fb" font-size="23" font-weight="700">Convergence : détection, calcul et programmation</text><text x="28" y="60" fill="#adbdcf" font-size="13">BFD peut accélérer la détection d’une panne de prochain saut ; il ne remplace ni OSPF ni la validation applicative.</text><line x1="28" y1="79" x2="972" y2="79" stroke="#34475d" stroke-width="1.5"/><rect x="45" y="160" width="195" height="82" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="142.5" y="187" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Défaut</text><text x="142.5" y="209" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">lien ou voisin</text><rect x="280" y="160" width="195" height="82" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="377.5" y="187" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Détection</text><text x="377.5" y="209" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">BFD / Hello</text><rect x="515" y="160" width="195" height="82" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="612.5" y="187" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Réaction OSPF</text><text x="612.5" y="209" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">adjacence / LSA</text><rect x="750" y="160" width="195" height="82" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="847.5" y="187" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">SPF + FIB</text><text x="847.5" y="209" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">nouveau chemin</text><line x1="240" y1="201" x2="280" y2="201" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><circle r="5" fill="#45c7f5" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 240 201 L 280 201" dur="2.4s" begin="0s" repeatCount="indefinite"/></circle><line x1="475" y1="201" x2="515" y2="201" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/><circle r="5" fill="#c4b5fd" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 475 201 L 515 201" dur="2.4s" begin="0s" repeatCount="indefinite"/></circle><line x1="710" y1="201" x2="750" y2="201" stroke="#4ade80" stroke-width="4" stroke-linecap="round"/><circle r="5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 710 201 L 750 201" dur="2.4s" begin="0s" repeatCount="indefinite"/></circle><rect x="95" y="315" width="350" height="75" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="270.0" y="342" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Mesure réseau</text><text x="270.0" y="364" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">perte, latence, route, prochain saut</text><rect x="555" y="315" width="350" height="75" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="730.0" y="342" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Mesure applicative</text><text x="730.0" y="364" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">session, requête, transaction métier</text><line x1="445" y1="352" x2="555" y2="352" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/><text x="500" y="440" text-anchor="middle" fill="#edf4fb" font-size="15" font-weight="700">Un BFD UP ne prouve pas que le service distant fonctionne.</text><text x="500" y="464" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Une détection agressive peut générer des faux positifs si le plan de contrôle est chargé.</text><text x="500" y="489" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Mesurer séparément : temps de détection, convergence, pertes de paquets et reprise applicative.</text></svg>
</div>

### 5.2 SPF throttling et LSA throttling

Les implémentations peuvent fournir des mécanismes de temporisation ou de contrôle des calculs SPF et de l'origine/flooding des LSA. Leur objectif est notamment d'empêcher un changement continu de provoquer des recalculs sans répit. Une temporisation trop grande peut retarder la réaction à une panne ; trop agressive, elle peut amplifier le coût de la charge et contribuer à l'instabilité. Il faut mesurer le taux de changement et choisir les paramètres en connaissance de cause.

Procédure de réglage :

1. collecter la fréquence réelle des recalculs, les déclencheurs et la charge CPU ;
2. déterminer si l'origine est physique, logique, redistribution ou plan de contrôle ;
3. évaluer les paramètres actuels et les objectifs de convergence ;
4. effectuer le réglage dans une maquette de même version ;
5. tester une panne unique, puis un scénario de changements répétés ;
6. comparer perte de trafic, temps de rétablissement, CPU et stabilité ;
7. documenter les valeurs, leur justification et le retour arrière.

Ne cherche pas à masquer un défaut physique instable par un délai plus long sans comprendre le défaut. De même, ne mets pas tous les timers au minimum dans l'espoir de rendre le réseau « plus rapide ».

### 5.3 BFD : détection rapide d'un voisin indisponible

Bidirectional Forwarding Detection (BFD) fournit un mécanisme de détection de défaut de chemin à faible délai, indépendant de nombreux protocoles de routage. OSPF peut utiliser l'état BFD comme signal pour accélérer la réaction à une défaillance. BFD ne calcule pas la route : il signale une condition de joignabilité à l'intégration prévue entre les protocoles.

Les intervalles et multiplicateurs doivent être raisonnables par rapport au matériel, à la charge et aux délais de transport. Une configuration trop agressive peut provoquer des déclarations de panne lors de pics CPU ou de congestion. Vérifier la prise en charge de BFD, les timers négociés, les sessions et la propagation de l'événement vers OSPF.

### 5.4 Fast reroute et Loop-Free Alternate

Un mécanisme de fast reroute peut préinstaller un chemin de secours afin de réduire le délai entre la détection de la panne et le réacheminement. Un candidat de secours n'est utile que si sa condition de boucle est satisfaite et si le matériel/logiciel réalise la fonction demandée. Ne pas confondre calcul d'un LFA, présence d'un next-hop de secours dans une sortie de commande et activation réelle du chemin de protection.

### Schéma 6 — Fast reroute et LFA candidat

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg width="1000" height="560" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 560" role="img" aria-label="Fast reroute : chemin primaire et LFA candidat"><rect x="0" y="0" width="1000" height="560" rx="16" fill="#0c1420"/><text x="28" y="35" fill="#edf4fb" font-size="23" font-weight="700">Fast reroute : chemin primaire et LFA candidat</text><text x="28" y="60" fill="#adbdcf" font-size="13">Le chemin de secours n’est valide que si les conditions de boucle et la prise en charge de la plate-forme sont satisfaites.</text><line x1="28" y1="79" x2="972" y2="79" stroke="#34475d" stroke-width="1.5"/><rect x="55" y="245" width="130" height="70" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="120.0" y="272" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-SOURCE</text><text x="120.0" y="294" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">destination D</text><rect x="300" y="150" width="145" height="70" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="372.5" y="177" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-A</text><text x="372.5" y="199" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">primaire</text><rect x="300" y="360" width="145" height="70" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="372.5" y="387" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-B</text><text x="372.5" y="409" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">LFA candidat</text><rect x="580" y="245" width="145" height="70" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="652.5" y="272" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">R-D</text><text x="652.5" y="294" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">destination</text><line x1="185" y1="270" x2="300" y2="185" stroke="#4ade80" stroke-width="5" stroke-linecap="round"/><line x1="445" y1="185" x2="580" y2="270" stroke="#4ade80" stroke-width="5" stroke-linecap="round"/><line x1="185" y1="295" x2="300" y2="395" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><line x1="445" y1="395" x2="580" y2="290" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><text x="240" y="215" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="500">coût 3</text><text x="512" y="210" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="500">coût 3</text><text x="240" y="355" text-anchor="middle" fill="#45c7f5" font-size="12" font-weight="500">coût 8</text><text x="512" y="365" text-anchor="middle" fill="#45c7f5" font-size="12" font-weight="500">coût 2</text><circle r="5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 185 270 L 300 185 L 445 185 L 580 270" dur="2.5s" begin="0s" repeatCount="indefinite"/></circle><circle r="5" fill="#45c7f5" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 185 295 L 300 395 L 445 395 L 580 290" dur="2.5s" begin="1.1s" repeatCount="indefinite"/></circle><rect x="775" y="155" width="175" height="80" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="862.5" y="182" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Avant panne</text><text x="862.5" y="204" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">R-SOURCE → R-A → R-D</text><rect x="775" y="330" width="175" height="80" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="862.5" y="357" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Après panne</text><text x="862.5" y="379" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">R-SOURCE → R-B → R-D</text><text x="500" y="470" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="700">Chemin primaire = 6 ; candidat de secours = 10. Les coûts ne suffisent pas à eux seuls à valider une LFA.</text><text x="500" y="495" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">La condition loop-free dépend des distances vers la destination et de la topologie connue.</text><text x="500" y="520" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Valider explicitement les capacités FRR/LFA et la route installée sur l’équipement cible.</text></svg>
</div>

**Règle d'interprétation :** l'exemple de l'illustration montre des chemins candidats et leurs coûts. Il ne constitue pas une preuve que n'importe quelle topologie satisfait la condition de Loop-Free Alternate. Vérifier le calcul de distances, la direction de la défaillance, la source du next-hop et la commande propre à la plateforme pour confirmer que la protection est effectivement programmée.


## 6. Graceful Restart et continuité du forwarding

### 6.1 Ce que Graceful Restart peut — et ne peut pas — garantir

Le Graceful Restart OSPF peut permettre au plan de transfert de continuer à utiliser une FIB encore valide pendant qu'un processus OSPF redémarre. Les voisins qui agissent comme helpers peuvent préserver temporairement certaines informations si les conditions du mécanisme sont respectées. Ce mécanisme repose sur des hypothèses : la topologie doit rester stable pendant la période utile, la FIB conservée doit rester valide, et les voisins ainsi que l'implémentation doivent coopérer.

### Schéma 7 — Graceful Restart, conditions et limites

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg width="1000" height="565" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 565" role="img" aria-label="Graceful Restart : continuité conditionnelle du forwarding"><rect x="0" y="0" width="1000" height="565" rx="16" fill="#0c1420"/><text x="28" y="35" fill="#edf4fb" font-size="23" font-weight="700">Graceful Restart : continuité conditionnelle du forwarding</text><text x="28" y="60" fill="#adbdcf" font-size="13">Le plan de transfert peut rester actif pendant un redémarrage du contrôle, uniquement si les hypothèses sont satisfaites.</text><line x1="28" y1="79" x2="972" y2="79" stroke="#34475d" stroke-width="1.5"/><rect x="55" y="135" width="175" height="70" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="142.5" y="162" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">État stable</text><text x="142.5" y="184" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">LSDB + FIB valides</text><rect x="280" y="135" width="175" height="70" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="367.5" y="162" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Redémarrage</text><text x="367.5" y="184" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">processus OSPF relancé</text><rect x="505" y="135" width="175" height="70" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="592.5" y="162" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Mode helper</text><text x="592.5" y="184" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">voisins conservent l’état</text><rect x="730" y="135" width="215" height="70" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="837.5" y="162" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Re-synchronisation</text><text x="837.5" y="184" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">adjacences et base rétablies</text><line x1="230" y1="170" x2="280" y2="170" stroke="#fbbf24" stroke-width="4" stroke-linecap="round"/><line x1="455" y1="170" x2="505" y2="170" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/><line x1="680" y1="170" x2="730" y2="170" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><circle r="5" fill="#4ade80" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 230 170 L 280 170 L 455 170 L 505 170 L 680 170 L 730 170" dur="3.3s" begin="0s" repeatCount="indefinite"/></circle><rect x="65" y="285" width="410" height="115" rx="14" fill="#143025" stroke="#4ade80" stroke-width="2"/><text x="270" y="315" text-anchor="middle" fill="#4ade80" font-size="15" font-weight="700">Si la topologie reste stable</text><text x="270" y="343" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="400">FIB valide + voisins helpers compatibles</text><text x="270" y="366" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">peuvent éviter un retrait de route immédiat</text><rect x="525" y="285" width="410" height="115" rx="14" fill="#34202a" stroke="#fb7185" stroke-width="2"/><text x="730" y="315" text-anchor="middle" fill="#fb7185" font-size="15" font-weight="700">Si la topologie change</text><text x="730" y="343" text-anchor="middle" fill="#edf4fb" font-size="13" font-weight="400">ne pas conserver des hypothèses périmées</text><text x="730" y="366" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">revenir à la convergence normale</text><text x="500" y="455" text-anchor="middle" fill="#edf4fb" font-size="14" font-weight="700">Graceful Restart n’est pas une promesse de zéro perte et ne convient pas à toute panne.</text><text x="500" y="480" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Tester planned/unplanned, compatibilité helper et comportement lors d’un changement de topologie.</text><text x="500" y="506" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">La plate-forme et les extensions prises en charge déterminent les détails opérationnels.</text></svg>
</div>

### 6.2 Pourquoi les changements de topologie comptent

Si un lien critique échoue pendant le redémarrage et que les voisins continuent à traiter le routeur comme s'il était stable, l'ancien état peut devenir dangereux. Le mécanisme de graceful restart est conçu avec des procédures d'abandon lorsque les hypothèses ne sont plus valides ; l'implémentation et le scénario doivent être vérifiés. Un redémarrage gracieux n'est ni une garantie de zero packet loss, ni un remplacement de la redondance de liens ou de la supervision applicative.

### 6.3 Validation d'un déploiement GR

- identifier si la fonction concerne les redémarrages planifiés, non planifiés ou les deux ;
- valider les capacités de helper des voisins et les interactions avec les autres protocoles ;
- mesurer le forwarding avant, pendant et après le redémarrage ;
- provoquer, en laboratoire, un changement de topologie au moment du restart pour vérifier le comportement de sortie du mode gracieux ;
- vérifier les routes installées et les sessions applicatives ;
- ne pas activer une fonction seulement parce que le nom promet une reprise sans coupure.


## 7. Redistribution : rendre l'entrée et la sortie contrôlables

### 7.1 Pourquoi la redistribution est un risque de conception

La redistribution injecte dans OSPF des routes issues d'une autre source (route statique, BGP ou autre protocole), généralement à travers un ASBR. Une redistribution réciproque peut créer des boucles de route, des préférences instables, des préfixes indésirables ou une origine impossible à diagnostiquer si aucune politique n'est appliquée.

### Schéma 8 — Redistribution contrôlée et prévention des boucles

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg width="1000" height="560" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 560" role="img" aria-label="Redistribution contrôlée : éviter les boucles de routes"><rect x="0" y="0" width="1000" height="560" rx="16" fill="#0c1420"/><text x="28" y="35" fill="#edf4fb" font-size="23" font-weight="700">Redistribution contrôlée : éviter les boucles de routes</text><text x="28" y="60" fill="#adbdcf" font-size="13">Une frontière explicite, une allow-list et des tags documentés rendent les annonces externes auditées.</text><line x1="28" y1="79" x2="972" y2="79" stroke="#34475d" stroke-width="1.5"/><rect x="45" y="170" width="200" height="88" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="145.0" y="197" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Domaine OSPF</text><text x="145.0" y="219" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">préfixes internes</text><rect x="340" y="145" width="250" height="135" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="465.0" y="172" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">ASBR / politique</text><text x="465.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">prefix-list + route-map</text><rect x="685" y="170" width="235" height="88" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="802.5" y="197" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Autre domaine</text><text x="802.5" y="219" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">BGP / statique / EIGRP</text><line x1="245" y1="215" x2="340" y2="215" stroke="#45c7f5" stroke-width="4" stroke-linecap="round"/><line x1="590" y1="215" x2="685" y2="215" stroke="#fbbf24" stroke-width="4" stroke-linecap="round"/><circle r="5" fill="#45c7f5" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 245 215 L 340 215" dur="2.7s" begin="0s" repeatCount="indefinite"/></circle><circle r="5" fill="#fbbf24" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 590 215 L 685 215" dur="2.7s" begin="1s" repeatCount="indefinite"/></circle><rect x="100" y="350" width="300" height="82" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="250.0" y="377" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Tag de provenance</text><text x="250.0" y="399" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">ex. 65010 : origine OSPF→BGP</text><rect x="600" y="350" width="300" height="82" rx="13" fill="#152235" stroke="#fb7185" stroke-width="2.4"/><text x="750.0" y="377" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Filtre au retour</text><text x="750.0" y="399" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">refuser tag déjà injecté</text><line x1="400" y1="391" x2="600" y2="391" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round"/><path d="M 802 258 L 802 315 L 750 315 L 750 350" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 6"/><circle r="5" fill="#fb7185" stroke="#edf4fb" stroke-width="1.8"><animateMotion path="M 802 258 L 802 315 L 750 315 L 750 350" dur="2.8s" begin="0s" repeatCount="indefinite"/></circle><text x="500" y="470" text-anchor="middle" fill="#edf4fb" font-size="14" font-weight="700">Ne redistribue pas globalement toutes les routes sans liste de préfixes et politique de boucle.</text><text x="500" y="495" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Les tags n’ont de valeur que si les route-maps/filters les appliquent dans le bon sens.</text><text x="500" y="520" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">La syntaxe de tags et filtres varie selon le protocole et l’OS réseau.</text></svg>
</div>

### 7.2 Allow-list, métrique et tag

Une politique de redistribution devrait expliciter :

- les préfixes que l'organisation a l'intention de redistribuer ;
- la source autorisée et les interfaces ou voisins concernés ;
- la métrique externe et le type externe attendus ;
- les tags utilisés pour identifier l'origine ;
- les routes à exclure, notamment les routes apprises depuis le même domaine ;
- le plan de retour arrière et les commandes de vérification.

Les tags ne protègent pas automatiquement des boucles. Ils n'ont d'effet que si une politique les attache, les conserve comme attendu et filtre les routes marquées à la frontière de retour. Le contenu des tags, leur propagation et leur interprétation doivent être documentés entre équipes et protocoles.

### 7.3 E1 et E2 dans un contexte opérationnel

Une route E1 prend en compte le coût OSPF interne vers l'ASBR et la métrique externe. En E2, la métrique externe constitue le facteur principal de comparaison et le coût interne intervient pour départager certaines routes à métrique externe égale. Le choix doit correspondre à la politique réseau et au point d'entrée que l'on veut favoriser. Ne choisis pas E1 ou E2 uniquement par habitude.

### 7.4 Vérifier une redistribution en quatre endroits

1. route d'origine dans la table/source initiale ;
2. policy d'export sur l'ASBR ;
3. LSA Type 5 ou Type 7 et son origine ;
4. route installée et route retour au point de destination.

Si un préfixe ne se comporte pas comme prévu, comparer chaque étage avant de changer la métrique. Un préfixe peut être présent dans la base mais rejeté à l'installation par une préférence concurrente ou un next-hop non valide.


## 8. Sécurité OSPF : authentification et intégrité opérationnelle

### 8.1 Authentification n'est pas une seule option universelle

Les possibilités d'authentification dépendent de la version OSPF et de la plateforme. Des mécanismes cryptographiques existent pour OSPFv2, notamment les extensions définies par les RFC 5709 et 7474, mais le support, la syntaxe et les capacités de gestion de clés varient. Vérifier la documentation locale au lieu de supposer qu'un seul type de commande est disponible sur tous les équipements.

L'objectif opérationnel est d'empêcher que des routeurs non autorisés puissent influencer la topologie, tout en préservant la continuité des adjacences légitimes pendant une migration. Les secrets et les clés ne doivent pas être copiés dans des tickets publics, des dépôts de code ou des captures partagées sans protection.

### 8.2 Rotation de clés : chevauchement contrôlé

Avant une rotation, inventorier tous les voisins, les interfaces/aires couvertes, les mécanismes actuellement utilisés et les différences de version. Choisir une fenêtre de changement, valider les types de clés compatibles et définir l'ordre de déploiement. Si la plate-forme prend en charge plusieurs clés et une période de chevauchement, cette capacité peut faciliter la transition ; il ne faut pas supposer qu'elle existe partout.

Pendant le changement, suivre immédiatement les états de voisinage, les logs, les compteurs d'authentification et les routes. Si une adjacence tombe, arrêter l'élargissement et appliquer le retour arrière documenté. En fin de migration, vérifier que les anciennes clés ne sont plus acceptées lorsque la politique l'exige.

### 8.3 Protéger le périmètre du contrôle

- ne pas activer OSPF sur des interfaces qui n'ont pas vocation à former des voisins ; utiliser les interfaces passives lorsque l'implémentation et la conception le justifient ;
- limiter les voisins et sources de routes aux segments attendus ;
- filtrer les routes redistribuées à la frontière ;
- contrôler les Router ID, les interfaces OSPF et les changements de topologie ;
- corréler les journaux des équipements avec la supervision et la gestion de changement ;
- réviser les accès administratifs, les sauvegardes et la rotation des secrets.

La sécurité OSPF ne se résume pas à l'authentification. Un administrateur autorisé peut mal configurer une aire, un résumé, un coût ou une redistribution ; le contrôle de changement et le monitoring restent essentiels.


## 9. OSPFv2, OSPFv3 et choix d'architecture

OSPFv2 est défini historiquement pour IPv4 par la RFC 2328, mise à jour par diverses extensions. OSPFv3 a été conçu pour IPv6 et a ensuite reçu des extensions pour la prise en charge de familles d'adresses supplémentaires selon les modes et versions. L'interopérabilité n'est pas une hypothèse : vérifier les fonctionnalités de l'image logicielle et les capacités de la plate-forme ciblée.

Ne traite pas l'activation d'OSPFv3 comme un simple copier-coller du processus OSPFv2. Les commandes, le contexte d'interface, les mécanismes d'identité et les éléments de configuration diffèrent selon l'OS réseau. Si IPv4 et IPv6 coexistent, vérifier la couverture de chaque famille, les annonces et les routes dans chacune des tables concernées.

Pour les questions OSPFv3 multi-familles, la RFC 5838 décrit un mécanisme permettant de prendre en charge plusieurs familles d'adresses. La configuration concrète reste dépendante des capacités de l'implémentation. Ce cours est centré sur l'ingénierie OSPFv2 ; la maîtrise complète d'OSPFv3 mérite un cours dédié.


## 10. Observabilité : mesurer ce qui se passe réellement

### 10.1 Captures et commandes à corréler

OSPFv2 utilise le protocole IP numéro 89, pas TCP ni UDP. Un filtre de capture courant dans Wireshark est `ospf`. Capturez à un endroit qui permet de voir les deux côtés du lien si possible ; une capture sur un seul côté peut masquer un paquet perdu sur l'autre segment.

Commandes usuelles, selon le support logiciel :

```text
show ip ospf neighbor detail
show ip ospf interface
show ip ospf database
show ip ospf statistics
show ip route ospf
show ip route <prefixe>
show ip protocols
show logging
```

Ajoute les commandes de FIB/CEF ou de BFD spécifiques à la plate-forme. Ne pars pas du principe qu'une commande est disponible partout. Enregistre le résultat avec l'heure, le routeur, l'interface, le contexte de changement et la destination de test.

### 10.2 Ce qu'il faut mesurer

- transitions d'adjacence et durée passée dans chaque état ;
- quantité de LSA et fréquence des changements ;
- nombre de calculs SPF et charge CPU associée ;
- temps entre le changement de topologie et l'installation d'une route ;
- disponibilité du next-hop dans la FIB ;
- perte de paquets au niveau hôte et délai de retour du service ;
- fréquence et origine des changements de route ;
- résultats des sondes applicatives et DNS.

Les événements doivent être corrélés sur plusieurs équipements. Un log du routeur qui détecte une panne et un log du routeur qui installe la route peuvent avoir des délais d'horloge différents. Synchroniser les horloges et noter les écarts avant d'établir une chronologie.

### Schéma 9 — Parcours de diagnostic OSPF

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:1rem">
<svg width="1000" height="590" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 590" role="img" aria-label="Diagnostic expert OSPF : partir d’une preuve observable"><rect x="0" y="0" width="1000" height="590" rx="16" fill="#0c1420"/><text x="28" y="35" fill="#edf4fb" font-size="23" font-weight="700">Diagnostic expert OSPF : partir d’une preuve observable</text><text x="28" y="60" fill="#adbdcf" font-size="13">Ne change pas la métrique au hasard : localise d’abord où disparaît l’information ou le forwarding.</text><line x1="28" y1="79" x2="972" y2="79" stroke="#34475d" stroke-width="1.5"/><rect x="340" y="105" width="320" height="66" rx="13" fill="#152235" stroke="#c4b5fd" stroke-width="2.4"/><text x="500.0" y="132" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Symptôme confirmé</text><text x="500.0" y="154" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">préfixe absent / trafic en panne</text><rect x="45" y="245" width="270" height="75" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="180.0" y="272" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">1 · Adjacence</text><text x="180.0" y="294" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">interface, Hello, MTU, auth</text><rect x="365" y="245" width="270" height="75" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="500.0" y="272" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">2 · LSDB / LSA</text><text x="500.0" y="294" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">origine, portée, séquence</text><rect x="685" y="245" width="270" height="75" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="820.0" y="272" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">3 · RIB / FIB</text><text x="820.0" y="294" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">sélection, next-hop, install</text><line x1="420" y1="171" x2="180" y2="245" stroke="#45c7f5" stroke-width="3" stroke-linecap="round"/><line x1="500" y1="171" x2="500" y2="245" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="580" y1="171" x2="820" y2="245" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><rect x="75" y="390" width="245" height="67" rx="13" fill="#152235" stroke="#45c7f5" stroke-width="2.4"/><text x="197.5" y="417" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Logs / capture</text><text x="197.5" y="439" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">OSPF proto 89, timestamps</text><rect x="378" y="390" width="245" height="67" rx="13" fill="#152235" stroke="#fbbf24" stroke-width="2.4"/><text x="500.5" y="417" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Frontières</text><text x="500.5" y="439" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Area / ABR / ASBR / filtre</text><rect x="680" y="390" width="245" height="67" rx="13" fill="#152235" stroke="#4ade80" stroke-width="2.4"/><text x="802.5" y="417" text-anchor="middle" fill="#edf4fb" font-size="16" font-weight="700">Données / applicatif</text><text x="802.5" y="439" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">retour, ACL, MTU, DNS</text><line x1="180" y1="320" x2="195" y2="390" stroke="#45c7f5" stroke-width="3" stroke-linecap="round"/><line x1="500" y1="320" x2="500" y2="390" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/><line x1="820" y1="320" x2="800" y2="390" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/><text x="500" y="495" text-anchor="middle" fill="#edf4fb" font-size="14" font-weight="700">Formuler une hypothèse, choisir un test discriminant, conserver l’état avant/après.</text><text x="500" y="520" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Collecter `show ip ospf neighbor`, `show ip ospf database`, `show ip route` et la FIB.</text><text x="500" y="545" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Une adjacence FULL et une LSA présente ne prouvent pas que la route est installée ou utilisable.</text></svg>
</div>


## 11. Laboratoires Expert

### Laboratoire 1 — Audit de stabilité d'un domaine OSPF

**But :** définir une ligne de base et repérer un domaine instable avant de toucher aux timers.

1. Collecter voisins, interfaces, LSDB, table de routage, logs et charge CPU sur les routeurs concernés.
2. Noter le nombre de changements d'adjacence pendant une période représentative.
3. Relever les LSA qui changent le plus souvent, leurs Advertising Router et les interfaces associées.
4. Corréler les changements avec la couche physique, les événements de maintenance ou les modifications de redistribution.
5. Rédiger une hypothèse et un test discriminant.

**Livrable :** tableau avant changement, courbe des événements si possible, cause probable et niveau de confiance.

### Laboratoire 2 — Calcul de chemins ECMP

1. Construire une topologie de laboratoire avec deux chemins dont le coût total est identique.
2. Vérifier les coûts d'interface effectifs et les routes installées.
3. Observer les next-hops de la RIB et, si disponible, la programmation FIB.
4. Générer plusieurs flux d'origine/destination différents et relever leur distribution.
5. Augmenter un seul coût dans la maquette, puis comparer le chemin et les flux.
6. Restaurer la configuration et vérifier qu'ECMP revient à l'état attendu.

**Questions :** la table montre-t-elle plusieurs next-hops ? La distribution de trafic est-elle équilibrée ? Les flux stateful empruntent-ils des chemins compatibles avec les équipements intermédiaires ?

### Laboratoire 3 — BFD et réaction OSPF

Sur une plate-forme qui prend en charge cette intégration :

1. valider l'adjacence OSPF et le chemin normal ;
2. valider la session BFD et ses paramètres négociés ;
3. démarrer ping continu et une transaction applicative ;
4. injecter une panne de lien dans la maquette ;
5. horodater le moment de panne, le changement BFD, la réaction OSPF et la modification du chemin ;
6. répéter avec un délai de BFD moins agressif et comparer stabilité/délai ;
7. restaurer l'état et confirmer l'absence de bascule répétitive.

**Critère de réussite :** pouvoir expliquer la contribution de chaque mécanisme et distinguer un défaut de détection d'une lenteur de programmation FIB.

### Laboratoire 4 — Fast reroute / LFA

La prise en charge est spécifique à la plate-forme ; si le simulateur ne supporte pas la fonctionnalité, effectuer le calcul théorique et documenter cette limite.

1. dessiner le graphe, les coûts et les distances vers la destination ;
2. calculer le chemin primaire et les voisins alternatifs ;
3. vérifier la condition loop-free selon le mécanisme supporté ;
4. configurer la fonction dans la maquette si disponible ;
5. lire la sortie de vérification pour confirmer la présence d'un chemin de protection ;
6. provoquer une panne ciblée et mesurer le transfert ;
7. confirmer la route après convergence complète.

Ne présente pas un chemin alternatif dessiné comme une protection installée avant que la plate-forme ne fournisse une preuve.

### Laboratoire 5 — Graceful Restart et changement de topologie

1. relever la FIB et le trafic applicatif avant le test ;
2. vérifier la capacité GR et helper sur l'ensemble des voisins nécessaires ;
3. exécuter uniquement le type de redémarrage pris en charge dans la maquette ;
4. mesurer le service pendant le restart et la ré-synchronisation ;
5. répéter avec un changement de topologie contrôlé dans le laboratoire ;
6. observer si le mécanisme gracieux est interrompu ou dégradé conformément à la fonction implémentée ;
7. documenter les cas où la continuité du forwarding n'est pas garantie.

### Laboratoire 6 — Redistribution avec tags et filtres

1. créer une route externe de test provenant d'un domaine contrôlé ;
2. appliquer une allow-list pour les préfixes approuvés ;
3. configurer le tag de provenance selon l'OS et le protocole concernés ;
4. vérifier la LSA et la route externe ;
5. simuler un chemin de retour vers la frontière pour s'assurer que la politique empêche la ré-injection ;
6. tenter un préfixe non autorisé et vérifier qu'il reste bloqué ;
7. supprimer l'annonce de test puis valider que la route se retire comme attendu.

### Laboratoire 7 — Rotation d'authentification

Uniquement dans une maquette où les deux côtés des adjacences sont contrôlés.

1. relever les algorithmes et paramètres actuels sans exporter les secrets ;
2. valider le plan de compatibilité et le rollback ;
3. déployer selon la méthode de chevauchement prise en charge par la plate-forme ;
4. surveiller les voisinages, logs et compteurs ;
5. vérifier toutes les interfaces participantes ;
6. terminer la rotation et confirmer que les anciens secrets ne sont plus en usage, selon la politique ;
7. archiver une preuve expurgée de secrets.

### Laboratoire 8 — Diagnostic d'une route absente en multi-aires

Scénario : les voisins de toutes les aires sont `FULL`, mais un sous-réseau distant n'est pas joignable.

1. identifier un préfixe précis et son routeur d'origine ;
2. vérifier la route connectée ou externe sur la source ;
3. contrôler la LSA d'origine dans l'aire source ;
4. vérifier ce que l'ABR doit annoncer et la présence du Type 3/5/7 attendu dans l'aire destinataire ;
5. examiner le type d'aire, les filtres, les résumés et la politique de redistribution ;
6. vérifier la RIB, le next-hop et la FIB ;
7. tester le retour et l'application ;
8. formuler la cause à partir de preuves, corriger une seule variable puis répéter.

### Laboratoire 9 — Plan de changement contrôlé

Préparer un changement de coût ou de résumé d'aire qui influence au moins deux destinations : topologie avant/après, routes attendues, évaluation de l'impact, commandes de vérification, fenêtre, approbation, retour arrière, tests applicatifs et critères d'abandon. Le changement doit être révisable par une autre personne avant exécution.


## 12. Étude de cas : plusieurs symptômes, une seule cause racine

### Situation

Après une modification de coût sur un lien inter-aires, certains utilisateurs ne joignent plus un sous-réseau ; le voisinage de tous les routeurs reste `FULL`. Le CPU du routeur de frontière est plus élevé qu'avant. Une équipe propose de réduire les timers Hello/Dead.

### Méthode d'enquête

1. **Vérifier le périmètre :** un seul préfixe, une seule aire ou plusieurs destinations ?
2. **Comparer l'état initial :** sauvegarder les sorties de route et LSDB avant d'effectuer d'autres changements.
3. **Vérifier la route d'origine :** le préfixe existe-t-il encore et est-il appris par la source attendue ?
4. **Inspecter la frontière :** la LSA inter-aire ou externe attendue est-elle annoncée et reçue ?
5. **Comparer RIB/FIB :** la route est-elle installée, quel next-hop est retenu et est-il joignable ?
6. **Examiner le coût modifié :** a-t-il déplacé le trafic vers un chemin qui ne possède pas de route retour ou une politique similaire ?
7. **Corréler la charge CPU :** la hausse est-elle associée à SPF, à une flood de LSA ou à un événement indépendant ?
8. **Test discriminant :** vérifier une transaction dans les deux sens en observant le chemin aller et retour.
9. **Corriger ciblément :** rétablir le coût ou corriger la cause confirmée, pas changer les timers par intuition.
10. **Prouver le rétablissement :** routes attendues, stabilité, application et capacité après changement.

### Conclusion attendue

Le fait que les voisins restent `FULL` écarte certaines causes d'adjacence, mais n'exclut ni une LSA manquante, ni une route non installée, ni un changement de next-hop, ni une panne de retour. Le diagnostic doit localiser l'étape où le préfixe ou le flux cesse d'être disponible. La hausse CPU est un indice à corréler, pas une preuve de la cause.


## 13. Évaluation Expert avec corrigés

### Questions

1. Pourquoi faut-il séparer LSDB, RIB et FIB dans le diagnostic ?
2. Une LSA Type 3 présente dans l'aire de destination garantit-elle la route installée ?
3. Pourquoi un domaine avec peu de routeurs peut-il être instable ?
4. Quelle est la différence entre ECMP théorique et chemins effectivement installés ?
5. Pourquoi une distribution de flux déséquilibrée ne prouve-t-elle pas un défaut OSPF ?
6. Quel est le rôle de BFD par rapport à OSPF ?
7. Quels risques apportent des timers BFD trop agressifs ?
8. Pourquoi un LFA candidat n'est-il pas automatiquement une protection garantie ?
9. Dans quelles conditions Graceful Restart peut-il être interrompu ?
10. Pourquoi la redistribution bidirectionnelle doit-elle être filtrée ?
11. Comment un tag aide-t-il à éviter les boucles et quelles sont ses limites ?
12. Quelle différence pratique existe entre une route externe E1 et E2 ?
13. Pourquoi doit-on prévoir un chevauchement de clés seulement si la plate-forme le prend en charge ?
14. Quels éléments prouveraient qu'un problème est dans la FIB plutôt que dans l'adjacence ?
15. Pourquoi une modification de résumé exige-t-elle un plan de préfixes ?
16. Pourquoi une LSA en forte variation ne prouve-t-elle pas à elle seule une attaque ?
17. Quelles métriques faut-il relever pour mesurer le temps de convergence réel ?
18. Pourquoi OSPFv3 ne doit-il pas être traité comme un simple remplacement du processus OSPFv2 ?
19. À quoi sert de corréler les journaux et captures sur plusieurs routeurs ?
20. Quels éléments sont obligatoires dans un changement expert de métrique ou d'aire ?

### Corrigés

**1.** La LSDB décrit la topologie connue ; la RIB contient les routes sélectionnées ; la FIB est utilisée pour transférer les paquets. Une erreur peut être localisée à un étage précis.

**2.** Non. La route peut être rejetée par la sélection de route, avoir un prochain saut non valide, être supplantée par une autre source ou ne pas être programmée comme prévu.

**3.** La fréquence et la corrélation des événements sont parfois plus déterminantes que le nombre de nœuds : une liaison instable ou une redistribution en boucle peut déclencher des changements répétés.

**4.** La théorie identifie des chemins dont la métrique est égale ; l'installation dépend aussi de la validité des next-hops, des paramètres et des capacités de la plate-forme.

**5.** Un hachage de flux peut concentrer peu de flux sur le même membre. OSPF choisit les next-hops ; la distribution effective dépend également du forwarding.

**6.** BFD détecte rapidement certaines défaillances de chemin ; OSPF prend ensuite les actions de routage selon son intégration avec BFD.

**7.** Des pertes ou retards temporaires du contrôle peuvent être pris pour une panne réelle, provoquant flapping, recalculs et pertes supplémentaires.

**8.** Le candidat doit satisfaire les conditions de boucle, être pris en charge et être installé/programmé par l'équipement. Une ligne sur un diagramme n'est pas une preuve.

**9.** Si la topologie change pendant la période de restart ou si les conditions de coopération et de forwarding ne sont plus satisfaites, le mécanisme doit suivre les règles de protection de l'implémentation et peut revenir à une convergence normale.

**10.** Sans filtres, le préfixe injecté dans un domaine peut être réannoncé vers son domaine d'origine, entraînant boucles, préférence inattendue ou instabilité.

**11.** Un tag peut marquer la provenance ; un filtre doit utiliser ce tag correctement à la frontière de retour. Sans application de politique, le tag n'a aucun effet protecteur automatique.

**12.** E1 additionne le coût interne vers l'ASBR et la métrique externe ; E2 compare principalement la métrique externe, le coût interne pouvant départager des métriques externes égales.

**13.** Les mécanismes de clés et les possibilités de chevauchement sont dépendants du logiciel. Une procédure conçue pour une plate-forme ne peut pas être copiée aveuglément sur une autre.

**14.** Un voisinage stable et une LSDB correcte avec une route attendue dans la RIB mais absente ou non résolue dans le forwarding peuvent orienter vers le plan de transfert. Il faut utiliser les commandes de FIB et des tests de prochain saut propres à la plateforme.

**15.** Un résumé représente un ensemble de préfixes. Sans plan hiérarchique, il peut couvrir des destinations absentes et attirer le trafic vers une frontière qui ne peut pas les acheminer.

**16.** Les LSA peuvent changer à cause de liens instables, de modifications légitimes ou de problèmes de redistribution. Il faut corréler l'origine, le temps, les séquences et les événements avant d'inférer une attaque.

**17.** Temps de détection, réaction OSPF, flooding, SPF, installation RIB/FIB, perte de paquets et retour du service applicatif.

**18.** Le contexte de configuration, les familles d'adresses, le support logiciel et les mécanismes diffèrent ; il faut vérifier les capacités et les routes de chaque famille séparément.

**19.** Cela reconstruit une chronologie, révèle où un paquet ou une annonce disparaît et permet de distinguer l'événement initial des effets secondaires.

**20.** État initial, impact, topologie, route/LSA attendue, fenêtre approuvée, changement atomique, mesures, critères de réussite et d'abandon, retour arrière et preuves conservées.


## 14. Runbook Expert : avant, pendant, après

### Avant

- [ ] sauvegarder la configuration et les sorties de commandes pertinentes ;
- [ ] inventorier les versions, Router ID, aires, interfaces, voisins et types d'authentification ;
- [ ] dessiner la topologie réelle, pas seulement la topologie logique supposée ;
- [ ] énumérer les LSA et routes attendues avant et après changement ;
- [ ] analyser les routes concurrentes, les chemins retour, les filtres et les résumés ;
- [ ] fixer les tests applicatifs, les seuils et les personnes chargées de l'observation ;
- [ ] valider les commandes et le rollback sur une maquette représentative.

### Pendant

- [ ] effectuer une seule modification principale à la fois ;
- [ ] horodater les événements et collecter la sortie avant qu'elle ne change ;
- [ ] surveiller les adjacences, LSA, SPF, RIB/FIB et la charge ;
- [ ] interrompre le changement si les critères d'abandon sont atteints ;
- [ ] ne pas élargir la redistribution ni neutraliser l'authentification pour résoudre temporairement un symptôme.

### Après

- [ ] confirmer les routes et next-hops attendus sur les routeurs concernés ;
- [ ] tester le chemin aller et le chemin retour depuis le point d'usage ;
- [ ] confirmer la stabilité pendant une période définie ;
- [ ] vérifier la supervision, les logs et les alarmes ;
- [ ] mettre à jour le diagramme, l'inventaire, les coûts et les runbooks ;
- [ ] conserver les preuves et les enseignements pour réduire la récurrence.


## 15. Glossaire de niveau Expert

| Terme | Définition opérationnelle |
|---|---|
| ABR | Routeur OSPF attaché à plusieurs aires et réalisant les fonctions inter-aires attendues |
| ASBR | Routeur qui introduit dans OSPF des routes issues d'une autre source |
| BFD | Mécanisme de détection rapide de défaut de chemin, utilisé en intégration avec les protocoles de routage |
| ECMP | Installation de plusieurs next-hops de coût égal lorsque les conditions sont réunies |
| FIB | Base utilisée par le plan de transfert pour choisir le prochain saut |
| Graceful Restart | Mécanisme permettant, sous conditions, de conserver le forwarding pendant le redémarrage du contrôle |
| LFA | Loop-Free Alternate, candidat de secours satisfaisant une condition de prévention de boucle |
| LSA / LSDB | Annonce d'état de liens / base d'état de liens connue dans la portée concernée |
| RIB | Base de routes installées ou sélectionnées par le système de routage |
| SPF | Calcul de plus court chemin à partir de la LSDB |
| Redistribution | Injection de routes d'une source ou d'un protocole dans un autre |
| Tag de route | Métadonnée utilisée par une politique de routage pour identifier la provenance d'une route |
| Convergence | Transition vers un état de routage et de forwarding cohérent après un changement |


## 16. Références techniques

Les RFC décrivent les standards et leurs extensions ; la documentation correspondant au système, au modèle et à la version est indispensable pour appliquer les commandes.

- **RFC 2328 — OSPF Version 2** : https://www.rfc-editor.org/rfc/rfc2328.html
- **RFC 5709 — OSPFv2 HMAC-SHA Cryptographic Authentication** : https://www.rfc-editor.org/rfc/rfc5709.html
- **RFC 7474 — Security Extension for OSPFv2 When Using Manual Key Management** : https://www.rfc-editor.org/rfc/rfc7474.html
- **RFC 3623 — Graceful OSPF Restart** : https://www.rfc-editor.org/rfc/rfc3623.html
- **RFC 5880 — Bidirectional Forwarding Detection (BFD)** : https://www.rfc-editor.org/rfc/rfc5880.html
- **RFC 9355 — OSPF Bidirectional Forwarding Detection (BFD) Strict-Mode** : https://www.rfc-editor.org/rfc/rfc9355.html
- **RFC 5838 — Support of Address Families in OSPFv3** : https://www.rfc-editor.org/rfc/rfc5838.html
- **Cisco — OSPF Prefix Suppression** : https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/213404-open-shortest-path-first-prefix-suppress.html
- **Cisco — OSPF Configuration Guide, IOS XE** : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr3-fwd/ospf/ospf-configuration-guide/ospf.html

La RFC 2328 a reçu des mises à jour et extensions ; lire seulement le texte de base ne suffit donc pas pour les fonctions modernes ou les questions de sécurité. Par exemple, RFC 5709 traite l'authentification cryptographique HMAC-SHA et RFC 7474 l'actualise pour la gestion manuelle de clés ; la prise en charge effective doit être vérifiée sur le matériel et le logiciel ciblés.

## Conclusion

Le niveau Expert n'est pas une liste de commandes plus longues. Il demande de relier topologie, portée des LSA, décision de route, programmation de la FIB, sécurité et comportement applicatif. Les schémas du cours doivent servir à formuler des hypothèses vérifiables, pas à remplacer la lecture des sorties réelles. Une modification est maîtrisée lorsqu'on sait ce qui changera, ce qui prouvera la réussite, ce qui provoquera l'arrêt et comment revenir à l'état précédent.
