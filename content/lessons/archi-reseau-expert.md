# Architecture Réseau — Niveau Expert

> **Parcours :** Réseaux informatiques · **Niveau :** Expert · **Fichier :** `archi-reseau-expert.md`  
> **Public :** architectes réseau, ingénieurs expérimentés, responsables infrastructure et candidats préparant des fonctions de conception avancée.  
> **Prérequis :** maîtriser les bases de l’architecture campus et les décisions d’ingénierie du niveau intermédiaire : VLAN/VRF, adressage IPv4/IPv6, routage dynamique, haute disponibilité, sécurité, supervision et exploitation.  
> **Objectif :** transformer les compétences de conception en une architecture multi-domaines, évolutive, résiliente, sécurisée, mesurable et exploitable, en documentant les compromis et les critères d’acceptation.

## Place dans le parcours

Le niveau débutant apprend à reconnaître les composants et à dessiner un réseau simple. Le niveau intermédiaire enseigne à assembler ces composants de manière cohérente dans un réseau d’entreprise de taille moyenne. **Le niveau expert porte sur les décisions à l’échelle** : frontières de panne, modèles de routage, underlay/overlay, services multi-sites, politique de sécurité, convergence, observabilité, migration et gouvernance. Le but n’est pas d’empiler les technologies les plus complexes, mais de choisir une solution qui satisfait des exigences mesurables et qu’une équipe peut réellement exploiter.

## Objectifs pédagogiques

À la fin du parcours, tu devrais être capable de :

- Traduire les besoins métier en exigences réseau vérifiables, SLO, budgets de panne et critères d’acceptation.
- Construire une architecture logique et physique couvrant campus, datacenter, WAN, cloud, sécurité et gestion.
- Choisir entre accès routé, architecture campus hiérarchique, EVPN-VXLAN, VPN MPLS, SD-WAN et routage classique selon les besoins.
- Analyser les plans de contrôle, de données et de gestion comme des systèmes distincts mais liés.
- Concevoir une résilience de bout en bout en traitant les risques partagés et les dépendances cachées.
- Définir des politiques BGP, des frontières de routage et des règles de segmentation testables.
- Concevoir l’observabilité pour confirmer ou réfuter des hypothèses de panne, et non seulement collecter des métriques.
- Préparer une migration brownfield avec pilote, fenêtre, rollback et critères d’arrêt.
- Rédiger des décisions d’architecture (ADR), schémas de référence et runbooks compréhensibles par l’équipe d’exploitation.

## Comment travailler avec ce document

Les schémas SVG sont intégrés directement à ce fichier Markdown, chacun sur une seule ligne et sans feuille CSS, marqueur externe, dégradé ni référence à un identifiant SVG. Cela vise à limiter les problèmes de rendu dans certains lecteurs Markdown. Si le lecteur ne rend pas les images SVG en ligne, vérifie sa prise en charge du SVG inline ou ouvre le fichier dans un navigateur compatible. Les commandes et syntaxes CLI sont des exemples de conception : elles ne constituent pas un bloc de configuration universel. Les fonctions disponibles varient selon le fournisseur, le modèle, la licence et la version logicielle.


## 1. Concevoir à partir des exigences, pas à partir des équipements

Un diagramme réseau ne doit pas être le point de départ unique. La première étape consiste à comprendre ce que le réseau doit permettre, quelles conséquences auraient une interruption et quelles contraintes sont non négociables. Deux environnements contenant les mêmes routeurs et commutateurs peuvent nécessiter des architectures différentes si leurs profils de risque et leurs objectifs de service diffèrent.

### 1.1 Convertir les besoins métier en exigences techniques

| Besoin métier | Traduction réseau à clarifier | Preuve attendue |
|---|---|---|
| Application de paiement disponible | Chemins indépendants, dépendances DNS/identité, bascule validée | Test de perte de lien et mesure d’interruption |
| Voix et visioconférence stables | Latence, gigue, pertes, QoS de bout en bout | Mesures par classe et test en congestion |
| Environnements séparés | VRF, politiques inter-zones, règles d’exception explicites | Tests autorisé/refusé entre zones |
| Déploiement cloud fréquent | Modèle d’adressage, connectivité hybride, automatisation | Test de provisionnement et de retrait |
| Traçabilité opérationnelle | Logs centralisés, horodatage cohérent, flux et télémétrie | Incident reconstituable à partir de preuves |
| Expansion multi-sites | Modèle WAN répétable, allocation IP, résilience et coûts | Onboarding d’un site pilote reproductible |

Évite des exigences comme « le réseau doit être rapide » ou « il faut de la redondance ». Il faut préciser le service, la période de mesure et la limite acceptable. Une exigence de disponibilité doit définir ce qui compte comme indisponibilité, le périmètre observé, la fenêtre temporelle et les dépendances incluses. Un lien secondaire n’est pas la preuve que le service peut fonctionner après la panne du lien primaire.

### 1.2 SLI, SLO, SLA et budget d’erreur

- **SLI (Service Level Indicator)** : mesure observée, par exemple le pourcentage de requêtes réussies, le RTT, la perte ou le temps de convergence.
- **SLO (Service Level Objective)** : cible interne mesurable pour le SLI.
- **SLA (Service Level Agreement)** : engagement formel, souvent contractuel, comportant un périmètre et des conséquences.
- **Budget d’erreur** : portion de dégradation disponible avant que le SLO soit dépassé. Il sert à arbitrer entre changements, fiabilité et vitesse de livraison.

Ne déduis pas un SLO applicatif d’une simple disponibilité d’interface. Une interface peut rester « up » tandis qu’un trajet est asymétrique, que le DNS est indisponible ou que la capacité du pare-feu est épuisée. Mesure les résultats vécus par le service et garde des indicateurs techniques pour expliquer les écarts.

### 1.3 Exemple de fiche d’exigences

| Élément | Exemple à adapter |
|---|---|
| Service critique | ERP hébergé au datacenter et dans le cloud |
| Population | 1 200 utilisateurs, 3 sites, postes et mobiles |
| Disponibilité cible | Définie par le propriétaire de service sur une période explicite |
| Temps de rétablissement | RTO validé par le métier ; testé en scénario de panne |
| Capacité | Charge nominale et scénario de pointe, avec croissance annuelle |
| Sécurité | Flux permis entre zones, administration séparée, journalisation |
| Dépendances | DNS, identité, PKI, NTP, pare-feu, opérateur, cloud |
| Preuves | Télémétrie, test synthétique, logs horodatés, test de bascule |

### 1.4 Schéma de référence multi-domaines


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="480" viewBox="0 0 1120 480"><rect x="0" y="0" width="1120" height="480" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Architecture de référence multi-domaines</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">Chaque domaine a un rôle, des frontières de panne et des politiques propres</text><rect x="35" y="105" width="180" height="78" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="125.0" y="138.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Utilisateurs</text><text x="125.0" y="159.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">LAN / Wi-Fi</text><rect x="260" y="105" width="190" height="78" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="355.0" y="138.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Campus</text><text x="355.0" y="159.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Accès routé / L3</text><rect x="500" y="105" width="180" height="78" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="590.0" y="138.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Cœur IP</text><text x="590.0" y="159.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">ECMP / IGP</text><rect x="730" y="105" width="165" height="78" rx="12" fill="#4c1d95" stroke="#c4b5fd" stroke-width="2"/><text x="812.5" y="138.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">WAN Edge</text><text x="812.5" y="159.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">BGP / SD-WAN</text><rect x="935" y="105" width="150" height="78" rx="12" fill="#713f12" stroke="#fbbf24" stroke-width="2"/><text x="1010.0" y="138.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Cloud / SaaS</text><text x="1010.0" y="159.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Internet</text><line x1="215" y1="144" x2="260" y2="144" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="260,144 248.0,150.0 248.0,138.0" fill="#8fb8e8"/><line x1="450" y1="144" x2="500" y2="144" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="500,144 488.0,150.0 488.0,138.0" fill="#8fb8e8"/><line x1="680" y1="144" x2="730" y2="144" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="730,144 718.0,150.0 718.0,138.0" fill="#8fb8e8"/><line x1="895" y1="144" x2="935" y2="144" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="935,144 923.0,150.0 923.0,138.0" fill="#8fb8e8"/><rect x="220" y="260" width="210" height="82" rx="12" fill="#4b1d34" stroke="#f9a8d4" stroke-width="2"/><text x="325.0" y="295.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Sécurité</text><text x="325.0" y="316.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Zones / politique</text><rect x="500" y="260" width="210" height="82" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="605.0" y="295.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Services partagés</text><text x="605.0" y="316.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">DNS / DHCP / NTP</text><rect x="785" y="260" width="210" height="82" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="890.0" y="295.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Observabilité</text><text x="890.0" y="316.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Logs / Flow / SLA</text><line x1="320" y1="183" x2="320" y2="260" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="320,260 314.0,248.0 326.0,248.0" fill="#8fb8e8"/><text x="320.0" y="213.5" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">contrôle</text><line x1="590" y1="183" x2="590" y2="260" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="590,260 584.0,248.0 596.0,248.0" fill="#8fb8e8"/><text x="590.0" y="213.5" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">services</text><line x1="812" y1="183" x2="875" y2="260" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="875,260 862.7574027216929,254.51193915110372 872.0448903121328,246.91308566801655" fill="#8fb8e8"/><text x="843.5" y="213.5" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">mesure</text><text x="560" y="405" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#e2e8f0">Plan de données : paquets       |       Plan de contrôle : routes       |       Plan de gestion : configuration et télémétrie</text></svg>


**Lecture :** chaque domaine a des responsabilités et des limites. L’architecture est plus simple à comprendre lorsqu’on identifie clairement le point de sortie du campus, la frontière de sécurité, le WAN edge, les services partagés et la plateforme d’observabilité. Les boîtes ne représentent pas nécessairement des équipements physiques distincts : elles représentent d’abord des rôles logiques. Une plateforme peut héberger plusieurs rôles, mais cette colocalisation doit être évaluée selon la capacité, la sécurité et les conséquences de panne.


## 2. Les trois plans : contrôle, données et gestion

Une architecture experte doit éviter de mélanger l’état du protocole, la sélection de route, le transfert matériel et l’opération du réseau.

### 2.1 Plan de contrôle

Le plan de contrôle construit l’information nécessaire à la décision de forwarding. Un IGP découvre les voisins et diffuse la topologie selon son mécanisme. BGP échange des routes en appliquant les attributs et politiques. Les protocoles de redondance de passerelle élisent ou coordonnent le rôle actif selon leurs mécanismes. Une session établie ne prouve cependant pas que toutes les routes attendues ont été acceptées.

### 2.2 RIB et FIB

La RIB est l’ensemble des routes candidates et des informations de routage maintenues par le système. La décision de sélection tient compte du protocole, des préférences administratives propres à la plateforme, des attributs et de la politique. La FIB est la structure utilisée pour transférer réellement les paquets, souvent programmée dans du matériel spécialisé. Des limites de table, un next-hop non résolu ou un problème de programmation matérielle peuvent créer un écart entre la route calculée et le forwarding.

### 2.3 Plan de gestion

Le plan de gestion transporte les accès administratifs, la configuration, les journaux, les sauvegardes et la télémétrie. Il doit être protégé contre les utilisateurs et les flux non autorisés. Une panne de management ne devrait pas automatiquement interrompre le forwarding, mais elle peut empêcher le diagnostic et rendre les modifications risquées. Prévois une voie d’accès hors bande pour les systèmes critiques lorsque le risque et le coût le justifient.


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="500" viewBox="0 0 1120 500"><rect x="0" y="0" width="1120" height="500" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Séparer plan de contrôle et plan de données</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">Une route installée est un résultat ; le forwarding matériel est une autre étape à vérifier</text><rect x="65" y="105" width="260" height="90" rx="12" fill="#4c1d95" stroke="#c4b5fd" stroke-width="2"/><text x="195.0" y="144.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">Protocoles de contrôle</text><text x="195.0" y="166.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">OSPF / IS-IS / BGP</text><rect x="430" y="105" width="260" height="90" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="560.0" y="144.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">RIB</text><text x="560.0" y="166.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">Choix des meilleures routes</text><rect x="795" y="105" width="260" height="90" rx="12" fill="#713f12" stroke="#fbbf24" stroke-width="2"/><text x="925.0" y="144.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">FIB / ASIC</text><text x="925.0" y="166.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">Next-hop et actions de forwarding</text><line x1="325" y1="150" x2="430" y2="150" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="430,150 418.0,156.0 418.0,144.0" fill="#8fb8e8"/><text x="377.5" y="142.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">calcule</text><line x1="690" y1="150" x2="795" y2="150" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="795,150 783.0,156.0 783.0,144.0" fill="#8fb8e8"/><text x="742.5" y="142.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">programme</text><rect x="100" y="300" width="250" height="75" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="225.0" y="332.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Télémetrie de contrôle</text><text x="225.0" y="353.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">voisinages · routes</text><rect x="435" y="300" width="250" height="75" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="560.0" y="332.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Télémetrie de transfert</text><text x="560.0" y="353.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">FIB · drops · erreurs</text><rect x="770" y="300" width="250" height="75" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="895.0" y="332.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Test réel</text><text x="895.0" y="353.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">ping · traceroute · SLA</text><line x1="220" y1="195" x2="225" y2="300" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="225,300 218.43600938066797,288.2989732437994 230.42242703336123,287.72819145081405" fill="#8fb8e8"/><line x1="560" y1="195" x2="560" y2="300" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,300 554.0,288.0 566.0,288.0" fill="#8fb8e8"/><line x1="920" y1="195" x2="895" y2="300" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="895,300 891.9426090395604,286.9366022599393 903.6162836157847,289.71604858761185" fill="#8fb8e8"/><text x="560" y="445" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#fca5a5">Un voisinage UP ne prouve ni l’installation de la route, ni son bon transfert, ni la santé de l’application.</text></svg>


### 2.4 La méthode de diagnostic à trois preuves

Pour chaque panne, recueille au moins trois niveaux de preuve :

1. **Contrôle** : voisinages, LSDB/BGP RIB, politique appliquée et route choisie.
2. **Transfert** : FIB, résolution ARP/ND, compteurs de drops, MTU, ACL et next-hop réel.
3. **Service** : test synthétique de l’application, résolution DNS, RTT, perte et code d’erreur.

Si le ping vers la passerelle réussit mais que l’application échoue, ne conclus pas immédiatement que le WAN est la cause. Le problème peut être dans le DNS, le routage retour, le pare-feu, le proxy, le TLS ou l’application elle-même. La démarche consiste à former une hypothèse, choisir un test qui la différencie d’autres causes, puis conserver la preuve.


## 3. Délimiter les domaines de panne

La redondance se conçoit au niveau de la dépendance réellement critique, pas uniquement par le nombre de ports ou de boîtiers. Deux liens vers le même commutateur, deux opérateurs utilisant le même conduit ou deux instances dépendantes du même plan de contrôle ne procurent pas une indépendance complète.

### 3.1 Identifier les risques partagés

Un **SRLG (Shared Risk Link Group)** regroupe des ressources qui peuvent tomber en panne ensemble. Exemples : fibres dans la même gaine, circuits passant par la même chambre, alimentation partagée, même bâtiment, même fournisseur d’accès ou même système d’orchestration. Une conception peut paraître redondante sur un schéma logique tout en restant exposée au même événement physique.

### 3.2 Construire une matrice de panne

| Événement | Détection | Réponse attendue | Preuve de succès |
|---|---|---|---|
| Perte d’un lien d’accès | État interface / BFD si adapté | Retrait du chemin ou convergence | Trafic servi par un autre chemin |
| Perte d’un switch de distribution | Voisinage L3 / état du pair | ECMP ou re-convergence | Routes et application disponibles |
| Perte d’un circuit WAN | BFD, IP SLA ou mécanisme opérateur | Bascule vers lien alternatif | Trafic sort par le lien sain |
| Perte d’un DNS | Tests synthétiques sur résolveurs | Résolveur secondaire / cache | Noms critiques résolus |
| Perte du système de management | Heartbeat de gestion | Accès hors bande | Contrôle d’accès de secours opérationnel |
| Erreur de changement | Diff de configuration / alerte | Rollback validé | Retour à la baseline connue |

### 3.3 Redondance physique et logique

La redondance physique concerne les chemins, équipements, alimentations, fibres et locaux. La redondance logique concerne les routes, sessions, politiques, instances et capacités à conserver un service. Une bascule de protocole rapide peut toujours envoyer du trafic vers un équipement sain mais saturé. La capacité résiduelle doit donc être validée après une perte majeure, pas seulement pendant la charge nominale.


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="520" viewBox="0 0 1120 520"><rect x="0" y="0" width="1120" height="520" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Redondance utile : chemins réellement indépendants</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">Deux liens ne donnent pas une haute disponibilité si les risques restent communs</text><rect x="420" y="80" width="280" height="70" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="560.0" y="109.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">Service critique</text><text x="560.0" y="131.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">SLA + objectif RTO/RPO</text><rect x="120" y="225" width="300" height="78" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="270.0" y="258.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Chemin A</text><text x="270.0" y="279.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Fibre / conduit A · énergie A</text><rect x="700" y="225" width="300" height="78" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="850.0" y="258.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Chemin B</text><text x="850.0" y="279.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Fibre / conduit B · énergie B</text><line x1="490" y1="150" x2="330" y2="225" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="330,225 338.31890397412207,214.47403986947816 343.41211048889073,225.33954710098456" fill="#8fb8e8"/><line x1="630" y1="150" x2="850" y2="225" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="850,225 836.7058341751288,226.8069739956136 840.5779213085864,215.4488517374711" fill="#8fb8e8"/><rect x="100" y="370" width="340" height="72" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="270.0" y="400.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Domaine de panne A</text><text x="270.0" y="421.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">routeur, alimentation, conduit</text><rect x="680" y="370" width="340" height="72" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="850.0" y="400.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Domaine de panne B</text><text x="850.0" y="421.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">autre POP / autre fournisseur</text><line x1="270" y1="303" x2="270" y2="370" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="270,370 264.0,358.0 276.0,358.0" fill="#8fb8e8"/><line x1="850" y1="303" x2="850" y2="370" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="850,370 844.0,358.0 856.0,358.0" fill="#8fb8e8"/><text x="560" y="477" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#fbbf24">Vérifier les risques partagés : SRLG, même chambre, même bâtiment, même plan de contrôle.</text></svg>


### 3.4 Définir les budgets de convergence

La convergence comprend plusieurs durées : détection, propagation de l’événement, recalcul, programmation FIB, résolution éventuelle du voisin, retransmission applicative et reprise des sessions. Un mécanisme BFD peut réduire le délai de détection mais ne garantit pas à lui seul une convergence applicative donnée. Les minuteries doivent être cohérentes avec la qualité du lien, la charge processeur, les pertes possibles et les capacités des équipements.

Évite de régler arbitrairement toutes les minuteries au minimum. Des timers trop agressifs peuvent déclencher des bascules répétées, consommer des ressources ou produire des instabilités lors de congestion. La cible doit être mesurée par des tests de panne représentatifs et dans les deux sens lorsque les chemins sont asymétriques.


## 4. Campus expert : routé, hiérarchique et à domaines maîtrisés

Il n’existe pas une seule topologie idéale pour tous les campus. Le choix entre un accès L2 étendu, une architecture traditionnelle à couches et un accès routé dépend de la mobilité, de la taille des domaines de broadcast, des fonctions des équipements, du personnel disponible et des contraintes d’exploitation.

### 4.1 Accès routé

Dans un modèle d’accès routé, les frontières L3 sont rapprochées de l’accès. Les liens montants peuvent utiliser ECMP et le protocole de routage calcule des chemins alternatifs. Cette approche peut réduire la dépendance à un grand domaine STP et rendre les chemins plus visibles dans le routage. Elle demande toutefois un plan d’adressage discipliné, une gestion rigoureuse de la mobilité des terminaux et une compatibilité avec les services qui exigent une continuité L2.


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="500" viewBox="0 0 1120 500"><rect x="0" y="0" width="1120" height="500" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Campus à accès routé</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">Limiter les domaines L2 et faire converger le routage jusqu’à l’accès</text><rect x="380" y="85" width="360" height="68" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="560.0" y="113.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">Cœur L3 redondant</text><text x="560.0" y="135.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">ECMP · IGP · liens point-à-point</text><rect x="100" y="225" width="270" height="76" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="235.0" y="257.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Bloc d’accès A</text><text x="235.0" y="278.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">SVI local / sous-réseaux</text><rect x="425" y="225" width="270" height="76" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="560.0" y="257.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Bloc d’accès B</text><text x="560.0" y="278.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">SVI local / sous-réseaux</text><rect x="750" y="225" width="270" height="76" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="885.0" y="257.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Bloc d’accès C</text><text x="885.0" y="278.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">SVI local / sous-réseaux</text><line x1="460" y1="153" x2="235" y2="225" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="235,225 244.60043540376918,215.62814639155866 248.25774412901458,227.05723615795054" fill="#8fb8e8"/><text x="347.5" y="181.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">L3</text><line x1="560" y1="153" x2="560" y2="225" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,225 554.0,213.0 566.0,213.0" fill="#8fb8e8"/><text x="560.0" y="181.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">L3</text><line x1="660" y1="153" x2="885" y2="225" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="885,225 871.7422558709853,227.05723615795054 875.3995645962308,215.62814639155866" fill="#8fb8e8"/><text x="772.5" y="181.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">L3</text><rect x="100" y="360" width="270" height="65" rx="12" fill="#26374f" stroke="#93c5fd" stroke-width="2"/><text x="235.0" y="397.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Clients / AP / VoIP</text><rect x="425" y="360" width="270" height="65" rx="12" fill="#26374f" stroke="#93c5fd" stroke-width="2"/><text x="560.0" y="397.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Serveurs locaux</text><rect x="750" y="360" width="270" height="65" rx="12" fill="#26374f" stroke="#93c5fd" stroke-width="2"/><text x="885.0" y="397.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">IoT / imprimantes</text><line x1="235" y1="301" x2="235" y2="360" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="235,360 229.0,348.0 241.0,348.0" fill="#8fb8e8"/><line x1="560" y1="301" x2="560" y2="360" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,360 554.0,348.0 566.0,348.0" fill="#8fb8e8"/><line x1="885" y1="301" x2="885" y2="360" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="885,360 879.0,348.0 891.0,348.0" fill="#8fb8e8"/><text x="560" y="466" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#cbd5e1">Avantages : convergence plus prévisible, chemins ECMP actifs, panne L2 contenue.</text></svg>


### 4.2 Quand garder du L2

Certaines fonctions peuvent exiger un domaine L2 : certaines solutions de virtualisation, clusters hérités, protocoles non routables, ou contraintes opérationnelles spécifiques. Cela ne signifie pas qu’il faut étendre chaque VLAN sur tout le campus. Le domaine L2 doit être aussi petit que raisonnablement possible, documenté et protégé contre les boucles, les tempêtes de broadcast et les erreurs de câblage.

Avant d’étendre un VLAN, documente : le motif, les frontières exactes, les chemins actifs et de secours, les contrôles de boucle, la capacité de broadcast, les conséquences d’une panne et la date de réexamen. Tout VLAN étendu doit avoir un propriétaire applicatif et une exigence qui justifie son existence.

### 4.3 Routage et ECMP

ECMP permet d’utiliser plusieurs next-hops de coût équivalent. C’est utile pour répartir le trafic et activer plusieurs liens, mais le comportement exact dépend de l’algorithme de hachage, des champs disponibles et de la plateforme. Des flux volumineux peuvent créer un déséquilibre même si le nombre de flux est réparti. Lors d’un changement de topologie, le hachage peut également déplacer des conversations et produire une charge différente sur les liens restants.

La validation devrait inclure :

- le nombre de next-hops réellement installés dans la FIB ;
- la répartition de charge observée par lien ;
- le comportement à la perte d’un chemin ;
- la capacité restante après la perte la plus importante considérée ;
- les effets du routage asymétrique sur les pare-feu stateful et la visibilité.

### 4.4 Multicast, IPv6 et services de campus

Les architectures qui utilisent multicast doivent concevoir explicitement IGMP/MLD, PIM ou les mécanismes de distribution adaptés à la plateforme. L’existence d’un routage unicast fonctionnel ne prouve pas que le multicast est correctement construit. IPv6 doit être traité comme une famille de services à part entière : plan d’adressage, routage, filtrage, Neighbor Discovery, RA Guard et télémétrie spécifique. N’active pas IPv6 sans gouvernance en supposant que l’absence d’adresses IPv4 visibles signifie l’absence de chemins alternatifs.


## 5. Underlay et overlay : définir la couche de transport et le service

L’underlay constitue l’infrastructure IP physique ou logique utilisée pour transporter le trafic encapsulé. L’overlay crée des services logiques au-dessus de cette infrastructure : segments, tenants, VRF, mobilité de machines ou politiques inter-sites. Les deux couches se complètent mais nécessitent des outils de dépannage et des critères de validation distincts.

### 5.1 Principes de l’underlay

Un underlay de datacenter moderne est souvent conçu en L3 avec des liens routés, un IGP adapté ou des routes statiques dans des environnements très simples, et ECMP entre fabrics. Le choix IS-IS ou OSPF, la conception des loopbacks, le filtrage des annonces, la MTU et les objectifs de convergence doivent être documentés. Le but est un transport IP prévisible entre endpoints d’overlay.

### 5.2 Overlay EVPN-VXLAN

VXLAN encapsule une trame Ethernet dans UDP/IP et utilise un identifiant VNI pour distinguer des segments logiques. EVPN peut fournir un plan de contrôle BGP pour annoncer les informations MAC/IP et les services associés. Le rôle précis de chaque type de route EVPN et les procédures de multihoming doivent être compris et vérifiés sur la version utilisée. Il faut éviter de réduire EVPN-VXLAN à « VLAN avec un numéro plus grand » : on ajoute une encapsulation, un contrôle de reachability, un modèle de mobilité et des états de contrôle supplémentaires.


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="520" viewBox="0 0 1120 520"><rect x="0" y="0" width="1120" height="520" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Underlay et overlay : deux couches différentes</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">L’underlay transporte les paquets encapsulés ; l’overlay définit les segments et services</text><rect x="60" y="104" width="205" height="76" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="162.5" y="136.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Hôte A</text><text x="162.5" y="157.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">VLAN / VRF</text><rect x="855" y="104" width="205" height="76" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="957.5" y="136.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Hôte B</text><text x="957.5" y="157.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">VLAN / VRF</text><rect x="350" y="102" width="420" height="82" rx="12" fill="#4c1d95" stroke="#c4b5fd" stroke-width="2"/><text x="560.0" y="137.62" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="600" fill="#f8fafc">Overlay</text><text x="560.0" y="160.62" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="600" fill="#f8fafc">VNI / EVPN / politiques tenant</text><line x1="265" y1="142" x2="350" y2="142" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="350,142 338.0,148.0 338.0,136.0" fill="#8fb8e8"/><text x="307.5" y="134.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">encapsulation</text><line x1="770" y1="142" x2="855" y2="142" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="855,142 843.0,148.0 843.0,136.0" fill="#8fb8e8"/><text x="812.5" y="134.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">décapsulation</text><rect x="150" y="300" width="180" height="78" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="240.0" y="333.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Leaf / VTEP 1</text><text x="240.0" y="354.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Loopback IP</text><rect x="470" y="300" width="180" height="78" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="560.0" y="333.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Spine IP</text><text x="560.0" y="354.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">ECMP underlay</text><rect x="790" y="300" width="180" height="78" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="880.0" y="333.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Leaf / VTEP 2</text><text x="880.0" y="354.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Loopback IP</text><line x1="330" y1="338" x2="470" y2="338" stroke="#62d6a4" stroke-width="3" stroke-linecap="round"/><polygon points="470,338 458.0,344.0 458.0,332.0" fill="#62d6a4"/><text x="400.0" y="330.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">IP</text><line x1="470" y1="338" x2="330" y2="338" stroke="#62d6a4" stroke-width="3" stroke-linecap="round"/><polygon points="330,338 342.0,332.0 342.0,344.0" fill="#62d6a4"/><line x1="650" y1="338" x2="790" y2="338" stroke="#62d6a4" stroke-width="3" stroke-linecap="round"/><polygon points="790,338 778.0,344.0 778.0,332.0" fill="#62d6a4"/><text x="720.0" y="330.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">IP</text><line x1="790" y1="338" x2="650" y2="338" stroke="#62d6a4" stroke-width="3" stroke-linecap="round"/><polygon points="650,338 662.0,332.0 662.0,344.0" fill="#62d6a4"/><text x="560" y="425" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#fbbf24">Diagnostic : vérifier d’abord la reachability VTEP, puis le contrôle EVPN, puis le service tenant.</text><text x="560" y="465" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#cbd5e1">MTU, ECMP et routage IP sont des dépendances de l’overlay, pas des détails secondaires.</text></svg>


### 5.3 MTU et encapsulation

L’en-tête externe ajoute de la charge au paquet ou à la trame. Si les MTU ne sont pas cohérentes le long du chemin, les grands paquets peuvent être perdus ou fragmentés selon le protocole, la version et les paramètres. Vérifie la MTU effective de bout en bout, y compris l’underlay et les interfaces tunnel, et utilise des tests de taille progressive. Un ping de petite taille ne démontre pas que les paquets d’application les plus grands passent.

Le diagnostic d’un overlay doit distinguer quatre questions :

1. L’endpoint distant est-il joignable par l’underlay ?
2. Les informations de contrôle overlay sont-elles apprises et installées ?
3. Le tunnel est-il encapsulé et décapsulé correctement, avec un MTU approprié ?
4. Le service au-dessus de l’overlay, y compris les politiques de sécurité, fonctionne-t-il ?

### 5.4 EVPN, VPN MPLS et SD-WAN : ne pas confondre

| Pattern | Usage typique | Principe central | Risques/complexité à gérer |
|---|---|---|---|
| Campus L3 | Accès et distribution d’entreprise | Routage, ECMP, domaines L2 contenus | Adressage, convergence, mobilité de terminaux |
| EVPN-VXLAN | Fabric datacenter / segmentation multi-tenant | Overlay Ethernet/IP avec control plane EVPN | MTU, convergence overlay, multihoming, modèle VNI/VRF |
| VPN MPLS L3VPN | Service WAN opérateur ou backbone privé | VRF PE et distribution de routes VPN BGP | Contrats d’exploitation opérateur, import/export RT, dépannage partagé |
| SD-WAN | WAN multi-lien orienté politiques | Overlay et sélection de chemin pilotés par politiques | Dépendance au contrôleur, visibilité, licences et comportement propriétaire |
| Routage IP classique | Réseaux simples et interconnexions explicites | Préfixes et next-hops routés | Moins de fonctions intégrées de virtualisation ou d’orchestration |

Aucun de ces patterns n’est universellement supérieur. Une architecture peut utiliser du routage IP simple dans le campus, EVPN-VXLAN dans le datacenter et SD-WAN pour les branches, à condition que les frontières, les responsabilités et l’interopérabilité soient clairement définies.


## 6. Concevoir un WAN multi-sites et hybride

Un WAN doit être conçu à partir de la géographie, des applications, des risques opérateurs, des contraintes de sécurité et du coût total. Une architecture qui fonctionne pour dix sites ne doit pas forcément être reproduite telle quelle pour cent sites : la gestion de l’adressage, la propagation des routes, les domaines de panne et la méthode de déploiement changent d’échelle.

### 6.1 Topologie WAN

Les formes fréquentes sont hub-and-spoke, double hub, full mesh et modèle hybride. Hub-and-spoke simplifie les sorties centralisées et certains contrôles, mais peut accroître la latence ou dépendre des hubs. Full mesh peut raccourcir les chemins mais augmente le nombre de relations et la complexité de politique. Un SD-WAN peut automatiser la sélection de chemins, mais les politiques doivent toujours être écrites, testées et surveillées.

### 6.2 Résilience opérateur

Deux services d’accès ne sont indépendants que si leur indépendance est confirmée. Analyse le dernier kilomètre, l’agrégation, le point de présence, le conduit, l’alimentation, le fournisseur de transit et les dépendances DNS/contrôle. Pour les applications critiques, mesure le RTT, la perte et la gigue de chaque chemin et définis les seuils de bascule. Une bascule qui se déclenche trop facilement peut provoquer du flapping ; une bascule trop tardive peut violer le SLO.

### 6.3 BGP à la frontière

BGP sert à échanger des routes entre systèmes autonomes ou au sein d’un réseau selon une politique explicite. Dans les architectures WAN et Internet, il faut documenter les voisins, les préfixes autorisés, les attributs utilisés, les filtres d’import/export, les limites de routes et les règles de préférence.

Les politiques doivent distinguer :

- **Préférence interne** : par exemple `LOCAL_PREF`, qui influence le choix de sortie dans l’AS.
- **Influence sur les chemins externes** : par exemple `AS_PATH`, communautés et, dans certains environnements, MED. Ces attributs n’ont pas tous la même portée ni la même priorité.
- **Filtrage** : limites de préfixes, prefix-lists, communautés permises, validations d’origine et politiques de prévention des fuites.
- **Résolution du next-hop** : une route BGP acceptable peut ne pas être installable si son next-hop n’est pas résolu ou si la politique locale la rejette.


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="520" viewBox="0 0 1120 520"><rect x="0" y="0" width="1120" height="520" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Politique BGP : de la réception à l’annonce</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">Ne jamais confondre préférence locale, influence sortante et filtrage de sécurité</text><rect x="40" y="110" width="185" height="80" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="132.5" y="144.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">eBGP entrant</text><text x="132.5" y="165.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">routes reçues</text><rect x="270" y="110" width="195" height="80" rx="12" fill="#4b1d34" stroke="#f9a8d4" stroke-width="2"/><text x="367.5" y="144.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Import policy</text><text x="367.5" y="165.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">prefix-list / RPKI</text><rect x="510" y="110" width="190" height="80" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="605.0" y="144.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Best-path</text><text x="605.0" y="165.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">LOCAL_PREF / AS_PATH</text><rect x="745" y="110" width="160" height="80" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="825.0" y="144.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">RIB / FIB</text><text x="825.0" y="165.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">route installée</text><rect x="945" y="110" width="150" height="80" rx="12" fill="#713f12" stroke="#fbbf24" stroke-width="2"/><text x="1020.0" y="144.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Export policy</text><text x="1020.0" y="165.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">annonce filtrée</text><line x1="225" y1="150" x2="270" y2="150" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="270,150 258.0,156.0 258.0,144.0" fill="#8fb8e8"/><line x1="465" y1="150" x2="510" y2="150" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="510,150 498.0,156.0 498.0,144.0" fill="#8fb8e8"/><line x1="700" y1="150" x2="745" y2="150" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="745,150 733.0,156.0 733.0,144.0" fill="#8fb8e8"/><line x1="905" y1="150" x2="945" y2="150" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="945,150 933.0,156.0 933.0,144.0" fill="#8fb8e8"/><rect x="120" y="300" width="250" height="72" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="245.0" y="330.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Préférence interne</text><text x="245.0" y="351.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">LOCAL_PREF</text><rect x="435" y="300" width="250" height="72" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="560.0" y="330.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Chemin AS externe</text><text x="560.0" y="351.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">AS_PATH / MED</text><rect x="750" y="300" width="250" height="72" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="875.0" y="330.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Hygiène annonce</text><text x="875.0" y="351.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">max-prefix / filtrage</text><line x1="365" y1="190" x2="245" y2="300" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="245,300 249.7915019113048,287.46837961658736 257.900197453513,296.3142292989963" fill="#8fb8e8"/><line x1="600" y1="190" x2="560" y2="300" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,300 558.4621562161097,286.67202053961853 569.7396772979711,290.77293729665894" fill="#8fb8e8"/><line x1="1000" y1="190" x2="875" y2="300" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="875,300 880.044794833721,287.56818415975914 887.9723295724252,296.57674636283224" fill="#8fb8e8"/><text x="560" y="445" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#cbd5e1">Toujours prévoir une route policy explicite, des filtres par voisin et des tests d’annonce avant production.</text></svg>


### 6.4 Hygiène BGP en production

Une politique d’import/export doit être explicite même si la plateforme offre des valeurs par défaut. Configure des filtres propres à chaque voisin, limite les préfixes et prépare les annonces exactes attendues. Si les capacités de l’environnement le permettent, ajoute des contrôles de validation d’origine basés sur RPKI et traite les résultats invalides selon une politique écrite. RPKI origin validation ne valide pas toute la politique de chemin et ne remplace pas les filtres ni la surveillance.

Pour chaque voisin BGP, documente au minimum : l’identité de l’opérateur, le rôle du peering, les adresses et ASN, l’authentification prise en charge, les familles d’adresses, les préfixes attendus, les attributs utilisés, les limites de routes, les méthodes de test, les alertes et le contact d’escalade.

### 6.5 Cloud et interconnexion hybride

Le cloud ajoute des primitives de réseau (réseaux virtuels, tables de routes, gateways, transit hubs, security groups, endpoints privés) et des limites de quotas. Le réseau on-premise et le cloud doivent partager une gouvernance d’adressage et de segmentation. Les chevauchements de préfixes deviennent particulièrement coûteux lorsque plusieurs clouds, partenaires et acquisitions doivent être interconnectés.

Distingue explicitement le plan de contrôle de l’interconnexion, la propagation des routes, les règles de sécurité cloud et le chemin de données. La présence d’un tunnel ou d’un circuit privé ne signifie pas que les routes attendues sont apprises dans les deux sens ni que le flux est autorisé dans les deux environnements.


## 7. Segmentation experte et modèle de confiance

La segmentation est une décision de sécurité et d’exploitation, pas seulement un choix d’adressage. Une VRF isole des tables de routage ; elle n’applique pas automatiquement une inspection applicative. Des ACL filtrent les paquets selon leurs champs et possibilités ; un pare-feu stateful peut suivre l’état des sessions ; un proxy ou une passerelle applicative fournit d’autres contrôles. Ces mécanismes ont des rôles complémentaires.

### 7.1 Définir les zones par fonction et niveau de confiance

Les zones courantes incluent postes utilisateurs, serveurs, administration, IoT, invités, services partagés, DMZ, sauvegardes et management hors bande. La classification doit se fonder sur les besoins du métier et les conséquences d’un compromis. N’empile pas des VLAN sans définir qui peut communiquer avec qui, ni qui approuve une exception.

### 7.2 Matrice de flux

| Source | Destination | Exemple de besoin | Contrôle attendu |
|---|---|---|---|
| Utilisateurs gérés | Application ERP | TCP sur ports applicatifs approuvés | Authentification, règle ciblée, logs utiles |
| Utilisateurs | Administration des équipements | Généralement interdit depuis le LAN utilisateur | Bastion / réseau de management |
| IoT | Serveur de collecte | Flux sortants spécifiés | Egress filtré, inventaire d’identité si possible |
| Invités | Réseau interne | Aucun accès métier par défaut | Internet only, isolement clients si approprié |
| Supervision | Équipements réseau | SNMPv3 / API / SSH selon norme interne | ACL de management, identité et journalisation |
| Sauvegarde | Serveurs protégés | Flux strictement nécessaires | Comptes séparés, contrôle de destination et audit |


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="520" viewBox="0 0 1120 520"><rect x="0" y="0" width="1120" height="520" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Segmentation de confiance : VRF, pare-feu et identité</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">La séparation logique doit être assortie d’une politique de flux vérifiable</text><rect x="55" y="105" width="200" height="80" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="155.0" y="139.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Zone utilisateurs</text><text x="155.0" y="160.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">VRF / VLAN</text><rect x="355" y="105" width="200" height="80" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="455.0" y="139.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Zone serveurs</text><text x="455.0" y="160.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">VRF / VLAN</text><rect x="655" y="105" width="200" height="80" rx="12" fill="#4c1d95" stroke="#c4b5fd" stroke-width="2"/><text x="755.0" y="139.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Zone admin</text><text x="755.0" y="160.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">accès restreint</text><rect x="865" y="105" width="200" height="80" rx="12" fill="#713f12" stroke="#fbbf24" stroke-width="2"/><text x="965.0" y="139.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Zone IoT</text><text x="965.0" y="160.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">sorties minimales</text><rect x="380" y="275" width="360" height="90" rx="12" fill="#4b1d34" stroke="#f9a8d4" stroke-width="2"/><text x="560.0" y="314.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">Point de contrôle</text><text x="560.0" y="336.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">pare-feu / ACL / policy engine</text><line x1="155" y1="185" x2="420" y2="275" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="420,275 406.70792637720723,276.82230041602804 410.5669154935019,265.45972135138254" fill="#8fb8e8"/><text x="287.5" y="222.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">règles</text><line x1="455" y1="185" x2="490" y2="275" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="490,275 480.05861683689284,265.9906215084341 491.2426728953884,261.64126637457474" fill="#8fb8e8"/><text x="472.5" y="222.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">règles</text><line x1="755" y1="185" x2="650" y2="275" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="650,275 655.2063309876478,262.6349639043366 663.0158274691194,271.74604313272016" fill="#8fb8e8"/><text x="702.5" y="222.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">règles</text><line x1="965" y1="185" x2="700" y2="275" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="700,275 709.4330845064982,265.45972135138254 713.2920736227928,276.82230041602804" fill="#8fb8e8"/><text x="832.5" y="222.0" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#fbbf24">règles</text><text x="560" y="415" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#e2e8f0">Principe : deny by default, ouvrir par application, source, destination, port, identité et justification.</text><text x="560" y="455" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#fca5a5">La VRF isole une table de routage ; elle ne remplace pas à elle seule un pare-feu applicatif.</text></svg>


### 7.3 Principe de moindre privilège

La philosophie Zero Trust ne signifie pas « supprimer le réseau » : elle signifie ne pas accorder une confiance implicite uniquement parce qu’un système se situe à l’intérieur d’un périmètre réseau. L’accès doit se fonder sur des décisions adaptées au contexte, à l’identité, à l’état de l’appareil et à la ressource, avec une vérification continue selon le risque. Les contrôles réseau restent importants, mais ils doivent être intégrés aux politiques d’identité et aux mécanismes de protection des applications.

### 7.4 Réduction du rayon d’impact

Pour les systèmes sensibles, utilise des frontières explicites, des chemins d’administration dédiés, des règles de flux restreintes, des comptes distincts et une journalisation centralisée. Les environnements de test et de production devraient être séparés selon le risque. Une politique « any-to-any » temporaire devient souvent permanente si la date de fin, le propriétaire et la justification ne sont pas définis.

### 7.5 Contrôler le trafic est-ouest

Le trafic est-ouest correspond aux échanges au sein d’un même environnement (par exemple entre serveurs). Il peut être plus difficile à observer que le trafic nord-sud vers Internet. La microsegmentation, les politiques distribuées ou les pare-feu internes peuvent améliorer le contrôle, mais ajoutent des dépendances opérationnelles. Pour choisir le placement des contrôles, évalue la visibilité, la capacité, la latence, la résilience, l’asymétrie et la capacité à produire une preuve d’autorisation/refus.


## 8. Résilience avancée et convergence

La résilience ne se résume pas à deux routeurs et deux liens. Elle doit être pensée sur la chaîne complète : détection de panne, réaction de protocole, sélection de chemin, transfert FIB, capacité restante, état des sessions et récupération de l’application.

### 8.1 Détection : BFD, timers et probes synthétiques

BFD (Bidirectional Forwarding Detection) permet de détecter certaines pertes de connectivité entre systèmes avec un mécanisme indépendant des minuteries de nombreux protocoles de routage. Il ne mesure pas la santé applicative et n’est pas forcément approprié sur tous les types de chemins. Les IP SLA/probes synthétiques peuvent tester une cible et un trajet plus proches de l’usage réel, mais exigent une sélection correcte de source, de destination, de VRF et de chemin.

Combine les signaux avec prudence : un test peut échouer parce que la cible ne répond pas à ICMP même si le service fonctionne ; à l’inverse, le test peut réussir sur un chemin différent du trafic applicatif. Il faut donc documenter la sémantique de chaque probe et tester son comportement en situation de charge.

### 8.2 Convergence et microboucles

Après un changement de topologie, différents nœuds peuvent mettre à jour leurs informations à des instants différents. Pendant cet intervalle, un paquet peut être envoyé vers un nœud qui le renvoie vers l’émetteur ou vers un chemin obsolète. Les microboucles sont liées à l’ordre de mise à jour des tables de forwarding et aux changements de route ; elles sont distinctes d’une boucle L2 causée par un mauvais câblage ou un défaut STP.

Le design doit vérifier la convergence selon les chemins et les protocoles présents. Des mécanismes tels que la convergence rapide, les protections de control plane et, selon la plateforme, les fonctions de prévention de microboucle peuvent réduire le risque, mais ne remplacent pas un test de bascule. Mesure les pertes pendant une fenêtre définie, pas uniquement le temps affiché par la CLI.

### 8.3 ECMP, hashing et asymétrie

ECMP permet plusieurs chemins de coût équivalent mais ne garantit pas que chaque flux est réparti également. Les paquets appartenant à une conversation doivent souvent rester sur le même chemin pour éviter le réordonnancement. La distribution dépend des champs de hachage et de l’équipement. Une perte de chemin peut créer des collisions de charge sur les chemins restants, particulièrement si quelques flux volumineux dominent.

L’asymétrie est acceptable dans certaines architectures mais peut poser problème aux pare-feu stateful, aux systèmes de capture ou aux fonctions de NAT. Il faut valider le comportement de retour et l’état de session après bascule, pas uniquement la reachability IP dans le sens aller.

### 8.4 HA du réseau et état des services

La redondance d’équipement ne garantit pas que l’état de session, la traduction NAT, la connexion VPN ou la session applicative survivra. Un service peut avoir besoin d’une reconnexion, d’un retry ou d’une réplication de son état. Documente la différence entre failover de transport, reprise de session et disponibilité applicative.


## 9. QoS, ingénierie de capacité et performance

La QoS doit s’appuyer sur une politique cohérente à travers tout le chemin. Marquer les paquets sans contrôle du trust boundary peut permettre à des hôtes de s’attribuer une priorité injustifiée. À l’inverse, effacer tous les marquages peut empêcher les applications sensibles de bénéficier du traitement prévu. Le design doit préciser où le marquage est accepté, normalisé, modifié et traduit entre technologies.

### 9.1 Classes, files et congestion

Une politique peut distinguer voix interactive, vidéo, contrôle réseau, applications transactionnelles et trafic best-effort. Les noms exacts et la sémantique DSCP doivent être normalisés dans l’organisation. Une file à priorité stricte doit être protégée contre l’abus et dimensionnée pour éviter de priver les autres classes de capacité. Les algorithmes de queueing, shaping et policing ne sont pas interchangeables.


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="500" viewBox="0 0 1120 500"><rect x="0" y="0" width="1120" height="500" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">QoS et capacité : mesurer avant de prioriser</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">Une classe prioritaire sans contrôle d’admission peut dégrader toutes les autres</text><rect x="55" y="100" width="220" height="80" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="165.0" y="134.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Trafic entrant</text><text x="165.0" y="155.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">classification / trust</text><rect x="345" y="100" width="220" height="80" rx="12" fill="#4c1d95" stroke="#c4b5fd" stroke-width="2"/><text x="455.0" y="134.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Policy edge</text><text x="455.0" y="155.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">marquage DSCP</text><rect x="635" y="100" width="220" height="80" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="745.0" y="134.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Queue / scheduler</text><text x="745.0" y="155.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">priorité + limites</text><rect x="925" y="100" width="150" height="80" rx="12" fill="#713f12" stroke="#fbbf24" stroke-width="2"/><text x="1000.0" y="134.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Lien saturé</text><text x="1000.0" y="155.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">mesures</text><line x1="275" y1="140" x2="345" y2="140" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="345,140 333.0,146.0 333.0,134.0" fill="#8fb8e8"/><line x1="565" y1="140" x2="635" y2="140" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="635,140 623.0,146.0 623.0,134.0" fill="#8fb8e8"/><line x1="855" y1="140" x2="925" y2="140" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="925,140 913.0,146.0 913.0,134.0" fill="#8fb8e8"/><rect x="90" y="285" width="280" height="76" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="230.0" y="317.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Contrôler</text><text x="230.0" y="338.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">débit · pertes · latence</text><rect x="420" y="285" width="280" height="76" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="560.0" y="317.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Protéger</text><text x="560.0" y="338.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">policer · shape · admission</text><rect x="750" y="285" width="280" height="76" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="890.0" y="317.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Valider</text><text x="890.0" y="338.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">SLA par classe applicative</text><line x1="200" y1="180" x2="230" y2="285" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="230,285 220.93420277938654,275.1100393956944 232.4724901510764,271.81338586092585" fill="#8fb8e8"/><line x1="750" y1="180" x2="560" y2="285" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,285 567.6007817551306,273.9443174470829 573.405015095412,284.44721587235415" fill="#8fb8e8"/><line x1="1000" y1="180" x2="890" y2="285" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="890,285 894.5374120496278,272.37415777494857 902.8231210098179,281.05442430467144" fill="#8fb8e8"/><text x="560" y="435" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#cbd5e1">Priorité : audio/contrôle temps réel selon design ; ne pas confondre DSCP marqué et traitement garanti.</text></svg>


### 9.2 Capacité nominale et capacité de panne

Dimensionne à partir de la charge nominale, de la croissance, des pointes, des sauvegardes, des transferts volumineux et du scénario de perte majeur. Une architecture qui utilise 70 % de chaque chemin en fonctionnement normal peut être incapable d’absorber tout le trafic après la perte d’un lien. Le dimensionnement doit porter sur chaque goulot d’étranglement : accès, uplink, WAN, pare-feu, NAT, contrôleur, collecteur et CPU du control plane.

### 9.3 Latence, gigue, perte et temps de réponse

La latence de bout en bout inclut plusieurs segments et le traitement intermédiaire. La gigue décrit la variation du délai ; les pertes peuvent être liées à la congestion, aux erreurs physiques, au MTU, à la politique, au policing ou aux files. Le temps de réponse applicatif peut également être dominé par le serveur, le DNS, TLS ou les dépendances externes. Corrèle les mesures avec le même intervalle de temps et les horloges synchronisées.

### 9.4 Mesure et critères d’acceptation

Un test de capacité sérieux précise le modèle de trafic, la durée, le nombre de flux, la taille des paquets, la direction, la charge de fond, le point de capture et la méthode de mesure. Les résultats d’un laboratoire sous faible charge ne suffisent pas à prouver une performance de production. Les tests doivent respecter les règles de sécurité, le périmètre autorisé et les fenêtres approuvées.


## 10. Observabilité unifiée et diagnostic fondé sur les preuves

Une architecture devient difficile à exploiter lorsque les équipes collectent des milliers de métriques sans savoir quelles questions elles doivent résoudre. L’observabilité doit être conçue autour des modes de panne attendus et des décisions opérationnelles : confirmer un incident, identifier le rayon d’impact, distinguer une panne réseau d’une panne applicative et vérifier le retour à la normale.

### 10.1 Les quatre familles de données

- **Mesures synthétiques** : ICMP, TCP, DNS ou transaction applicative, selon le service.
- **Flux** : NetFlow/IPFIX ou équivalent, utiles pour identifier les conversations, volumes et destinations observés.
- **État et compteurs** : interfaces, erreurs, drops, queues, routes, FIB, CPU, mémoire, tables et sessions.
- **Événements et traces** : syslog, journaux de sécurité, changement de configuration, événements de routage et traces applicatives pertinentes.


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="520" viewBox="0 0 1120 520"><rect x="0" y="0" width="1120" height="520" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Observabilité : corréler les couches</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">Un symptôme utilisateur est diagnostiqué en combinant plusieurs signaux synchronisés</text><rect x="45" y="100" width="240" height="78" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="165.0" y="133.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Mesures de chemin</text><text x="165.0" y="154.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">IP SLA / TWAMP</text><rect x="320" y="100" width="240" height="78" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="440.0" y="133.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Flux de trafic</text><text x="440.0" y="154.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">NetFlow / IPFIX</text><rect x="595" y="100" width="240" height="78" rx="12" fill="#4c1d95" stroke="#c4b5fd" stroke-width="2"/><text x="715.0" y="133.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">État réseau</text><text x="715.0" y="154.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">SNMP / streaming telemetry</text><rect x="870" y="100" width="205" height="78" rx="12" fill="#713f12" stroke="#fbbf24" stroke-width="2"/><text x="972.5" y="133.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Événements</text><text x="972.5" y="154.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">syslog / traps</text><rect x="300" y="275" width="520" height="95" rx="12" fill="#26374f" stroke="#93c5fd" stroke-width="2"/><text x="560.0" y="317.12" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="600" fill="#f8fafc">Plateforme de corrélation</text><text x="560.0" y="340.12" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="600" fill="#f8fafc">temps synchronisé · topologie · inventaire</text><line x1="165" y1="178" x2="370" y2="275" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="370,275 356.5867487558157,275.29101728537677 361.71923542518795,264.4440093758786" fill="#8fb8e8"/><line x1="440" y1="178" x2="455" y2="275" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="455,275 447.23660559334337,264.0578929229013 459.095649017685,262.22402022841555" fill="#8fb8e8"/><line x1="715" y1="178" x2="650" y2="275" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="650,275 651.6957176689507,261.69118556793245 661.6644821470245,268.37128547592005" fill="#8fb8e8"/><line x1="970" y1="178" x2="750" y2="275" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="750,275 758.5594851340488,264.66872639797026 763.400709962053,275.6488239460212" fill="#8fb8e8"/><rect x="365" y="420" width="390" height="58" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="560.0" y="454.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Diagnostic : hypothèse → test → preuve</text><line x1="560" y1="370" x2="560" y2="420" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,420 554.0,408.0 566.0,408.0" fill="#8fb8e8"/></svg>


### 10.2 Horodatage et cardinalité

La corrélation est peu fiable si les systèmes n’ont pas une heure cohérente. Utilise NTP ou une architecture de synchronisation adaptée, surveille les écarts et conserve la provenance des données. Évite de construire des identifiants de métriques non bornés à partir de toute adresse, de tout port et de tout utilisateur sans raison : une cardinalité trop élevée peut rendre le stockage et les requêtes prohibitifs.

### 10.3 Ne pas confondre corrélation et causalité

Deux métriques qui changent en même temps ne prouvent pas qu’une est la cause de l’autre. Le taux d’erreurs d’interface peut augmenter pendant qu’une application ralentit, mais il faut vérifier si le trafic de l’application traversait cette interface et si l’augmentation précède réellement le symptôme. Les captures paquet peuvent fournir une preuve détaillée mais ont des coûts de stockage, de confidentialité et de performance ; la collecte doit respecter les règles de l’organisation.

### 10.4 Construire un runbook utile

Chaque alerte importante devrait répondre à :

1. Quel service et quels utilisateurs sont potentiellement touchés ?
2. Quels signaux la déclenchent et quelle est leur limite ?
3. Quel test non destructif confirmerait l’hypothèse ?
4. Quelles commandes ou dashboards consulter dans quel ordre ?
5. Quelle action est sûre, qui peut l’approuver, et comment revenir en arrière ?
6. Quelle preuve permet de clôturer l’incident ?

Les alertes fondées sur un seul indicateur générique produisent souvent du bruit. Favorise des seuils liés au service, des durées d’observation et une documentation de faux positifs connus.


## 11. Automatisation, source de vérité et changement contrôlé

L’automatisation n’est pas uniquement un script qui envoie des commandes à un équipement. Elle doit avoir une source de vérité, un modèle de données, une validation des entrées, une méthode de diff, des approbations et des contrôles après changement.

### 11.1 Source de vérité

L’inventaire doit préciser les sites, rôles, modèles, versions, interfaces, liens, adresses, VRF, VLAN, voisins, propriétaires, criticité et dépendances. Si les informations sont dispersées dans plusieurs fichiers non synchronisés, l’automatisation peut propager une erreur plus vite que l’opération manuelle. Les données d’inventaire doivent être validées et les changements suivis dans un historique.

### 11.2 Infrastructure as Code (IaC) réseau

Un pipeline mature peut enchaîner :

1. validation du schéma de données et des conventions ;
2. génération de configuration à partir de modèles ;
3. linting et analyse statique ;
4. comparaison avec l’état actuel ;
5. test en environnement de laboratoire ou de préproduction ;
6. approbation et déploiement progressif ;
7. test de service après déploiement ;
8. collecte du résultat et rollback contrôlé si nécessaire.

Ne place pas les secrets en clair dans Git. Utilise des mécanismes adaptés de stockage de secrets, une séparation des rôles et des journaux d’audit. Le pipeline devrait échouer en mode fermé si des données essentielles manquent ou si les validations échouent.

### 11.3 Gestion des changements

Un changement réseau doit définir son périmètre, son propriétaire, ses dépendances, sa fenêtre, son plan de tests, les seuils d’abandon et son rollback. Pour les changements de routage, documente l’état avant, les routes attendues après, le comportement sur perte du chemin, et les filtres qui empêchent une annonce inattendue. Il faut savoir restaurer la configuration, mais aussi vérifier le résultat dans la RIB/FIB et sur le service.


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="520" viewBox="0 0 1120 520"><rect x="0" y="0" width="1120" height="520" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Migration de réseau : phases et portes de validation</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">Un changement réussi est mesuré par des critères d’acceptation et un rollback testé</text><rect x="35" y="120" width="180" height="90" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="125.0" y="159.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">1. Découvrir</text><text x="125.0" y="180.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">inventaire / baseline</text><rect x="255" y="120" width="180" height="90" rx="12" fill="#4c1d95" stroke="#c4b5fd" stroke-width="2"/><text x="345.0" y="159.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">2. Concevoir</text><text x="345.0" y="180.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">ADR / risques</text><rect x="475" y="120" width="180" height="90" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="565.0" y="159.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">3. Piloter</text><text x="565.0" y="180.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">périmètre limité</text><rect x="695" y="120" width="180" height="90" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="785.0" y="159.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">4. Déployer</text><text x="785.0" y="180.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">vagues contrôlées</text><rect x="915" y="120" width="170" height="90" rx="12" fill="#713f12" stroke="#fbbf24" stroke-width="2"/><text x="1000.0" y="159.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">5. Exploiter</text><text x="1000.0" y="180.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">SLO / runbook</text><line x1="215" y1="165" x2="255" y2="165" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="255,165 243.0,171.0 243.0,159.0" fill="#8fb8e8"/><line x1="435" y1="165" x2="475" y2="165" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="475,165 463.0,171.0 463.0,159.0" fill="#8fb8e8"/><line x1="655" y1="165" x2="695" y2="165" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="695,165 683.0,171.0 683.0,159.0" fill="#8fb8e8"/><line x1="875" y1="165" x2="915" y2="165" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="915,165 903.0,171.0 903.0,159.0" fill="#8fb8e8"/><rect x="130" y="315" width="260" height="80" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="260.0" y="349.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Gate de validation</text><text x="260.0" y="370.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">tests fonctionnels + résilience</text><rect x="430" y="315" width="260" height="80" rx="12" fill="#4b1d34" stroke="#f9a8d4" stroke-width="2"/><text x="560.0" y="349.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Rollback</text><text x="560.0" y="370.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">préconditions / délai / owner</text><rect x="730" y="315" width="260" height="80" rx="12" fill="#26374f" stroke="#65a8ff" stroke-width="2"/><text x="860.0" y="349.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Après changement</text><text x="860.0" y="370.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">état final / écarts / preuve</text><line x1="350" y1="210" x2="260" y2="315" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="260,315 263.25395686727984,301.98417253088064 272.3650360956634,309.7936690123522" fill="#8fb8e8"/><line x1="560" y1="210" x2="560" y2="315" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,315 554.0,303.0 566.0,303.0" fill="#8fb8e8"/><line x1="785" y1="210" x2="860" y2="315" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="860,315 848.1427408481304,308.72262750783375 857.9075425026112,301.7477691832046" fill="#8fb8e8"/><text x="560" y="455" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#fbbf24">Aucun déploiement sans fenêtre, responsables, sauvegarde, critères d’abandon et communication.</text></svg>


### 11.4 Modèles de configuration et standardisation

Un modèle de configuration doit séparer paramètres variables et invariants. Exemple d’invariants : NTP approuvé, comptes d’administration gérés, SSH durci, ACL de management, syslog, télémétrie, bannière et conventions de nommage. Les exceptions doivent être représentées explicitement plutôt que codées sous forme de divergences silencieuses. Les standards ne doivent pas empêcher une adaptation justifiée ; ils doivent rendre les différences visibles.


## 12. Sécurité de l’infrastructure et du plan de gestion

Le plan de gestion constitue un chemin privilégié vers le réseau. Il doit être plus difficile à atteindre que le trafic utilisateur et limiter les actions possibles à chaque identité. Les mesures précises dépendent des fonctions de l’équipement, du modèle de gestion et des normes internes.

### 12.1 Contrôles essentiels

- Administrer via des protocoles chiffrés et des mécanismes d’identité appropriés ; désactiver les services inutiles lorsque cela est pris en charge.
- Séparer les accès utilisateurs et administrateurs et, pour les actifs critiques, évaluer un réseau de management hors bande.
- Contrôler les sources d’administration et réduire la portée des comptes et clés.
- Centraliser les événements utiles et protéger l’intégrité des journaux selon le risque.
- Sauvegarder les configurations et tester la restauration.
- Suivre les versions, vulnérabilités, bulletins fournisseurs et fenêtres de correctifs.
- Protéger le control plane contre les flux qui ne devraient jamais atteindre les processus de routage.
- Tester le comportement de sécurité en situation de bascule et lors de la perte des services d’identité.

### 12.2 Durcissement du routage

Les sessions de routage doivent être limitées à leurs voisins attendus et aux interfaces appropriées. Quand ils sont pris en charge, l’authentification de voisinage, les filtres de préfixes, les limites de routes, les communautés contrôlées, la validation d’origine et les fonctions de protection du control plane peuvent réduire les risques. Aucune protection unique ne suffit contre toutes les erreurs de politique, les fuites de routes ou les erreurs de configuration.

### 12.3 Plan de management hors bande

Le réseau hors bande peut être utile en cas de panne de l’infrastructure de production ou de changement qui coupe l’accès normal. Il doit être conçu lui-même : disponibilité, contrôle d’accès, MFA selon la plateforme, chemins physiques, accès d’urgence, logs et procédure d’utilisation. Un réseau de secours trop largement accessible devient un raccourci pour contourner les contrôles de sécurité.

### 12.4 Zero Trust et segmentation réseau

Les contrôles de réseau sont une couche d’application de politique parmi d’autres. Ils ne remplacent ni l’identité de l’utilisateur et du terminal, ni les contrôles d’accès à l’application, ni l’évaluation du risque. Pour chaque flux d’administration ou d’application, documente l’identité attendue, la source, la destination, la ressource, les ports, la justification, les logs et le propriétaire.


## 13. Multicast, IPv6 et services spécialisés à l’échelle

Dans les grands réseaux, certains flux sortent du modèle « unicast classique ». La conception doit rendre visibles les protocoles de découverte, les dépendances et les limites de propagation.

### 13.1 Multicast

Pour du multicast routé, le plan de contrôle et le forwarding reposent sur des mécanismes distincts : appartenance aux groupes, arbres de distribution, RPF et état de forwarding. Le test unicast vers l’adresse source ou le routeur ne garantit pas qu’un groupe multicast sera livré. Il faut vérifier l’adhésion au groupe, les états PIM appropriés, le sens RPF, les interfaces entrantes/sortantes et les ACL applicables.

### 13.2 IPv6 à grande échelle

IPv6 exige un plan de préfixes cohérent, une stratégie de résumé, une gouvernance du RA, Neighbor Discovery, DHCPv6 si utilisé et des règles de sécurité équivalentes au niveau IPv4. Le dual-stack double certains travaux de surveillance et de dépannage, mais permet une transition progressive. Évite les filtres qui ne couvrent qu’IPv4 en pensant que l’architecture est sécurisée.

### 13.3 DNS, NTP, PKI et identité

Ces services sont des dépendances de l’infrastructure, pas des détails annexes. Les équipements utilisent DNS, NTP, certificats et systèmes d’identité dans leurs fonctions de gestion et de sécurité. Une panne de ces dépendances peut ressembler à un problème réseau ou empêcher une opération pourtant prévue. Documente les chemins, les résolveurs, les sources de temps, les autorités de certification et les procédures d’urgence.


## 14. Architectures de référence et choix technologiques

Une bonne architecture documente autant les raisons de refuser une technologie que celles de l’adopter. Elle évalue les exigences, la complexité à opérer, la capacité disponible, les compétences et les contraintes de migration. La capacité à expliquer une solution en termes de modes de panne compte autant que ses fonctionnalités.


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="520" viewBox="0 0 1120 520"><rect x="0" y="0" width="1120" height="520" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Choisir le bon pattern : décisions explicites</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">Le pattern dépend des contraintes ; aucune technologie n’est une réponse universelle</text><rect x="45" y="135" width="230" height="110" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="160.0" y="184.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Campus L3</text><text x="160.0" y="205.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">simplicité / ECMP</text><rect x="320" y="135" width="230" height="110" rx="12" fill="#4c1d95" stroke="#c4b5fd" stroke-width="2"/><text x="435.0" y="184.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">EVPN-VXLAN</text><text x="435.0" y="205.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">segments DC extensibles</text><rect x="595" y="135" width="230" height="110" rx="12" fill="#713f12" stroke="#fbbf24" stroke-width="2"/><text x="710.0" y="184.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">MPLS L3VPN</text><text x="710.0" y="205.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">services opérateur</text><rect x="870" y="135" width="230" height="110" rx="12" fill="#1e3a5f" stroke="#93c5fd" stroke-width="2"/><text x="985.0" y="184.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">SD-WAN</text><text x="985.0" y="205.94" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">policy WAN par application</text><rect x="165" y="325" width="790" height="78" rx="12" fill="#26374f" stroke="#93c5fd" stroke-width="2"/><text x="560.0" y="358.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">Matrice de décision</text><text x="560.0" y="380.78" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="600" fill="#f8fafc">échelle · mobilité L2 · segmentation · compétences · coût · dépannage</text><line x1="160" y1="245" x2="560" y2="325" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,325 547.0563350808799,328.5300904324873 549.409728702538,316.7631223241963" fill="#8fb8e8"/><line x1="435" y1="245" x2="560" y2="325" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,325 546.6584210135217,323.5849840468887 553.127065370602,313.47772723895054" fill="#8fb8e8"/><line x1="710" y1="245" x2="560" y2="325" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,325 567.7647058823529,314.05882352941177 573.4117647058824,324.64705882352945" fill="#8fb8e8"/><line x1="985" y1="245" x2="560" y2="325" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,325 570.6829733218233,316.88371507367975 572.9028119341501,328.67660770166646" fill="#8fb8e8"/><text x="560" y="455" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#cbd5e1">Écrire pourquoi une solution est choisie, ce qu’elle simplifie, ce qu’elle complexifie et quand la reconsidérer.</text></svg>


### 14.1 Matrice de décision indicative

| Critère | Campus routé L3 | EVPN-VXLAN | VPN MPLS L3VPN | SD-WAN |
|---|---|---|---|---|
| Principal intérêt | Simplicité et convergence du campus | Segmentation et mobilité dans le DC | Isolation de tables/services opérateur | Politiques de chemin WAN |
| L2 étendu | Limité par design | Possible via services overlay | Dépend du service offert ; L3VPN n’étend pas un domaine L2 par défaut | Dépend de la solution et du service |
| Plan de contrôle | IGP/EBGP selon design | Underlay + BGP EVPN ou variante | IGP de cœur + MP-BGP VPN dans le réseau opérateur | Contrôle/orchestration souvent propre au produit |
| Exploitation | Routage, adressage, convergence | Overlay, VNI/VRF, MTU, EVPN | Frontières opérateur/entreprise et politique VPN | Contrôleur, tunnels, politiques et licences |
| Risque courant | L2 hérité, mauvaise convergence ou résumé | État overlay et MTU incompris | Problème de partage de responsabilité | Dépendance à l’orchestrateur ou à une politique opaque |

### 14.2 Questions à poser avant le choix

- Quel problème concret le pattern résout-il ?
- Peut-on atteindre l’objectif avec une architecture plus simple ?
- Quels nouveaux états, journaux, licences ou compétences sont introduits ?
- Qui possède et dépanne chaque plan de contrôle ?
- Quelles conséquences si le contrôleur ou l’interconnexion est indisponible ?
- Comment vérifier les routes, le chemin de données et la segmentation ?
- Quelles sont les possibilités réalistes de migration et de retour arrière ?

### 14.3 Architecture et coût total

Le coût total inclut les équipements et abonnements, mais aussi l’exploitation, les compétences, l’automatisation, les licences de télémétrie, la collecte de logs, les environnements de test et le coût des interruptions. Une architecture légèrement plus chère en matériel peut être plus rentable si elle réduit les changements risqués ou accélère le diagnostic. À l’inverse, une solution riche en fonctions peut être un mauvais choix si l’équipe ne peut pas l’exploiter correctement.


## 15. Documentation d’architecture : faire des décisions durables

La documentation ne doit pas être une image figée qui devient rapidement obsolète. Elle devrait combiner vues logique et physique, conventions de nommage, plan IP, politiques de routage, matrice de flux, inventaire de dépendances, scénarios de panne, exigences de supervision et procédures de changement.

### 15.1 Architecture Decision Record (ADR)

Chaque décision importante peut être conservée sous une forme courte :

- **Contexte :** le problème et les contraintes observées.
- **Options :** les solutions réalistes évaluées, avec leurs avantages et risques.
- **Décision :** le pattern retenu et les critères qui l’ont fait gagner.
- **Conséquences :** ce qui devient plus simple, plus complexe, plus coûteux ou impossible.
- **Validation :** les tests, mesures et critères qui permettront d’accepter ou de revoir la décision.
- **Revue :** le propriétaire, la date et les événements qui justifieraient une réévaluation.


<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="500" viewBox="0 0 1120 500"><rect x="0" y="0" width="1120" height="500" rx="18" fill="#0b1424"/><text x="560.0" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#f8fafc">Revue de conception experte</text><text x="560.0" y="59" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#cbd5e1">Passer de besoins métier à une architecture testable et exploitable</text><rect x="40" y="100" width="200" height="75" rx="12" fill="#1e3a5f" stroke="#65a8ff" stroke-width="2"/><text x="140.0" y="132.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Exigences</text><text x="140.0" y="153.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">SLO / criticité</text><rect x="270" y="100" width="200" height="75" rx="12" fill="#4b1d34" stroke="#f9a8d4" stroke-width="2"/><text x="370.0" y="132.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Modèle de panne</text><text x="370.0" y="153.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">risques partagés</text><rect x="500" y="100" width="200" height="75" rx="12" fill="#4c1d95" stroke="#c4b5fd" stroke-width="2"/><text x="600.0" y="132.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Choix technique</text><text x="600.0" y="153.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">patterns / trade-offs</text><rect x="730" y="100" width="160" height="75" rx="12" fill="#164e63" stroke="#5eead4" stroke-width="2"/><text x="810.0" y="132.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Validation</text><text x="810.0" y="153.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">tests / preuves</text><rect x="920" y="100" width="160" height="75" rx="12" fill="#713f12" stroke="#fbbf24" stroke-width="2"/><text x="1000.0" y="132.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">Runbook</text><text x="1000.0" y="153.44" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="600" fill="#f8fafc">ownership</text><line x1="240" y1="137" x2="270" y2="137" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="270,137 258.0,143.0 258.0,131.0" fill="#8fb8e8"/><line x1="470" y1="137" x2="500" y2="137" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="500,137 488.0,143.0 488.0,131.0" fill="#8fb8e8"/><line x1="700" y1="137" x2="730" y2="137" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="730,137 718.0,143.0 718.0,131.0" fill="#8fb8e8"/><line x1="890" y1="137" x2="920" y2="137" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="920,137 908.0,143.0 908.0,131.0" fill="#8fb8e8"/><rect x="230" y="285" width="660" height="92" rx="12" fill="#26374f" stroke="#93c5fd" stroke-width="2"/><text x="560.0" y="325.62" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="600" fill="#f8fafc">Architecture Decision Record (ADR)</text><text x="560.0" y="348.62" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="600" fill="#f8fafc">contexte · options · décision · conséquences · critères de succès</text><line x1="350" y1="175" x2="420" y2="285" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="420,285 408.49552516728943,278.0973151003737 418.6194630200747,271.65480919405576" fill="#8fb8e8"/><line x1="600" y1="175" x2="560" y2="285" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="560,285 558.4621562161097,271.67202053961853 569.7396772979711,275.77293729665894" fill="#8fb8e8"/><line x1="810" y1="175" x2="740" y2="285" stroke="#8fb8e8" stroke-width="3" stroke-linecap="round"/><polygon points="740,285 741.3805369799253,271.65480919405576 751.5044748327106,278.0973151003737" fill="#8fb8e8"/><text x="560" y="430" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#fbbf24">Une architecture experte se justifie par des exigences et des preuves, pas par une liste de fonctionnalités.</text></svg>


### 15.2 Vues à produire

1. **Vue de contexte :** sites, fournisseurs, cloud, services critiques et frontières de confiance.
2. **Vue logique :** VRF, sous-réseaux, zones, relations de routage et politiques.
3. **Vue physique :** équipements, liens, supports, alimentations, emplacements et risques partagés.
4. **Vue opérationnelle :** supervision, accès d’administration, logs, automatisation et restauration.
5. **Vue de panne :** scénarios, état attendu, temps de détection, convergence, capacité et critères de réussite.

Chaque vue doit comporter une date de mise à jour, un propriétaire et un périmètre. Les valeurs illustratives doivent être identifiées comme telles ; les adresses, capacités et niveaux de disponibilité ne doivent jamais être copiés en production sans validation.


## 16. Laboratoire de synthèse : concevoir une entreprise multi-sites

### 16.1 Énoncé

Une entreprise possède un siège, un datacenter, deux agences et des services cloud. Les utilisateurs accèdent à un ERP, des outils SaaS et un service de fichiers. Le datacenter héberge aussi des systèmes d’administration et de sauvegarde. Les agences doivent rester opérationnelles si leur lien principal tombe, et les invités ne doivent pas accéder aux services internes.

Conçois une architecture de référence sans supposer que toutes les fonctions doivent être implémentées par le même fournisseur. Le but est de produire des choix justifiés, une liste des dépendances, des politiques de routage et de sécurité, un plan d’observabilité et une stratégie de bascule.

### 16.2 Livrables attendus

- Diagramme logique multi-sites ;
- plan d’adressage IPv4/IPv6 et règles de résumé ;
- zones de sécurité et matrice de flux ;
- sélection de pattern pour campus, datacenter et WAN ;
- politique d’entrée/sortie BGP si utilisée ;
- matrice de panne couvrant la perte d’un lien, d’un équipement, d’un fournisseur et d’un service partagé ;
- SLI/SLO, alertes et runbooks ;
- plan de migration par étapes et rollback ;
- ADR expliquant au moins trois décisions structurantes.

### 16.3 Exemple de direction d’architecture

Une solution possible pourrait employer un campus majoritairement routé, un underlay L3 dans le datacenter et EVPN-VXLAN lorsque les besoins de segmentation et de mobilité le justifient, et deux transports WAN selon la disponibilité réelle des fournisseurs. Les services partagés doivent être redondés selon leur criticité, et les zones d’administration/sauvegarde séparées. Cette proposition n’est pas une réponse universelle : si les besoins de mobilité L2 sont faibles, un réseau plus simple peut être préférable ; si le budget ou les compétences ne permettent pas d’exploiter l’overlay, il faut l’assumer dans la décision.

### 16.4 Matrice de tests d’acceptation

| Test | Précondition | Action | Résultat attendu | Preuve à conserver |
|---|---|---|---|---|
| Perte du WAN primaire | Trafic applicatif synthétique en cours | Couper le circuit en environnement autorisé | Chemin secondaire activé dans le budget mesuré | Horodatages, mesures RTT/perte, routes |
| Perte d’un uplink campus | Deux chemins en service | Désactiver un lien contrôlé | FIB converge, application reste disponible | État interface, RIB/FIB, test utilisateur |
| Isolation invité | Client invité et cible interne | Tester des flux autorisés/interdits | Internet autorisé, réseau interne refusé | Logs pare-feu et résultats de tests |
| Perte DNS primaire | Résolveur secondaire prêt | Simuler la panne | Résolution reprend selon le SLO | Logs de résolution et latence |
| Changement de politique BGP | Préfixes attendus documentés | Appliquer en pilote | Seuls les préfixes autorisés sont annoncés | Capture des routes avant/après |
| Épuisement de capacité | Profil de charge défini | Augmenter progressivement la charge de test | Seuils et alertes détectent le risque | Courbes, compteurs, résultats de service |
| Restauration de configuration | Sauvegarde validée | Restaurer en lab ou équipement de secours | Configuration et service restaurés | Diff de configuration et test final |

### 16.5 Débrief du laboratoire

Après chaque test, note ce qui a fonctionné, ce qui a été plus lent que prévu, ce qui n’a pas été mesuré et ce qui dépend d’un tiers. Un test est incomplet si la réussite est définie seulement comme « le ping répond ». Il faut vérifier les sessions applicatives, la capacité après bascule, les flux de retour et la possibilité pour l’équipe d’exploiter le réseau pendant l’incident.


## 17. Études de cas avancées

### Cas A — Tout est redondant, mais le site tombe quand même

**Symptôme :** deux uplinks par switch, deux routeurs WAN, mais une panne de conduit coupe toutes les liaisons.  
**Cause conceptuelle :** la redondance logique ne correspond pas à l’indépendance physique.  
**Démarche :** cartographier les circuits et les dépendances communes, demander les informations de route physique à l’opérateur, identifier les SRLG et refaire le modèle de panne.  
**Correction de design :** établir une diversité de chemin vérifiable ou documenter le risque résiduel si la diversité n’est pas possible.  
**Leçon :** une ligne de plus dans un diagramme n’est pas une preuve d’indépendance.

### Cas B — BGP est établi, mais le préfixe ne passe pas

**Symptôme :** la session BGP est Established, mais le réseau distant n’est pas joignable.  
**Hypothèses :** le préfixe n’est pas annoncé, une policy le refuse, l’attribut entraîne un choix inattendu, le next-hop n’est pas résolu, la route n’est pas retenue dans la RIB ou la FIB n’est pas programmée, un filtre de données bloque le flux.  
**Démarche :** vérifier routes reçues, routes acceptées, décision best-path, résolution du next-hop, RIB, FIB puis test du chemin dans les deux sens.  
**Leçon :** la santé d’une session ne démontre pas la santé du service.

### Cas C — Un overlay fonctionne pour les petits paquets

**Symptôme :** la connexion est établie, mais certains transferts ou applications échouent.  
**Hypothèse forte :** MTU ou traitement des paquets volumineux, sans exclure les ACL, TCP MSS ou différences de chemin.  
**Démarche :** tester par tailles progressives et avec DF lorsque pertinent, vérifier MTU des liens et tunnels, consulter les compteurs de drops/fragmentation et comparer le chemin retour.  
**Leçon :** les tests de faible taille ne prouvent pas que le chemin complet accepte la taille requise.

### Cas D — La bascule prend moins d’une seconde, mais l’utilisateur voit une longue interruption

**Symptôme :** le monitoring de lien indique une reprise rapide ; l’application ne récupère qu’après plusieurs secondes.  
**Causes possibles :** perte de session stateful, reconnexion TCP, cache DNS, délai d’application, politique de chemin de retour, mécanisme retry ou état non répliqué.  
**Démarche :** synchroniser les timestamps entre probes, équipement, pare-feu et application ; distinguer détection, convergence, transfert et reprise applicative.  
**Leçon :** le SLO doit être défini depuis le point de vue du service.

### Cas E — Le réseau est sain, mais l’alerte explose

**Symptôme :** alerte de saturation et collecte perdue pendant les pointes.  
**Causes possibles :** cardinalité excessive, fréquence de polling trop importante, buffers ou exporters saturés, pertes de paquets de collecte, horloge désynchronisée, seuils basés sur un unique indicateur.  
**Démarche :** vérifier la chaîne complète, mesurer le taux d’échantillons perdus, contrôler la cardinalité et séparer la santé du collecteur de la santé du service observé.  
**Leçon :** la plateforme de supervision est elle-même un service critique à concevoir et tester.


## 18. Erreurs d’architecture fréquemment rencontrées

1. **Choisir une technologie avant d’avoir les exigences.** La solution peut être sophistiquée mais inadaptée au besoin.
2. **Confondre double connexion et diversité de panne.** Les risques physiques et opérateurs doivent être vérifiés.
3. **Étendre le L2 par défaut.** Chaque extension augmente les impacts possibles d’une erreur de couche 2.
4. **Supposer qu’une route visible dans la RIB est forcément transférée.** Vérifier la FIB, les compteurs et le service.
5. **Ouvrir une politique temporaire sans date d’expiration.** Toute exception doit avoir un propriétaire et un contrôle de retrait.
6. **Activer BFD ou des timers agressifs sans test.** Une détection rapide n’est utile que si le système peut réagir de manière stable.
7. **Marquer le trafic QoS sans gérer la frontière de confiance.** Les classes prioritaires doivent être protégées contre l’abus.
8. **Empiler les couches d’overlay.** Chaque encapsulation et plan de contrôle ajoute un coût opérationnel qui doit être justifié.
9. **N’observer que les interfaces.** Il faut des mesures de service, des flux et des événements corrélables.
10. **Automatiser une source de vérité douteuse.** La validation des données est aussi importante que la qualité du code.
11. **Considérer une configuration sauvegardée comme un rollback testé.** La restauration et le retour du service doivent être éprouvés.
12. **Documenter uniquement l’état normal.** Les scénarios de panne et les chemins de secours doivent également être représentés.


## 19. Checklist de revue d’architecture

### Exigences et conception

- [ ] Les besoins métier ont des indicateurs de service et critères d’acceptation explicites.
- [ ] Les domaines de panne et risques partagés sont cartographiés.
- [ ] Les choix sont consignés dans des ADR avec conséquences et conditions de réexamen.
- [ ] Les frontières campus, datacenter, WAN, cloud, sécurité et gestion sont documentées.
- [ ] Le plan IP, les résumés et les exceptions sont cohérents entre les sites.

### Routage et disponibilité

- [ ] Les politiques BGP d’import/export et les préfixes autorisés sont explicites.
- [ ] Les comportements de convergence ont été mesurés dans les scénarios de panne pertinents.
- [ ] La capacité après perte du chemin principal est suffisante ou le risque est accepté.
- [ ] L’asymétrie est validée avec les pare-feu et services stateful.
- [ ] Le MTU a été testé de bout en bout pour les chemins encapsulés.

### Sécurité

- [ ] Les zones ont une matrice de flux documentée et des propriétaires.
- [ ] Le plan de gestion est séparé et les accès d’urgence sont contrôlés.
- [ ] Les exceptions ont une justification, une échéance et un propriétaire.
- [ ] Les politiques IPv4 et IPv6 ont une couverture cohérente.
- [ ] Le control plane, les sessions de routage et les annonces sont protégés selon les capacités.

### Opérations et changement

- [ ] Les logs, métriques, flux et tests synthétiques sont horodatés et corrélables.
- [ ] Les runbooks indiquent les tests, la décision, le rollback et les preuves de clôture.
- [ ] L’inventaire est une source de vérité gouvernée et contrôlée.
- [ ] Les changements sont testés par étapes avec un mécanisme d’arrêt.
- [ ] Le rollback a été essayé dans un environnement représentatif.
- [ ] Les configurations et les données d’infrastructure sont protégées et sauvegardées.


## 20. Quiz final — Niveau Expert

**1. Pourquoi une architecture à deux liens peut-elle ne pas être résiliente ?**  
A. Parce que l’ECMP ne supporte jamais deux liens.  
B. Parce que les deux liens peuvent partager un conduit, une alimentation ou un fournisseur.  
C. Parce qu’un lien secondaire ne peut jamais transporter du trafic.  
D. Parce que les routeurs ne supportent pas plusieurs next-hops.

**2. Une session BGP est établie, mais un service est inaccessible. Quelle méthode est la plus rigoureuse ?**  
A. Redémarrer immédiatement BGP.  
B. Ajouter une route statique non documentée.  
C. Vérifier routes reçues/acceptées, best-path, next-hop, RIB, FIB et chemin retour.  
D. Augmenter tous les timers.

**3. Que fournit l’underlay d’un réseau EVPN-VXLAN ?**  
A. Uniquement l’authentification des utilisateurs.  
B. La connectivité IP entre endpoints de tunnel, avec routage et capacité appropriés.  
C. La politique applicative complète.  
D. Le remplacement de tous les contrôles de sécurité.

**4. Quel contrôle donne la preuve la plus pertinente qu’un utilisateur peut réellement utiliser une application ?**  
A. La présence d’une route dans la RIB.  
B. L’interface du routeur est up.  
C. Un test synthétique représentatif du service, corrélé aux données réseau.  
D. Un ping vers la passerelle locale.

**5. Pourquoi les timers de détection ne doivent-ils pas simplement être réglés au minimum ?**  
A. Ils peuvent créer de l’instabilité et dépasser la capacité réelle de réaction.  
B. Ils rendent toutes les routes statiques.  
C. Ils désactivent les ACL.  
D. Ils empêchent la collecte de flux dans tous les cas.

**6. Une VRF est-elle suffisante pour imposer une politique applicative complète ?**  
A. Oui, toujours.  
B. Non ; elle sépare des tables de routage mais ne remplace pas nécessairement les contrôles inter-zones ou applicatifs.  
C. Oui, si le VLAN ID est supérieur à 1000.  
D. Non, car les VRF ne fonctionnent qu’en IPv6.

**7. Pourquoi tester la capacité après une panne ?**  
A. Parce que la charge se répartit toujours uniformément.  
B. Parce que les liens restants peuvent être saturés alors que le réseau fonctionnait en régime nominal.  
C. Parce que les protocoles de routage cessent de fonctionner en cas de charge.  
D. Parce que l’ECMP ne redistribue jamais les flux.

**8. Quelle caractéristique rend un pipeline d’automatisation réseau plus sûr ?**  
A. Envoyer toute configuration sans diff.  
B. Stocker les secrets dans le dépôt de code.  
C. Valider les données, comparer l’état, tester, approuver, déployer par étapes et vérifier après changement.  
D. Supprimer les sauvegardes pour éviter la dérive.

**9. Une capture montre des paquets et le monitoring montre une latence élevée au même moment. Que peut-on conclure ?**  
A. La capture prouve automatiquement la cause de la latence.  
B. La corrélation temporelle est utile mais nécessite de confirmer le trajet, le trafic et l’ordre causal.  
C. Il faut désactiver le monitoring.  
D. Une latence élevée implique toujours une panne physique.

**10. Quel est le rôle d’un ADR ?**  
A. Remplacer tous les schémas de réseau.  
B. Décrire contexte, options, décision, conséquences et validation d’un choix d’architecture.  
C. Stocker les mots de passe de secours.  
D. Mesurer les erreurs d’interface.

### Corrigé

1. **B** — Les risques partagés peuvent faire tomber les deux chemins simultanément.  
2. **C** — Le diagnostic suit l’information depuis la politique et la décision jusqu’au transfert et au service.  
3. **B** — L’underlay transporte les tunnels entre leurs endpoints ; l’overlay porte les services logiques.  
4. **C** — Un test de service représentatif se rapproche davantage de l’expérience réelle, à corréler avec les signaux techniques.  
5. **A** — Des timers agressifs peuvent produire des fausses détections, du flapping ou une instabilité.  
6. **B** — La VRF isole le routage mais ne fournit pas à elle seule tous les contrôles nécessaires.  
7. **B** — Une panne modifie la distribution et réduit la capacité disponible.  
8. **C** — Les garde-fous couvrent les données, le changement et la vérification du résultat.  
9. **B** — La temporalité seule ne prouve pas que les paquets observés causent la dégradation.  
10. **B** — L’ADR rend une décision compréhensible et réévaluable.


## 21. Glossaire essentiel

- **ADR** : Architecture Decision Record, document court qui conserve la justification d’une décision.
- **BFD** : mécanisme de détection rapide de défaillance entre endpoints, selon le support de la plateforme.
- **BGP** : protocole de routage à vecteur de chemin utilisé entre systèmes autonomes et dans plusieurs architectures de services.
- **Control plane** : mécanismes qui construisent et échangent les informations de routage ou de contrôle.
- **ECMP** : utilisation de plusieurs next-hops à coût égal.
- **EVPN** : famille de services Ethernet VPN avec distribution d’état via BGP.
- **FIB** : structure de transfert utilisée pour acheminer les paquets.
- **IaC** : pratiques qui représentent et valident l’infrastructure à partir de données et de code versionnés.
- **IGP** : protocole de routage interne, par exemple OSPF ou IS-IS.
- **MTU** : taille maximale d’un paquet/trame sur une liaison selon le contexte ; doit être examinée sur les chemins encapsulés.
- **Overlay** : service logique établi au-dessus d’un réseau de transport sous-jacent.
- **RIB** : base des routes connues et candidates d’un système de routage.
- **RPKI** : infrastructure permettant notamment de valider l’autorisation d’origine de préfixes IP pour le routage BGP.
- **RTO** : objectif de délai de rétablissement après une interruption.
- **SRLG** : groupe de ressources partageant un risque de panne commun.
- **SLO/SLI/SLA** : objectif, indicateur et engagement de niveau de service.
- **Underlay** : réseau de transport sous-jacent qui fournit la connectivité nécessaire à un overlay.
- **VRF** : contexte de routage distinct permettant de séparer les tables de routes.
- **VTEP/VNI** : endpoint de tunnel VXLAN et identifiant d’un segment VXLAN.


## Références techniques et normes

Les références ci-dessous permettent d’approfondir certains mécanismes. Elles ne signifient pas que tous les composants doivent être déployés dans chaque architecture ; les documents standards doivent être lus avec leur statut et leurs mises à jour.

1. **RFC 7348 — VXLAN: A Framework for Overlaying Virtualized Layer 2 Networks over Layer 3 Networks** : https://www.rfc-editor.org/rfc/rfc7348
2. **RFC 4364 — BGP/MPLS IP Virtual Private Networks (VPNs)** : https://www.rfc-editor.org/rfc/rfc4364
3. **RFC 7432 — BGP MPLS-Based Ethernet VPN**, à lire avec ses mises à jour ultérieures : https://www.rfc-editor.org/rfc/rfc7432
4. **RFC 8365 — EVPN comme Network Virtualization Overlay**, à lire avec les mises à jour correspondantes : https://www.rfc-editor.org/rfc/rfc8365
5. **RFC 9746 (mars 2025) — BGP EVPN Multihoming Extensions for Split-Horizon Filtering** : https://www.rfc-editor.org/rfc/rfc9746
6. **RFC 9552 (décembre 2023) — Distribution of Link-State and Traffic Engineering Information Using BGP** : https://www.rfc-editor.org/rfc/rfc9552
7. **RFC 9252 — BGP Overlay Services Based on Segment Routing over IPv6 (SRv6)**, avec les mises à jour publiées par le RFC Editor : https://www.rfc-editor.org/rfc/rfc9252
8. **Cisco Design Zone — High Availability Campus Network Design, Routed Access Layer** : https://www.cisco.com/c/en/us/td/docs/solutions/Enterprise/Campus/routed-ex.html

## Conclusion

Une architecture réseau experte est une collection de décisions expliquées et testées. Elle définit les frontières de panne et de confiance, les chemins normaux et de secours, les politiques, les dépendances et les preuves attendues. Elle reste assez simple pour que l’équipe sache l’exploiter, tout en satisfaisant les exigences présentes et la croissance raisonnablement anticipée. La validation finale n’est pas « le schéma paraît correct », mais « les scénarios importants ont été testés, les résultats sont mesurés et l’équipe sait quoi faire lorsque la réalité s’écarte du modèle ».
