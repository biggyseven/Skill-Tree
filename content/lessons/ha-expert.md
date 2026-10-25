# Haute disponibilité des réseaux — Niveau Expert

**Niveau :** Expert  
**Durée indicative :** 6 à 10 heures, selon les laboratoires et les analyses  
**Prérequis :** avoir étudié `ha-debutant.md` et `ha-intermediaire.md`, savoir configurer et diagnostiquer des VLAN/trunks, STP, LACP/EtherChannel, routes statiques ou dynamiques, HSRP/VRRP, suivi de route, bases de pare-feu et mesures de connectivité.  
**Environnement recommandé :** maquette virtuelle ou matériel isolé, deux hôtes clients, plusieurs nœuds réseau, serveur de test, supervision et Wireshark/tcpdump.

Ce cours constitue le troisième niveau de la série **Haute disponibilité des réseaux**. Le niveau Débutant a établi les notions de disponibilité, de redondance, de SPOF, de RTO/RPO, de bascule et de test simple. Le niveau Intermédiaire a approfondi passerelles redondantes, LACP, STP/RSTP, pare-feu stateful, split-brain, asymétrie et runbooks. Ici, la question n’est plus simplement de configurer un protocole : il faut concevoir les dépendances pour limiter les défaillances corrélées, quantifier la disponibilité observée, définir des garde-fous, tester des scénarios multi-couches et prouver qu’un service est réellement rétabli.

> **Règle d’exploitation :** aucun mécanisme n’offre une disponibilité absolue. La HA réduit la probabilité et l’impact de certaines pannes ; elle n’élimine ni les erreurs communes, ni les défauts logiciels, ni les attaques, ni la corruption de données, ni les erreurs de changement. Toute configuration de laboratoire doit être adaptée au produit, à la version et aux exigences du service.

## Objectifs pédagogiques

À la fin du cours, tu devrais pouvoir :

- établir un modèle de dépendances et identifier les défaillances corrélées ;
- comparer actif/passif, actif/actif, ECMP, multi-homing et réplication de service ;
- concevoir des critères de santé cohérents entre interface, route, session et transaction métier ;
- combiner suivi, BFD, routage, bascule de passerelle et supervision sans créer de boucles de décision ;
- expliquer les risques de split-brain, d’asymétrie, de réplication retardée et de fencing insuffisant ;
- définir des objectifs SLI/SLO, des budgets de perte et une matrice de tests ;
- planifier une migration HA avec phases, seuils d’arrêt, retour arrière et validation après changement ;
- produire un rapport d’incident argumenté par des journaux, métriques et captures.

## Comment utiliser les schémas

Les huit schémas sont des SVG intégrés directement à ce Markdown, sans fichier externe. Ils ont été composés avec une grille, une légende couleur, des libellés d’équipement et des trajectoires d’animation attachées aux connecteurs dessinés. Les marqueurs indiquent un flux logique ; ils ne représentent pas un chronométrage réel ni un comportement identique sur tous les produits. Si ton lecteur bloque les animations, la topologie reste lisible à l’arrêt. Les commandes détaillées restent dans les blocs de code : le SVG sert à comprendre l’architecture, pas à remplacer le schéma précis du matériel.


## 1. Concevoir la HA à partir du service

### 1.1 Le périmètre doit être défini avant l’architecture

Une conception commence par définir l’unité de service. « Le routeur est accessible en SSH » ne signifie pas nécessairement que les utilisateurs accèdent au portail métier. Inversement, un équipement peut être inaccessible pour la gestion mais continuer à transférer les paquets. L’objet de la HA est le service du point de vue d’un consommateur identifié.

Pour chaque service, documente :

- **Consommateur :** VLAN, site, application, API, client mobile ou système partenaire.
- **Parcours :** DNS, accès, passerelle, routage, pare-feu, répartiteur, application, dépendance de données.
- **Fonction attendue :** transaction ou flux que l’on considère comme utile.
- **Tolérance :** durée d’interruption, perte de sessions, perte de données et niveau de performance acceptable.
- **Mode de mesure :** sonde réseau, test applicatif, transaction synthétique, métriques et journalisation.
- **Frontière de responsabilité :** équipe réseau, plateforme, sécurité, application, fournisseur ou opérateur.

Un objectif de disponibilité doit toujours préciser la fenêtre de calcul, les exclusions, la source de mesure et ce qui constitue une panne. Sans cette définition, deux équipes peuvent déclarer le même incident de façon contradictoire.

### 1.2 Architecture multicouche : chaque lien doit correspondre à une dépendance vraie

<div class="lesson-figure ha-expert-figure">
<svg width="960" height="440" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 440" role="img" aria-label="1. Architecture HA multi-couches" style="width:100%;max-width:100%;display:block;font-family:Arial,Helvetica,sans-serif">
<rect width="960" height="440" rx="16" fill="#10151f"/>
<text x="24" y="29" font-size="20" font-weight="700" fill="#edf3fa">1. Architecture HA multi-couches</text>
<text x="25" y="51" font-size="12" fill="#a8b6c8">Exemple de chemins actifs multiples ; la sélection réelle dépend du protocole et de la politique.</text>
<path d="M24 65 H936" stroke="#344357" stroke-width="1.5"/>
<g><rect x="25" y="145" width="125" height="70" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="87.5" y="171" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Clients</text><text x="87.5" y="199" text-anchor="middle" font-size="11" fill="#a8b6c8">sondes + utilisateurs</text></g>
<g><rect x="190" y="90" width="150" height="70" rx="12" fill="#182231" stroke="#43c7f5" stroke-width="2"/><text x="265.0" y="116" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Accès A</text><text x="265.0" y="144" text-anchor="middle" font-size="11" fill="#a8b6c8">chemin actif A</text></g>
<g><rect x="190" y="220" width="150" height="70" rx="12" fill="#182231" stroke="#fbbf24" stroke-width="2"/><text x="265.0" y="246" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Accès B</text><text x="265.0" y="274" text-anchor="middle" font-size="11" fill="#a8b6c8">chemin actif B</text></g>
<g><rect x="390" y="90" width="150" height="70" rx="12" fill="#182231" stroke="#4ade80" stroke-width="2"/><text x="465.0" y="116" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Cœur L3 A</text><text x="465.0" y="144" text-anchor="middle" font-size="11" fill="#a8b6c8">ECMP / routage</text></g>
<g><rect x="390" y="220" width="150" height="70" rx="12" fill="#182231" stroke="#4ade80" stroke-width="2"/><text x="465.0" y="246" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Cœur L3 B</text><text x="465.0" y="274" text-anchor="middle" font-size="11" fill="#a8b6c8">ECMP / routage</text></g>
<g><rect x="590" y="145" width="145" height="75" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="662.5" y="171" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">FW cluster</text><text x="662.5" y="204" text-anchor="middle" font-size="11" fill="#a8b6c8">sessions / état</text></g>
<g><rect x="785" y="80" width="150" height="70" rx="12" fill="#182231" stroke="#43c7f5" stroke-width="2"/><text x="860.0" y="106" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">LB / service A</text><text x="860.0" y="134" text-anchor="middle" font-size="11" fill="#a8b6c8">health check</text></g>
<g><rect x="785" y="220" width="150" height="70" rx="12" fill="#182231" stroke="#43c7f5" stroke-width="2"/><text x="860.0" y="246" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">LB / service B</text><text x="860.0" y="274" text-anchor="middle" font-size="11" fill="#a8b6c8">health check</text></g>
<path d="M150 175 L170 175 L170 125 L190 125" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.3s" begin="0s" repeatCount="indefinite" path="M150 175 L170 175 L170 125 L190 125"/></circle>
<path d="M150 185 L170 185 L170 255 L190 255" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#fbbf24" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.6s" begin=".7s" repeatCount="indefinite" path="M150 185 L170 185 L170 255 L190 255"/></circle>
<path d="M340 125 L365 125 L365 125 L390 125" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.5s" begin=".2s" repeatCount="indefinite" path="M340 125 L365 125 L365 125 L390 125"/></circle>
<path d="M340 255 L365 255 L365 255 L390 255" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#fbbf24" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.8s" begin=".9s" repeatCount="indefinite" path="M340 255 L365 255 L365 255 L390 255"/></circle>
<path d="M540 125 L560 125 L560 170 L590 170" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.7s" begin=".35s" repeatCount="indefinite" path="M540 125 L560 125 L560 170 L590 170"/></circle>
<path d="M540 255 L560 255 L560 195 L590 195" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#fbbf24" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.9s" begin="1.1s" repeatCount="indefinite" path="M540 255 L560 255 L560 195 L590 195"/></circle>
<path d="M735 170 L760 170 L760 115 L785 115" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.2s" begin=".4s" repeatCount="indefinite" path="M735 170 L760 170 L760 115 L785 115"/></circle>
<path d="M735 195 L760 195 L760 255 L785 255" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#fbbf24" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.5s" begin="1.2s" repeatCount="indefinite" path="M735 195 L760 195 L760 255 L785 255"/></circle>
<text x="480" y="330" text-anchor="middle" font-size="13" font-weight="400" fill="#edf3fa">Vérifier les routes aller/retour, les contrôles de santé et l’état des sessions.</text>
<text x="480" y="352" text-anchor="middle" font-size="11" font-weight="400" fill="#fbbf24">Deux chemins dessinés ne sont indépendants que si leurs dépendances physiques et logiques le sont.</text>
<text x="480.0" y="426" text-anchor="middle" font-size="11" fill="#a8b6c8">Schéma conceptuel : les composants, les dépendances et les tests exacts dépendent de l’architecture déployée.</text>
</svg>
</div>

Le schéma représente un service passant de l’accès aux cœurs L3, puis à un cluster de sécurité et à deux chemins de service. Un réseau peut avoir plusieurs chemins dessinés tout en restant dépendant d’un seul rack, d’une seule alimentation, d’un seul service DNS, d’un seul conduit ou d’un seul plan de contrôle. Le nombre de lignes sur un dessin n’est pas une mesure de résilience.

La première activité d’architecture est donc une **analyse des dépendances**. Pour chaque composant critique, demande :

1. quel défaut peut le rendre indisponible ;
2. quel composant alternatif prend la fonction ;
3. quelles dépendances sont communes à la fonction principale et au secours ;
4. quel mécanisme détecte la panne et quelle preuve atteste la bascule ;
5. ce qui se passe si le secours est en état dégradé avant la panne ;
6. comment restaurer l’état normal sans provoquer un deuxième incident.

### 1.3 Matrice de défaillance (FMEA simplifiée)

Une FMEA (*Failure Mode and Effects Analysis*) inventorie un mode de panne, son effet, sa détection, sa réponse et sa gravité. Elle ne requiert pas obligatoirement un score numérique complexe : le but initial est d’éviter les causes oubliées.

| Élément | Mode de panne | Effet observable | Détection utile | Mécanisme possible | Risque résiduel |
|---|---|---|---|---|---|
| Lien d’accès | Perte physique | Port down | État interface + sonde client | Deuxième uplink / LACP | Chemins communs ou capacité réduite |
| Route amont | Retrait ou voisin perdu | Sous-réseaux distants injoignables | Table de routes, BFD, sonde | Convergence L3 | Route de retour incorrecte |
| Passerelle | Nœud actif en panne | Perte de sortie LAN | Protocole FHRP + test service | HSRP/VRRP | Le contrôle peut basculer sans vraie route utile |
| Pare-feu | Nœud actif perdu | Sessions coupées | État HA + test TCP | Cluster stateful | État non synchronisé |
| DNS/GSLB | Mauvaise réponse ou cache | Utilisateur dirigé vers un site indisponible | Résolution + transaction | Réponse de secours | Caches et connexions persistantes |
| Stockage | Réplication en retard | Données obsolètes ou indisponibles | Lag, erreurs I/O, cohérence | Réplication/quorum | Perte ou divergence de données |
| Plan de gestion | Contrôleur/AAA indisponible | Changements ou accès admin bloqués | Supervision hors bande | Contrôle secondaire | Perte de visibilité pendant incident |

Pour chaque entrée, ajoute un propriétaire, un runbook, un test validé et une date de dernière exécution. Une ligne sans mécanisme de détection ou sans test est une dette de résilience.

### 1.4 Redondance indépendante contre défaillance commune

Deux équipements peuvent partager le même défaut logiciel, les mêmes identifiants compromis, la même alimentation, le même hyperviseur, la même carte, le même opérateur ou le même pipeline de déploiement. La redondance ne réduit pas automatiquement ces risques.

Un contrôle de conception doit donc examiner au minimum :

- **Physique :** racks, PDU, alimentation, câblage, fibres, conduits, salle et site.
- **Réseau :** accès, cœur, protocoles, adressage de gestion, plan de routage, liens de synchronisation.
- **Plateforme :** versions, mises à jour, licences, hyperviseur, orchestration et images.
- **Données :** réplication, cohérence, sauvegardes, clés, certificats et procédures de restauration.
- **Opérations :** gestion de changement, automatisation, comptes, secrets, supervision et documentation.

L’indépendance doit être prouvée. Deux liens qui traversent le même conduit n’offrent pas une diversité physique complète ; deux instances déployées depuis la même configuration erronée peuvent tomber ensemble.


## 2. Choisir un modèle d’activation et de capacité

### 2.1 Actif/passif

Un nœud principal traite le trafic ou détient la ressource ; un secours attend ou reste prêt à reprendre le rôle. Ce modèle réduit parfois la complexité de partage d’état, mais le secours doit être suffisamment dimensionné et continuellement vérifié. Un secours qui n’a jamais été testé peut être obsolète : configuration ancienne, certificat expiré, licence absente, table de routage différente ou capacité insuffisante.

**Avantages :** rôle simple à expliquer, panne active plus facile à isoler, possibilité de limiter l’écriture concurrente.

**Contraintes :** ressources de secours potentiellement sous-utilisées, reprise pouvant interrompre les sessions, besoin d’un mécanisme d’élection et de fencing, validation du retour du nœud préféré.

### 2.2 Actif/actif

Plusieurs nœuds servent simultanément les requêtes. Le gain de capacité s’accompagne de contraintes : distribution de charge, affinité de session, cohérence des données, gestion d’état partagé et retrait rapide d’un nœud non sain.

Il faut distinguer trois notions souvent confondues :

1. **Actif/actif de trafic :** plusieurs nœuds transfèrent ou traitent des flux.
2. **Actif/actif de contrôle :** plusieurs nœuds participent aux décisions.
3. **Actif/actif de données :** plusieurs nœuds acceptent des opérations sur un jeu de données partagé/répliqué.

Un load balancer actif/actif ne rend pas automatiquement la base de données active/active. Chaque couche possède sa propre sémantique de disponibilité.

### 2.3 ECMP et redondance L3

ECMP (*Equal-Cost Multi-Path*) permet à un routeur de conserver plusieurs next-hops de coût égal vers une destination, selon le protocole, la plate-forme et la politique. Plusieurs chemins peuvent être utilisés simultanément. Toutefois, la panne d’un next-hop peut modifier le hachage et réinitialiser certaines sessions si le chemin est stateful ou si les ressources intermédiaires ne sont pas équivalentes.

À vérifier dans un design ECMP :

- les chemins sont-ils réellement de coût égal et ont-ils une capacité suffisante ?
- la table de forwarding contient-elle les next-hops attendus ?
- le hachage est-il stable pour les flux ?
- un pare-feu stateful voit-il les deux directions ?
- comment sont traitées les routes retour et les annonces asymétriques ?
- le retrait d’un chemin est-il observé par toutes les couches requises ?

### 2.4 Capacité après panne (N-1 et N+1)

Le test N-1 estime si le service supporte la perte d’un composant prévu sans dépasser les limites de capacité définies. Le nom seul ne suffit pas : précise l’unité (lien, châssis, site, alimentation ou nœud applicatif) et le scénario de charge.

Exemple : trois liens de 10 Gbit/s ne permettent pas d’affirmer que le réseau dispose de 30 Gbit/s de capacité utile. Il faut tenir compte de la distribution par flux, des équipements aux extrémités, de la congestion, des politiques de QoS, du trafic de réplication et du comportement après la perte d’un membre.

Calcule la demande de pointe, la marge, la capacité après défaillance et la charge transférée. Si la perte d’un membre surcharge les autres, la panne peut déclencher un effet en chaîne (congestion, timeouts, nouveaux essais applicatifs, charge serveur accrue).

### 2.5 Tableau de choix rapide

| Modèle | Convient notamment si… | Vigilance principale |
|---|---|---|
| Actif/passif | la ressource ne doit avoir qu’un propriétaire à la fois | fencing, état du secours, temps de bascule |
| Actif/actif | les requêtes peuvent être distribuées et la cohérence est définie | session affinity, données partagées, asymétrie |
| ECMP | plusieurs next-hops L3 équivalents peuvent transporter le trafic | convergence, hachage, état des équipements intermédiaires |
| Cluster stateful | les sessions et politiques doivent survivre à certaines pannes | synchronisation, latence, compatibilité des états |
| Multi-site/GSLB | la reprise du site entier est nécessaire | données, DNS TTL, connectivité et gouvernance des sites |


## 3. Passerelles redondantes et tracking expert

### 3.1 Distinguer la santé d’un rôle de la santé du service

<div class="lesson-figure ha-expert-figure">
<svg width="900" height="380" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 380" role="img" aria-label="2. Passerelle : rôle de contrôle vs chemin utile" style="width:100%;max-width:100%;display:block;font-family:Arial,Helvetica,sans-serif">
<rect width="900" height="380" rx="16" fill="#10151f"/>
<text x="24" y="29" font-size="20" font-weight="700" fill="#edf3fa">2. Passerelle : rôle de contrôle vs chemin utile</text>
<text x="25" y="51" font-size="12" fill="#a8b6c8">Un équipement actif peut avoir perdu la connectivité amont : le tracking doit couvrir la panne visée.</text>
<path d="M24 65 H876" stroke="#344357" stroke-width="1.5"/>
<g><rect x="35" y="145" width="150" height="72" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="110.0" y="171" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Hôtes</text><text x="110.0" y="201" text-anchor="middle" font-size="11" fill="#a8b6c8">passerelle virtuelle</text></g>
<g><rect x="285" y="82" width="180" height="72" rx="12" fill="#182231" stroke="#4ade80" stroke-width="2"/><text x="375.0" y="108" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">GW-A · ACTIF</text><text x="375.0" y="138" text-anchor="middle" font-size="11" fill="#a8b6c8">priorité 110</text></g>
<g><rect x="285" y="230" width="180" height="72" rx="12" fill="#182231" stroke="#fbbf24" stroke-width="2"/><text x="375.0" y="256" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">GW-B · SECOURS</text><text x="375.0" y="286" text-anchor="middle" font-size="11" fill="#a8b6c8">priorité 100</text></g>
<g><rect x="650" y="145" width="205" height="72" rx="12" fill="#182231" stroke="#43c7f5" stroke-width="2"/><text x="752.5" y="171" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Cible amont</text><text x="752.5" y="201" text-anchor="middle" font-size="11" fill="#a8b6c8">route / service réel</text></g>
<path d="M185 168 L235 168 L235 118 L285 118" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.3s" begin="0s" repeatCount="indefinite" path="M185 168 L235 168 L235 118 L285 118"/></circle>
<path d="M185 194 L235 194 L235 266 L285 266" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 6"/>

<path d="M465 118 L535 118 L535 160 L650 160" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.2s" begin=".2s" repeatCount="indefinite" path="M465 118 L535 118 L535 160 L650 160"/></circle>
<path d="M465 266 L555 266 L555 205 L650 205" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 6"/>

<text x="450" y="330" text-anchor="middle" font-size="12" font-weight="400" fill="#edf3fa">Signal de détection possible : interface, route suivie ou sonde IP SLA.</text>
<text x="450" y="349" text-anchor="middle" font-size="11" font-weight="400" fill="#fbbf24">Le seuil et la destination de sonde doivent éviter de masquer la panne à détecter.</text>
<text x="450.0" y="366" text-anchor="middle" font-size="11" fill="#a8b6c8">HSRP/VRRP gère le rôle de passerelle ; il ne garantit pas, à lui seul, la santé applicative.</text>
</svg>
</div>

HSRP, VRRP ou une technologie équivalente assure le transfert de responsabilité pour une passerelle virtuelle selon une logique d’élection. Ce mécanisme ne valide pas à lui seul la chaîne de routage, le DNS, la sécurité ou l’application. Si la priorité reste élevée après la perte d’un réseau amont, les hôtes peuvent continuer à envoyer vers une passerelle active mais inutile.

### 3.2 Une sonde doit mesurer ce qu’on veut protéger

Une sonde vers le voisin directement connecté prouve la joignabilité de ce voisin ; elle ne prouve pas que la destination utile est joignable. À l’inverse, une sonde vers un serveur externe peut échouer pour une raison indépendante de la route qu’on veut surveiller. Les sondes doivent être conçues comme des tests discriminants.

Définis :

- **Cible :** la destination ou le comportement dont dépend réellement le service.
- **Chemin de la sonde :** interface source, VRF, route, DSCP et éventuel NAT utilisés.
- **Fréquence et timeout :** délai de détection compatible avec les faux positifs et le budget de panne.
- **Seuil de déclenchement :** nombre de réponses perdues, délai de maintien et éventuelle hystérésis.
- **Action :** changement de priorité, retrait de route, bascule de pool ou alerte, selon la responsabilité définie.
- **Validation :** un second test indépendant qui confirme la reprise depuis le point consommateur.

Ne fais pas piloter simultanément une bascule par plusieurs sondes dont les actions s’alimentent mutuellement. Par exemple, une sonde qui change la route peut ensuite rendre sa propre cible inaccessible et provoquer un ping-pong. Dessine les dépendances de contrôle aussi soigneusement que les chemins de données.

### 3.3 Préemption et stabilité

Une préemption automatique peut restaurer le chemin nominal à la remise sous tension, mais si le nœud revenu est encore instable, la préemption provoque une deuxième bascule. Une temporisation, la validation de la route amont ou une reprise manuelle peuvent être préférables pour certains services.

La bonne politique varie selon l’application : pour un service sans état, un retour rapide peut être acceptable ; pour des sessions longues ou une ressource exclusive, la stabilité et la cohérence de l’état peuvent primer sur le retour immédiat au nœud préféré.

### 3.4 Commandes de vérification Cisco

Exemples usuels, à adapter aux versions réellement utilisées :

```text
show standby brief
show standby
show ip route
show ip cef <destination>
show track
show ip sla statistics
show logging
```

Une sortie montrant « Active » ne prouve pas l’accès à la cible métier. Complète-la avec un test depuis un client et des traces horodatées. Selon le matériel, des variantes IPv6 et des sous-commandes différentes seront nécessaires.


## 4. Détection de panne et convergence de routage

### 4.1 Les signaux ne sont pas interchangeables

Un lien physique `up`, un voisin de routage établi, une session BFD active, une route installée et une application qui répond représentent des niveaux différents. Il est dangereux de prendre l’un pour une preuve de tous les autres.

- **État physique :** lumière, porteuse, erreurs, optique, LACP, interface.
- **Adjacence de contrôle :** voisin OSPF/BGP ou protocole de passerelle.
- **Détection de forwarding :** BFD ou mécanisme équivalent lorsqu’il est pris en charge.
- **RIB/FIB :** route connue dans le plan de contrôle et installée dans le plan de transfert.
- **Test de service :** échange applicatif, transaction, résolution DNS et réponse.

### 4.2 BFD : utile, mais à calibrer

Bidirectional Forwarding Detection (BFD) vise à détecter rapidement certaines défaillances du chemin bidirectionnel entre moteurs de transfert. Le protocole est indépendant des protocoles de routage, mais son intégration au routage dépend des capacités du produit. Les timers négociés et la charge de la plate-forme influencent le comportement réel.

Un intervalle agressif ne signifie pas une meilleure disponibilité si le CPU, le transport ou les mécanismes de contrôle ne peuvent pas garantir ce rythme. Des faux positifs peuvent faire tomber une adjacence pourtant utilisable, provoquer des bascules répétées et ajouter de la congestion au moment où le réseau est déjà dégradé.

### Schéma 3 — BFD et convergence

<div class="lesson-figure ha-expert-figure">
<svg width="900" height="390" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 390" role="img" aria-label="3. Détection rapide : BFD + protocole de routage" style="width:100%;max-width:100%;display:block;font-family:Arial,Helvetica,sans-serif">
<rect width="900" height="390" rx="16" fill="#10151f"/>
<text x="24" y="29" font-size="20" font-weight="700" fill="#edf3fa">3. Détection rapide : BFD + protocole de routage</text>
<text x="25" y="51" font-size="12" fill="#a8b6c8">BFD peut signaler rapidement une défaillance de chemin ; l’effet dépend du protocole et de l’implémentation.</text>
<path d="M24 65 H876" stroke="#344357" stroke-width="1.5"/>
<g><rect x="35" y="130" width="145" height="70" rx="12" fill="#182231" stroke="#43c7f5" stroke-width="2"/><text x="107.5" y="156" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">R1</text><text x="107.5" y="184" text-anchor="middle" font-size="11" fill="#a8b6c8">routeur de bord</text></g>
<g><rect x="275" y="75" width="165" height="70" rx="12" fill="#182231" stroke="#4ade80" stroke-width="2"/><text x="357.5" y="101" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">R2</text><text x="357.5" y="129" text-anchor="middle" font-size="11" fill="#a8b6c8">chemin préféré</text></g>
<g><rect x="275" y="235" width="165" height="70" rx="12" fill="#182231" stroke="#fbbf24" stroke-width="2"/><text x="357.5" y="261" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">R3</text><text x="357.5" y="289" text-anchor="middle" font-size="11" fill="#a8b6c8">chemin de secours</text></g>
<g><rect x="635" y="150" width="220" height="70" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="745.0" y="176" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Réseau / service</text><text x="745.0" y="204" text-anchor="middle" font-size="11" fill="#a8b6c8">destination testée</text></g>
<path d="M180 155 L230 155 L230 110 L275 110" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.2s" begin="0s" repeatCount="indefinite" path="M180 155 L230 155 L230 110 L275 110"/></circle>
<path d="M180 180 L230 180 L230 270 L275 270" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 6"/>

<path d="M440 110 L520 110 L520 170 L635 170" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.3s" begin=".2s" repeatCount="indefinite" path="M440 110 L520 110 L520 170 L635 170"/></circle>
<path d="M440 270 L540 270 L540 200 L635 200" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 6"/>

<text x="450" y="330" text-anchor="middle" font-size="12" font-weight="400" fill="#edf3fa">Chronologie à mesurer : détection → retrait/ajustement de route → convergence → reprise applicative.</text>
<text x="450" y="350" text-anchor="middle" font-size="11" font-weight="400" fill="#fbbf24">Des timers très agressifs peuvent provoquer des faux positifs si le transport ou le CPU est instable.</text>
<text x="450.0" y="376" text-anchor="middle" font-size="11" fill="#a8b6c8">BFD n’est pas un protocole de routage et ne prouve pas que toute l’application fonctionne.</text>
</svg>
</div>

Le chemin vert représente l’option préférée et le jaune une option de secours. Le mécanisme de détection peut accélérer la signalisation de panne ; il ne remplace pas l’analyse de la route, du transfert réel ou de la réponse applicative.

### 4.3 Routage dynamique : stratégies de convergence

Pour une architecture OSPF ou BGP, définis les événements qui doivent retirer un chemin : perte physique, expiration de voisin, échec BFD, changement de politique ou alerte de service. Ces événements n’ont pas tous le même coût et ne doivent pas être associés à des actions sans évaluer les conséquences.

**OSPF :** examiner l’adjacence, la base d’état de liens, les coûts, les timers et l’installation dans la FIB. Un voisin rétabli ne garantit pas que la bonne route soit préférée.

**BGP :** examiner la session, les annonces reçues, les attributs, les politiques d’import/export, la meilleure route et la propagation vers les voisins. La disponibilité d’une session BGP ne prouve pas que le préfixe utile est annoncé correctement.

**ECMP :** confirmer la liste des next-hops, le retrait d’un membre, le hachage et la réaction des sessions. Les chemins de coût égal sont une décision de routage ; ils ne valident pas l’équivalence de sécurité et d’état le long de chaque chemin.

### 4.4 Mesurer la convergence correctement

Enregistre au moins :

1. l’heure de la défaillance injectée ;
2. le premier signal détectant la panne ;
3. le changement de rôle ou d’adjacence ;
4. la modification RIB puis FIB si observable ;
5. la première réponse réseau après bascule ;
6. la première transaction applicative réussie ;
7. le temps de stabilisation après la reprise.

La différence entre le premier ping reçu et le retour du service métier doit être expliquée. Des caches DNS, une session TCP, un état NAT ou un pool applicatif peuvent retarder la récupération même si le plan de transfert a convergé.


## 5. Multichâssis, MLAG et multi-homing

### 5.1 La redondance de châssis exige un modèle de coordination

Des technologies telles que MLAG, vPC, les agrégats multi-châssis ou EVPN multihoming permettent, selon le produit, d’attacher un équipement à plusieurs commutateurs tout en présentant une topologie logique cohérente. Elles ne sont pas interchangeables et ne partagent pas nécessairement le même modèle de contrôle.

Le design doit documenter :

- rôle et état du lien de pair/peer-link ;
- canal de keepalive ou mécanisme indépendant de détection ;
- comportement lorsqu’un membre, le peer-link ou le canal de contrôle échoue ;
- règle empêchant deux membres de devenir des propriétaires incompatibles ;
- cohérence des configurations LACP, VLAN, MTU et paramètres de routage ;
- conséquences pour les MAC, les tables de transfert et les flux existants ;
- procédure de reconstruction du pair après un redémarrage prolongé.

### Schéma 4 — Attachement double et contrôle du pair

<div class="lesson-figure ha-expert-figure">
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="420" viewBox="0 0 960 420" role="img" aria-label="4. Multi-homing : agrégat, peer-link et risque split-brain" style="width:100%;max-width:100%;display:block;font-family:Arial,Helvetica,sans-serif">
<rect width="960" height="420" rx="16" fill="#10151f"/>
<text x="24" y="29" font-size="20" font-weight="700" fill="#edf3fa">4. Multi-homing : agrégat, peer-link et risque split-brain</text>
<text x="25" y="51" font-size="12" fill="#a8b6c8">Deux chemins de données vers deux châssis coordonnés ; le peer-link transporte le contrôle/la synchronisation selon le produit.</text>
<path d="M24 65 H936" stroke="#344357" stroke-width="1.5"/>
<g><rect x="30" y="168" width="160" height="78" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="110" y="195" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Serveur / accès</text><text x="110" y="228" text-anchor="middle" font-size="11" fill="#a8b6c8">LACP multi-châssis</text></g>
<g><rect x="280" y="80" width="190" height="78" rx="12" fill="#182231" stroke="#4ade80" stroke-width="2"/><text x="375" y="106" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Leaf / châssis A</text><text x="375" y="140" text-anchor="middle" font-size="11" fill="#a8b6c8">membre du pair</text></g>
<g><rect x="280" y="255" width="190" height="78" rx="12" fill="#182231" stroke="#43c7f5" stroke-width="2"/><text x="375" y="281" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Leaf / châssis B</text><text x="375" y="315" text-anchor="middle" font-size="11" fill="#a8b6c8">membre du pair</text></g>
<g><rect x="710" y="165" width="200" height="78" rx="12" fill="#182231" stroke="#fbbf24" stroke-width="2"/><text x="810" y="192" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Fabric amont</text><text x="810" y="225" text-anchor="middle" font-size="11" fill="#a8b6c8">chemins L3</text></g>
<path d="M190 187 L235 187 L235 119 L280 119" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.3s" begin="0s" repeatCount="indefinite" path="M190 187 L235 187 L235 119 L280 119"/></circle>
<path d="M190 225 L235 225 L235 294 L280 294" fill="none" stroke="#43c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#43c7f5" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.7s" begin=".7s" repeatCount="indefinite" path="M190 225 L235 225 L235 294 L280 294"/></circle>
<path d="M470 119 L610 119 L610 188 L710 188" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.4s" begin=".2s" repeatCount="indefinite" path="M470 119 L610 119 L610 188 L710 188"/></circle>
<path d="M470 294 L610 294 L610 220 L710 220" fill="none" stroke="#43c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#43c7f5" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.8s" begin="1s" repeatCount="indefinite" path="M470 294 L610 294 L610 220 L710 220"/></circle>
<path d="M470 137 L535 137 L535 274 L470 274" fill="none" stroke="#c4b5fd" stroke-width="2.5" stroke-dasharray="6 5" stroke-linecap="round" stroke-linejoin="round"/>
<text x="550" y="205" font-size="11" fill="#c4b5fd">peer-link / sync</text>
<text x="480" y="365" text-anchor="middle" font-size="12" fill="#edf3fa">En actif/actif, les deux liens peuvent transporter des flux si la plateforme et le design le permettent.</text>
<text x="480" y="386" text-anchor="middle" font-size="11" fill="#fb7185">Teste séparément la perte d’un membre, du peer-link et du canal keepalive ; vérifie le mécanisme anti split-brain.</text>
<text x="480" y="408" text-anchor="middle" font-size="11" fill="#a8b6c8">Les termes MLAG, vPC et EVPN multihoming désignent des modèles différents : consulte le guide du produit.</text>
</svg>
</div>

Le dessin est conceptuel : les noms « peer-link » et « contrôle » peuvent correspondre à des liens ou fonctions différents selon l’implémentation. Ne suppose pas que la perte d’un seul canal déclenche le même comportement sur tous les systèmes. Lis le scénario de défaillance du fournisseur.

### 5.2 Risque split-brain

Le split-brain survient lorsque des membres supposés se coordonner prennent simultanément des décisions exclusives ou incompatibles. Dans un réseau, cela peut affecter les adresses virtuelles, les tables MAC, les agrégats ou le transfert. Dans les clusters de données, il peut produire des écritures concurrentes et compromettre la cohérence.

La prévention peut combiner quorum, témoin, fencing, lease, isolation de ressources et règles de propriété. Aucun de ces mots ne doit être utilisé comme simple case à cocher : la question centrale est **comment empêcher l’ancien propriétaire de continuer à modifier la ressource après qu’un nouveau propriétaire a été élu ?**

### 5.3 Quorum et fencing

Un quorum sert à déterminer si un ensemble de membres dispose d’une majorité ou des conditions nécessaires pour agir. Un témoin peut influencer ce calcul, mais sa présence ne garantit pas le fencing. Le fencing est le mécanisme qui retire réellement l’accès à l’ancien propriétaire (par exemple une ressource partagée, un port, un volume ou une capacité d’écriture), selon le système.

Si le réseau de heartbeat est isolé mais que les deux nœuds voient toujours le stockage, chacun peut croire que l’autre est mort. Sans une politique qui empêche une double écriture, une élection à elle seule ne suffit pas.

### Schéma 5 — Décision, quorum et ressource exclusive

<div class="lesson-figure ha-expert-figure">
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="410" viewBox="0 0 960 410" role="img" aria-label="5. Split-brain : quorum et fencing" style="width:100%;max-width:100%;display:block;font-family:Arial,Helvetica,sans-serif">
<rect width="960" height="410" rx="16" fill="#10151f"/>
<text x="24" y="29" font-size="20" font-weight="700" fill="#edf3fa">5. Split-brain : quorum et fencing</text>
<text x="25" y="51" font-size="12" fill="#a8b6c8">Une ressource exclusive doit avoir un seul propriétaire autorisé ; une élection seule ne neutralise pas l’ancien propriétaire.</text>
<path d="M24 65 H936" stroke="#344357" stroke-width="1.5"/>
<g><rect x="35" y="135" width="160" height="78" rx="12" fill="#182231" stroke="#4ade80" stroke-width="2"/><text x="115" y="161" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Nœud A</text><text x="115" y="195" text-anchor="middle" font-size="11" fill="#a8b6c8">propriétaire actif</text></g>
<g><rect x="350" y="78" width="180" height="76" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="440" y="104" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Témoin / quorum</text><text x="440" y="136" text-anchor="middle" font-size="11" fill="#a8b6c8">autorise une décision</text></g>
<g><rect x="350" y="245" width="180" height="76" rx="12" fill="#182231" stroke="#43c7f5" stroke-width="2"/><text x="440" y="271" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Nœud B</text><text x="440" y="303" text-anchor="middle" font-size="11" fill="#a8b6c8">candidat, pas propriétaire</text></g>
<g><rect x="610" y="258" width="105" height="58" rx="10" fill="#30202a" stroke="#fb7185" stroke-width="2"/><text x="662.5" y="282" text-anchor="middle" font-size="12" font-weight="700" fill="#ffe4e6">Fencing</text><text x="662.5" y="300" text-anchor="middle" font-size="10" fill="#fecdd3">non confirmé</text></g>
<g><rect x="760" y="135" width="170" height="78" rx="12" fill="#182231" stroke="#fbbf24" stroke-width="2"/><text x="845" y="161" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Ressource</text><text x="845" y="195" text-anchor="middle" font-size="11" fill="#a8b6c8">écriture exclusive</text></g>
<path d="M195 154 L270 154 L270 116 L350 116" fill="none" stroke="#c4b5fd" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.3" fill="#c4b5fd" stroke="#f8fafc" stroke-width="1.2"><animateMotion dur="2.6s" begin="0s" repeatCount="indefinite" path="M195 154 L270 154 L270 116 L350 116"/></circle>
<path d="M350 285 L270 285 L270 194 L195 194" fill="none" stroke="#c4b5fd" stroke-width="2" stroke-dasharray="5 5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M195 174 L235 174 L235 174 L760 174" fill="none" stroke="#4ade80" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.8" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.4s" begin=".25s" repeatCount="indefinite" path="M195 174 L235 174 L235 174 L760 174"/></circle>
<path d="M530 285 L610 285" fill="none" stroke="#fb7185" stroke-width="3" stroke-dasharray="6 5" stroke-linecap="round"/>
<path d="M721 275 L741 295 M741 275 L721 295" fill="none" stroke="#fb7185" stroke-width="4" stroke-linecap="round"/>
<text x="662" y="240" text-anchor="middle" font-size="11" fill="#fb7185">accès bloqué tant que le fencing n’est pas confirmé</text>
<text x="480" y="348" text-anchor="middle" font-size="12" fill="#edf3fa">Le nœud B ne doit pas écrire tant que l’autorité de l’ancien propriétaire n’a pas été retirée.</text>
<text x="480" y="369" text-anchor="middle" font-size="11" fill="#fbbf24">Le mécanisme de quorum/fencing doit être défini par le produit ; ce schéma montre l’invariant de sécurité.</text>
<text x="480" y="393" text-anchor="middle" font-size="11" fill="#a8b6c8">Si le nœud A peut toujours écrire, l’élection du nœud B ne suffit pas à prévenir la divergence.</text>
</svg>
</div>

Dans un système distribué, la ressource protégée doit avoir une règle de propriété explicite. Le schéma ne constitue pas une implémentation de quorum : c’est le modèle logique à vérifier dans le guide du cluster utilisé.

### 5.4 Diagnostiquer un multi-homing instable

Collecte avant toute action destructive :

- état du pair, timers, keepalive et peer-link ;
- état LACP sur les deux extrémités ;
- événements STP et changements MAC ;
- annonces de routes et next-hops installés ;
- journaux horodatés des deux châssis ;
- configuration effective et écarts de version ;
- résultat d’un test client et d’un flux retour.

Ne force pas arbitrairement les deux équipements en mode actif. Si la plateforme fournit une commande de récupération, suis le runbook du fournisseur, car la remise en service peut affecter les tables et les flux.


## 6. Pare-feu stateful et état de session

### 6.1 La haute disponibilité du forwarding ne garantit pas la continuité TCP

Un pare-feu stateful maintient un état par connexion ou flux, par exemple les adresses, ports, directions, timers, translation et étapes de protocole selon le produit. Le nœud de secours doit recevoir ou reconstruire un ensemble d’informations compatible pour traiter les paquets d’une session existante après bascule.

Le mécanisme de réplication peut être synchrone, asynchrone, partiel ou limité par type de session. La perte d’un flux de synchronisation peut donc affecter les sessions même si le heartbeat reste opérationnel, ou l’inverse. Il faut mesurer les deux signaux séparément.

### Schéma 6 — Cluster stateful

<div class="lesson-figure ha-expert-figure">
<svg width="960" height="410" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 410" role="img" aria-label="6. Pare-feu stateful : trafic et réplication de session" style="width:100%;max-width:100%;display:block;font-family:Arial,Helvetica,sans-serif">
<rect width="960" height="410" rx="16" fill="#10151f"/>
<text x="24" y="29" font-size="20" font-weight="700" fill="#edf3fa">6. Pare-feu stateful : trafic et réplication de session</text>
<text x="25" y="51" font-size="12" fill="#a8b6c8">Un cluster n’est pas validé uniquement par son état actif/secours.</text>
<path d="M24 65 H936" stroke="#344357" stroke-width="1.5"/>
<g><rect x="30" y="150" width="135" height="70" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="97.5" y="176" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">WAN</text><text x="97.5" y="204" text-anchor="middle" font-size="11" fill="#a8b6c8">clients externes</text></g>
<g><rect x="265" y="70" width="190" height="80" rx="12" fill="#182231" stroke="#4ade80" stroke-width="2"/><text x="360.0" y="96" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">FW-A · ACTIF</text><text x="360.0" y="134" text-anchor="middle" font-size="11" fill="#a8b6c8">table de sessions</text></g>
<g><rect x="265" y="245" width="190" height="80" rx="12" fill="#182231" stroke="#fbbf24" stroke-width="2"/><text x="360.0" y="271" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">FW-B · SECOURS</text><text x="360.0" y="309" text-anchor="middle" font-size="11" fill="#a8b6c8">état répliqué</text></g>
<g><rect x="650" y="150" width="145" height="70" rx="12" fill="#182231" stroke="#43c7f5" stroke-width="2"/><text x="722.5" y="176" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Réseau LAN</text><text x="722.5" y="204" text-anchor="middle" font-size="11" fill="#a8b6c8">serveurs</text></g>
<g><rect x="820" y="150" width="110" height="70" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="875.0" y="176" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Application</text><text x="875.0" y="204" text-anchor="middle" font-size="11" fill="#a8b6c8">API / TCP</text></g>
<path d="M165 173 L215 173 L215 110 L265 110" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2s" begin="0s" repeatCount="indefinite" path="M165 173 L215 173 L215 110 L265 110"/></circle>
<path d="M455 110 L520 110 L520 175 L650 175" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.3s" begin=".2s" repeatCount="indefinite" path="M455 110 L520 110 L520 175 L650 175"/></circle>
<path d="M165 195 L215 195 L215 285 L265 285" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 6"/>

<path d="M455 285 L540 285 L540 195 L650 195" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 6"/>

<path d="M795 185 L820 185" fill="none" stroke="#43c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#43c7f5" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="1.8s" begin=".4s" repeatCount="indefinite" path="M795 185 L820 185"/></circle>
<path d="M360 150 L360 245" fill="none" stroke="#c4b5fd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="5 5"/>
<text x="380" y="205" text-anchor="start" font-size="10" font-weight="400" fill="#c4b5fd">synchronisation</text>
<text x="480" y="352" text-anchor="middle" font-size="12" font-weight="400" fill="#edf3fa">Après la bascule, tester les nouvelles connexions ET les sessions existantes.</text>
<text x="480.0" y="396" text-anchor="middle" font-size="11" fill="#a8b6c8">La synchronisation exacte dépend du produit, de sa configuration et du type d’état maintenu.</text>
</svg>
</div>

Le chemin de données est distinct de la synchronisation de session. Après une bascule, vérifie :

- nouvelles connexions TCP/UDP ;
- sessions établies avant la bascule ;
- trafic initié dans chaque direction ;
- translations NAT et sessions liées ;
- VPN/associations cryptographiques si pertinentes ;
- routes, ARP/NDP et annonces d’adresses virtuelles ;
- métriques et alertes de synchronisation.

### 6.2 Asymétrie de routage

Un chemin aller et un chemin retour différents peuvent fonctionner si l’architecture l’accepte. Mais un pare-feu stateful qui ne voit qu’une moitié du flux peut rejeter les paquets ou considérer la session invalide. Il faut comprendre le comportement d’état du produit et la politique de routage, notamment lorsque plusieurs chemins ECMP, plusieurs pare-feu ou du NAT sont impliqués.

### 6.3 Synchronisation et charge

Un lien de synchronisation surchargé ou trop latent peut accumuler du retard. Lorsqu’une bascule survient, l’état du secours peut être incomplet. Une conception doit spécifier la capacité du canal, la priorité du trafic de contrôle, la supervision du retard et le comportement en cas de perte de synchronisation.

Le test n’est pas seulement « le cluster affiche synchronized ». Il faut injecter une charge représentative, vérifier l’état au moment de la bascule et mesurer quelles sessions sont conservées. Précise dans les critères si une reconnexion automatique acceptable suffit, ou si la continuité stricte des sessions est exigée.


## 7. Haute disponibilité applicative et multi-site

### 7.1 Une sonde doit tester le parcours métier

Un port TCP ouvert peut indiquer qu’un processus écoute, sans garantir que la transaction métier est disponible. Un endpoint de health check peut réussir sur une instance qui n’accède plus à sa base ou à son système d’authentification. Les sondes doivent varier selon leur fonction : processus, dépendance, requête de lecture, transaction synthétique et test externe depuis un client.

Sépare les niveaux de contrôle de santé :

1. **Processus :** l’application est lancée.
2. **Instance :** l’instance peut recevoir une requête simple.
3. **Dépendances :** DNS, base, files, authentification et stockage sont joignables.
4. **Transaction :** une opération représentative réussit.
5. **Perspective client :** le service est accessible par le chemin normalement utilisé.

Un health check trop superficiel maintient un nœud hors service dans le pool. Un health check trop agressif peut sortir les instances pendant une courte surcharge et amplifier la panne. Choisis les timeouts, nombres d’échecs, délais de récupération et mécanismes de dégradation progressive à partir des objectifs réels.

### 7.2 Active/active et affinité de session

Les répartiteurs de charge peuvent distribuer les connexions selon diverses politiques. Si l’application conserve son état local dans la mémoire d’une instance, une requête suivante envoyée à un autre nœud peut échouer. L’affinité de session est une réponse possible, mais elle peut réduire la flexibilité de la répartition et ne remplace pas la conception d’état partagé ou de jetons autoportants.

Le passage actif/actif demande une stratégie pour :

- sessions et cookies ;
- migrations et versions de l’application ;
- migrations de schéma de base ;
- files d’attente, tâches planifiées et opérations exclusives ;
- identifiants idempotents et répétition des requêtes ;
- vidage (drain) d’une instance avant retrait du pool ;
- rétrogradation d’une dépendance et limitation du rayon d’impact.

### 7.3 Multi-site et DNS/GSLB

Une stratégie DNS/GSLB peut orienter un client vers un site choisi selon une politique et des sondes. Les caches DNS, le TTL, les résolveurs intermédiaires, les connexions persistantes et la logique de sélection de destination empêchent souvent d’obtenir une bascule instantanée universelle.

<div class="lesson-figure ha-expert-figure">
<svg width="960" height="420" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 420" role="img" aria-label="7. HA multi-site : DNS/GSLB et santé réelle" style="width:100%;max-width:100%;display:block;font-family:Arial,Helvetica,sans-serif">
<rect width="960" height="420" rx="16" fill="#10151f"/>
<text x="24" y="29" font-size="20" font-weight="700" fill="#edf3fa">7. HA multi-site : DNS/GSLB et santé réelle</text>
<text x="25" y="51" font-size="12" fill="#a8b6c8">Un changement DNS n’est pas instantané partout : caches, TTL, clients et connexions persistantes comptent.</text>
<path d="M24 65 H936" stroke="#344357" stroke-width="1.5"/>
<g><rect x="25" y="170" width="130" height="70" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="90.0" y="196" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Clients</text><text x="90.0" y="224" text-anchor="middle" font-size="11" fill="#a8b6c8">résolution DNS</text></g>
<g><rect x="220" y="170" width="160" height="70" rx="12" fill="#182231" stroke="#43c7f5" stroke-width="2"/><text x="300.0" y="196" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">DNS / GSLB</text><text x="300.0" y="224" text-anchor="middle" font-size="11" fill="#a8b6c8">choix de site</text></g>
<g><rect x="470" y="75" width="175" height="75" rx="12" fill="#182231" stroke="#4ade80" stroke-width="2"/><text x="557.5" y="101" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Site A</text><text x="557.5" y="134" text-anchor="middle" font-size="11" fill="#a8b6c8">API + données</text></g>
<g><rect x="470" y="255" width="175" height="75" rx="12" fill="#182231" stroke="#fbbf24" stroke-width="2"/><text x="557.5" y="281" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Site B</text><text x="557.5" y="314" text-anchor="middle" font-size="11" fill="#a8b6c8">API + données</text></g>
<g><rect x="750" y="170" width="180" height="70" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="840.0" y="196" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">Supervision</text><text x="840.0" y="224" text-anchor="middle" font-size="11" fill="#a8b6c8">sondes applicatives</text></g>
<path d="M155 190 L220 190" fill="none" stroke="#43c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#43c7f5" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2s" begin="0s" repeatCount="indefinite" path="M155 190 L220 190"/></circle>
<path d="M380 188 L420 188 L420 113 L470 113" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.4s" begin=".3s" repeatCount="indefinite" path="M380 188 L420 188 L420 113 L470 113"/></circle>
<path d="M380 220 L420 220 L420 293 L470 293" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#fbbf24" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.6s" begin="1s" repeatCount="indefinite" path="M380 220 L420 220 L420 293 L470 293"/></circle>
<path d="M645 113 L700 113 L700 185 L750 185" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.3s" begin=".6s" repeatCount="indefinite" path="M645 113 L700 113 L700 185 L750 185"/></circle>
<path d="M645 293 L700 293 L700 225 L750 225" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#fbbf24" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.7s" begin="1.3s" repeatCount="indefinite" path="M645 293 L700 293 L700 225 L750 225"/></circle>
<text x="480" y="360" text-anchor="middle" font-size="12" font-weight="400" fill="#edf3fa">Une sonde TCP peut réussir alors que le parcours métier échoue : tester une transaction pertinente.</text>
<text x="480.0" y="406" text-anchor="middle" font-size="11" fill="#a8b6c8">La bascule multi-site doit prendre en compte données, état applicatif, TTL DNS et route retour.</text>
</svg>
</div>

Avant de déclarer un site « hors service », la sonde doit différencier panne applicative, panne d’accès de la sonde, panne DNS, défaillance d’une dépendance ou incident réseau local. Une mauvaise sonde peut retirer tous les sites d’un pool ou diriger les clients vers un site qui n’a pas les données les plus récentes.

### 7.4 Disponibilité des données : réplication n’est pas sauvegarde

La réplication aide à disposer d’une copie à jour sur un autre nœud ou site, selon le mécanisme et le délai. Elle peut aussi propager une suppression accidentelle, une corruption ou une opération malveillante. Une sauvegarde versionnée et testée répond à un autre besoin : restaurer une version saine.

Pour chaque service avec données, définis :

- RPO et méthode de mesure du retard ;
- cohérence requise après bascule ;
- propriétaire de l’écriture ;
- traitement des conflits ;
- conditions de promotion du secours ;
- procédure de resynchronisation après retour ;
- sauvegarde, restauration et vérification périodique.

Ne permets pas aux deux sites d’accepter des écritures concurrentes simplement parce que le lien inter-site est coupé. La politique doit protéger l’intégrité, même si cela implique une indisponibilité temporaire contrôlée.


## 8. SLI, SLO et budget d’erreur

### 8.1 Mesurer le service avec une définition reproductible

Un **SLI** est un indicateur mesuré, par exemple le pourcentage de transactions réussies. Un **SLO** définit la cible attendue sur une période. Un **SLA** est un engagement de service formel ou contractuel, selon l’organisation. Ne mélange pas leurs définitions.

Exemples de SLI :

- taux de requêtes réussies ;
- latence médiane, p95 ou p99 ;
- durée de bascule ;
- durée des pertes de paquets ;
- taux de sessions conservées ;
- retard de réplication ;
- disponibilité d’une transaction complète depuis un point utilisateur.

Une cible de « 99,99 % » n’a de sens que si le calcul précise la période, les événements exclus, les sondes, le mode de comptage et la dépendance observée. La mesure depuis la console de l’équipement ne remplace pas celle depuis les utilisateurs.

### 8.2 Budget d’erreur

Le budget d’erreur correspond à la part de défaillance tolérée par la cible de service pendant une période. Il aide à arbitrer entre changement, risque et stabilité. Ce n’est pas un permis pour ignorer les incidents : les données doivent alimenter les améliorations de l’architecture et des opérations.

Une disponibilité calculée sur le mois peut masquer une panne unique très longue ou de nombreux micro-incidents. Il faut compléter le pourcentage par la durée maximale, la répétition, l’impact par site et l’expérience utilisateur.

### 8.3 Observabilité de bout en bout

Pour chaque bascule, corrèle :

- télémétrie et état des interfaces ;
- logs de passerelle, routage et cluster ;
- changement RIB/FIB ;
- compteurs de perte, latence et retransmission ;
- métriques de santé applicative ;
- journaux DNS et de pool ;
- trace/capture horodatée ;
- commentaire d’opérateur et changement exécuté.

Les horloges doivent être synchronisées. Si deux équipements sont décalés de 20 secondes, une chronologie reconstruite peut attribuer la cause au mauvais événement. Les données de contrôle doivent être conservées avant qu’une panne ne les efface.


## 9. Réduire les boucles de décision et les bascules répétées

### 9.1 Le danger du ping-pong

Si plusieurs mécanismes déclenchent des changements interdépendants, une panne peut provoquer une série de changements secondaires. Exemple : une sonde retire la route principale, la route de secours change le chemin de la sonde, la sonde échoue à son tour et déclenche une seconde action. Un autre cas : un nœud est retiré du pool par une sonde locale, la charge de ses voisins augmente, ils dépassent leur seuil et sont également retirés.

### 9.2 Principes de contrôle

- une cause de défaillance doit avoir un signal principal clairement attribué ;
- les seuils doivent être compatibles entre contrôleurs ;
- prévoir des délais de stabilisation et un mécanisme d’hystérésis ;
- limiter le nombre de bascules avant une alerte ou un état de protection ;
- vérifier que la sonde reste indépendante du mécanisme qu’elle contrôle ;
- mesurer le comportement de retour et pas uniquement la première bascule ;
- inclure les surcharges et la perte partielle dans les tests.

### 9.3 Faits, hypothèses et preuves

Dans un incident, sépare trois colonnes :

| Catégorie | Exemple |
|---|---|
| Fait mesuré | L’adjacence BGP est tombée à 10:04:12.120 UTC. |
| Hypothèse | La perte d’adjacence a retiré le préfixe utilisé par le retour applicatif. |
| Preuve discriminante | La route FIB a disparu sur le nœud A, et la capture montre que le SYN-ACK n’atteint plus le client. |

Une explication n’est validée que si les observations la soutiennent et si une hypothèse concurrente a été éliminée raisonnablement. Évite d’attribuer la cause à « STP » ou « le firewall » seulement parce que la panne s’est produite au même moment.


## 10. Automatisation de l’audit HA

L’automatisation utile ne remplace pas le jugement de l’ingénieur : elle améliore la répétabilité. Un audit peut comparer les configurations à une intention déclarée, repérer les écarts de versions, extraire l’état de cluster et générer une matrice des tests non effectués.

### 10.1 Données minimales d’inventaire

Pour chaque composant : identifiant, site/rack, rôle, propriétaire, version, dépendances, protocole HA, interfaces de contrôle et de données, état de redondance, dernier test, dernier incident, plan de retour arrière, alarmes et lien vers la documentation du fournisseur.

### 10.2 Exemple de checklist automatisable

```yaml
service: portail-interne
criticality: high
user_probe:
  type: https_transaction
  endpoint: /health/transaction
  interval_seconds: 5
  timeout_seconds: 2
availability_path:
  - access_pair
  - gateway_group
  - firewall_cluster
  - load_balancer_pool
  - app_cluster
  - database_service
failover_tests:
  - lose_access_member
  - lose_uplink
  - fail_active_gateway
  - isolate_cluster_heartbeat
  - remove_one_app_instance
success_criteria:
  max_recovery_seconds: 5
  max_failed_transactions: 2
  require_data_consistency_check: true
```

Cet exemple est une structure de conception, pas un format universel reconnu par les équipements. Les champs doivent être reliés aux outils de supervision et aux opérations réelles. Ne déclenche pas automatiquement des pannes en production à partir d’un fichier sans contrôle d’accès, approbation et garde-fous.

### 10.3 Vérification de configuration

Un outil d’audit peut rechercher des incohérences telles que :

- les deux membres d’un EtherChannel n’ont pas la même configuration ;
- la passerelle virtuelle n’est pas identique sur les pairs prévus ;
- les priorités ou le tracking ne correspondent pas au design ;
- les politiques de sécurité diffèrent entre actifs et secours ;
- le pool applicatif a un seul membre sain ;
- le canal de synchronisation n’est pas supervisé ;
- aucun test de bascule n’est consigné depuis la dernière mise à jour ;
- la sauvegarde ou le retour arrière n’a jamais été vérifié.

Les alertes d’audit doivent donner une preuve et une recommandation, pas seulement un score rouge. Un écart intentionnel et documenté ne doit pas être traité comme une panne sans examen.


## 11. Campagne de tests : ne pas se limiter à couper un câble

<div class="lesson-figure ha-expert-figure">
<svg width="960" height="400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 400" role="img" aria-label="8. Test de bascule : méthode reproductible" style="width:100%;max-width:100%;display:block;font-family:Arial,Helvetica,sans-serif">
<rect width="960" height="400" rx="16" fill="#10151f"/>
<text x="24" y="29" font-size="20" font-weight="700" fill="#edf3fa">8. Test de bascule : méthode reproductible</text>
<text x="25" y="51" font-size="12" fill="#a8b6c8">Un résultat HA doit être mesuré avec l’état initial, un défaut défini et une validation utilisateur.</text>
<path d="M24 65 H936" stroke="#344357" stroke-width="1.5"/>
<g><rect x="30" y="130" width="165" height="78" rx="12" fill="#182231" stroke="#43c7f5" stroke-width="2"/><text x="112.5" y="156" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">1. Baseline</text><text x="112.5" y="192" text-anchor="middle" font-size="11" fill="#a8b6c8">config + santé</text></g>
<g><rect x="265" y="130" width="165" height="78" rx="12" fill="#182231" stroke="#fbbf24" stroke-width="2"/><text x="347.5" y="156" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">2. Panne contrôlée</text><text x="347.5" y="192" text-anchor="middle" font-size="11" fill="#a8b6c8">une cause à la fois</text></g>
<g><rect x="500" y="130" width="165" height="78" rx="12" fill="#182231" stroke="#4ade80" stroke-width="2"/><text x="582.5" y="156" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">3. Mesure</text><text x="582.5" y="192" text-anchor="middle" font-size="11" fill="#a8b6c8">paquets + app</text></g>
<g><rect x="735" y="130" width="195" height="78" rx="12" fill="#182231" stroke="#c4b5fd" stroke-width="2"/><text x="832.5" y="156" text-anchor="middle" font-size="14" font-weight="700" fill="#edf3fa">4. Retour arrière</text><text x="832.5" y="192" text-anchor="middle" font-size="11" fill="#a8b6c8">preuve + stabilité</text></g>
<path d="M195 169 L265 169" fill="none" stroke="#43c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#43c7f5" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.0s" begin="0s" repeatCount="indefinite" path="M195 169 L265 169"/></circle>
<path d="M430 169 L500 169" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#fbbf24" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.0s" begin=".5s" repeatCount="indefinite" path="M430 169 L500 169"/></circle>
<path d="M665 169 L735 169" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#4ade80" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="2.0s" begin="1s" repeatCount="indefinite" path="M665 169 L735 169"/></circle>
<path d="M835 208 L835 275 L110 275 L110 208" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="4.5" fill="#c4b5fd" stroke="#f8fafc" stroke-width="1.3"><animateMotion dur="5.5s" begin="1.5s" repeatCount="indefinite" path="M835 208 L835 275 L110 275 L110 208"/></circle>
<text x="470" y="322" text-anchor="middle" font-size="12" font-weight="400" fill="#edf3fa">Consigner : détection, décision, convergence, perte, impact session, reprise applicative, observations.</text>
<text x="470" y="343" text-anchor="middle" font-size="11" font-weight="400" fill="#fbbf24">Arrêter le test si la maquette devient instable ou si le périmètre déborde.</text>
<text x="480.0" y="386" text-anchor="middle" font-size="11" fill="#a8b6c8">Aucun test isolé ne couvre toutes les pannes possibles ; construire une matrice de scénarios.</text>
</svg>
</div>

### 11.1 Matrice de scénarios

| Scénario | Déclenchement en laboratoire | Résultat attendu à mesurer |
|---|---|---|
| Perte d’un membre LACP | désactiver un port membre | bundle actif, capacité restante suffisante |
| Perte de l’uplink principal | couper le lien amont d’un nœud | tracking/convergence et route réellement utilisable |
| Voisin de routage perdu sans perte physique | arrêter le protocole ou isoler le contrôle selon la maquette | délai de détection, retrait de route, chemin secours |
| Nœud de passerelle actif indisponible | arrêter le nœud actif | nouveau rôle, cache voisin, reprise d’application |
| Perte du canal de synchronisation | isoler uniquement le lien de sync | comportement sûr prévu par le produit, aucune double propriété |
| Un nœud applicatif devient lent | injecter une latence contrôlée | health check retire le nœud sans faire tomber le pool entier |
| DNS renvoie une cible obsolète | utiliser zone de laboratoire | effet du TTL et du cache clairement identifié |
| Perte d’un site | simuler l’indisponibilité du site de laboratoire | bascule, état des données, validation du service |
| Retour du nœud favori | rétablir un actif prioritaire | pas de deuxième interruption incontrôlée |
| Panne partielle ICMP/sonde | filtrage de test ciblé | sonde n’est pas confondue avec l’application |

### 11.2 Ordre de test sûr

1. Démarrer dans une topologie isolée ; capturer les versions, configurations et états.
2. Vérifier que les sondes réseau et applicatives réussissent avant l’injection.
3. Déclencher un seul défaut bien défini.
4. noter l’heure exacte et recueillir les journaux sur tous les pairs.
5. mesurer le changement de rôle, de route et la reprise des transactions.
6. restaurer l’élément défaillant et observer le comportement de retour.
7. vérifier l’absence d’état incohérent et de pression de capacité.
8. refaire le test plusieurs fois si la variabilité des timers ou du trafic peut changer le résultat.
9. documenter les faits, la limite et la décision d’acceptation.

### 11.3 Critères d’arrêt

Arrête un test si le périmètre impacté dépasse la maquette, si deux membres prennent une propriété incompatible, si les routes sortent du chemin de test, si le système perd ses données de contrôle ou si une surcharge menace de faire tomber des composants non concernés. Le plan d’arrêt doit exister avant le test, et non être inventé une fois l’incident en cours.


## 12. Runbook expert de changement HA

### Phase A — Préparation

- [ ] Définir le service utilisateur et le SLO visé.
- [ ] Identifier toutes les dépendances et les modes de panne communs.
- [ ] Relever version, configuration, routes, rôles, sessions et capacité.
- [ ] Vérifier les sauvegardes et le plan de retour arrière.
- [ ] Vérifier la synchronisation d’horloge et l’accès aux journaux.
- [ ] Valider les sondes réseau et applicatives.
- [ ] Définir les critères de réussite et d’arrêt.
- [ ] Obtenir la fenêtre et les approbations requises.

### Phase B — Exécution

- [ ] Modifier une seule variable majeure à la fois.
- [ ] Surveiller le plan de contrôle et le plan de données en parallèle.
- [ ] Tester un client depuis le vrai segment utilisateur.
- [ ] Mesurer la durée et la perte de paquets.
- [ ] Vérifier les sessions existantes, DNS, routes retour et données.
- [ ] Si un seuil d’arrêt est dépassé, rétablir le dernier état connu.

### Phase C — Stabilisation

- [ ] Rejouer les tests de service après la convergence.
- [ ] Vérifier les alarmes et l’état dégradé du secours.
- [ ] Vérifier la capacité du mode N-1.
- [ ] Valider le retour du nœud et du site sans bascule en boucle.
- [ ] Mettre à jour l’inventaire, les diagrammes et les procédures.
- [ ] Documenter les observations réelles et les risques résiduels.

### Modèle de compte rendu

```text
Identifiant du changement :
Service / propriétaire :
Topologie et versions :
État initial mesuré :
Hypothèse testée :
Défaut injecté :
Heure de début / fin :
Détection observée :
Décision et convergence :
Perte de paquets / sessions :
Résultat applicatif :
État après restauration :
Preuves collectées :
Écarts / risques résiduels :
Décision : accepté / rollback / investigation
```

Un bon rapport indique aussi ce qui **n’a pas été testé**. Ne présente pas la validation de deux scénarios comme une preuve universelle de haute disponibilité.


## 13. Laboratoires avancés

### Laboratoire 1 — Architecture et FMEA

**Objectif :** identifier les causes communes dans un schéma de service.

1. Choisir un service de laboratoire (portail, DNS interne ou API).
2. Dessiner son parcours complet depuis le client jusqu’aux données.
3. Pour chaque dépendance, lister au moins deux modes de panne plausibles.
4. Marquer les composants redondés et les dépendances encore uniques.
5. Définir une sonde et un mécanisme de secours par panne critique.
6. classer les risques en fonction de l’impact, de la probabilité estimée et de la détectabilité.

**Livrable :** diagramme, matrice de pannes, mesures et plan d’action. La réussite se mesure à la capacité d’expliquer un point unique de défaillance et de proposer une preuve pour le corriger.

### Laboratoire 2 — Suivi d’une passerelle au-delà de l’interface

**Objectif :** démontrer qu’un port actif ne représente pas toujours la santé de la route.

1. Configurer une passerelle redondante dans une maquette.
2. établir un test continu vers un hôte distant de laboratoire.
3. mesurer le comportement lorsque le lien direct d’un nœud est coupé.
4. répéter en gardant le lien local actif mais en interrompant le chemin amont de laboratoire.
5. comparer la détection d’interface à une sonde de route ou IP SLA supportée.
6. observer un retour avec préemption et déterminer si la reprise est stable.

**Livrable :** sorties des commandes, chronologie, différence de perte et recommandation. Ne tire aucune conclusion à partir du seul état Active/Standby.

### Laboratoire 3 — BFD et retrait de route

**Objectif :** relier une détection de forwarding au changement de chemin.

1. Créer deux chemins de routage dans une maquette compatible.
2. Vérifier la route et la latence de référence.
3. Activer BFD selon la documentation de l’image logicielle utilisée, si supporté.
4. provoquer une panne contrôlée du chemin primaire.
5. capturer les changements de voisinage et de route ; mesurer l’application.
6. répéter avec des timers moins agressifs si le système autorise cette expérience.

**Livrable :** latences, délais de détection, changement de route, perte et explication des limites.

### Laboratoire 4 — Multi-homing et perte du lien de pair

**Objectif :** tester le comportement d’un modèle MLAG/vPC pris en charge.

1. Consulter la documentation du produit et dessiner les canaux de données et de contrôle.
2. vérifier LACP, VLAN, MTU et état du pair.
3. lancer un trafic de laboratoire avec mesure continue.
4. simuler dans les conditions autorisées la perte d’un membre, puis du canal de pair.
5. relever le rôle des nœuds, les tables MAC, les routes, logs et alertes.
6. restaurer et vérifier qu’un seul état cohérent subsiste.

**Sécurité :** ne reproduis pas une perte de peer-link sur une infrastructure de production sans procédure écrite et compréhension exacte du comportement du fournisseur.

### Laboratoire 5 — Préserver les sessions au travers d’un pare-feu

**Objectif :** différencier la reprise des nouvelles connexions et celle des sessions établies.

1. Créer des connexions longue durée et des requêtes périodiques.
2. vérifier l’état de synchronisation des sessions.
3. collecter les compteurs avant bascule.
4. effectuer la bascule de laboratoire selon la documentation du cluster.
5. déterminer quelles connexions restent valides, se réinitialisent ou time-out.
6. examiner la réplication, l’asymétrie et les traductions NAT possibles.

**Livrable :** tableau par type de flux, délai, résultat et niveau de continuité effectivement obtenu.

### Laboratoire 6 — Failover multi-site et DNS

**Objectif :** démontrer que le retrait du site n’est pas instantané chez chaque client.

1. Déployer deux services de test dans une maquette ou un simulateur adapté.
2. définir une sonde qui vérifie une transaction métier.
3. enregistrer la réponse DNS et son TTL depuis plusieurs clients.
4. rendre le site primaire indisponible à l’intérieur du laboratoire.
5. relever l’état du GSLB/DNS, les caches et les connexions existantes.
6. vérifier données, routes, authentification, puis le site de secours.

**Livrable :** chronologie par couche et recommandations pour limiter les effets d’un cache obsolète.

### Laboratoire 7 — Split-brain et fencing : étude de conception

Si un produit réel ne permet pas de simuler ce scénario sans risque, conduis l’exercice comme une étude de panne plutôt qu’en injectant réellement une défaillance. Cartographie le heartbeat, le quorum, le propriétaire et le fencing. Réponds à cette question : après une partition réseau, quelle preuve empêche l’ancien nœud de continuer à écrire ? Si la réponse n’est pas précise, la conception n’est pas validée.

### Laboratoire 8 — Campagne de tests et rapport final

Construis une matrice couvrant perte d’un membre LACP, perte d’uplink, perte d’adjacence, nœud de passerelle, synchronisation de pare-feu, instance applicative lente et panne de site. Pour chaque scénario, relève la détection, la bascule, la convergence, les pertes, l’effet applicatif et le retour normal. Termine par une synthèse des risques résiduels et une décision d’acceptation.


## 14. Exercices corrigés

### Questions

1. Pourquoi la présence de deux routeurs ne suffit-elle pas à démontrer une HA multi-couches ?
2. Quelle différence y a-t-il entre un lien `up` et une transaction applicative réussie ?
3. Pourquoi une sonde qui contrôle une route peut-elle provoquer un ping-pong ?
4. Que faut-il examiner avant de réduire fortement les timers BFD ?
5. Pourquoi ECMP peut-il interrompre certaines sessions après retrait d’un next-hop ?
6. En quoi MLAG et un EtherChannel classique à un seul châssis sont-ils différents du point de vue de l’architecture ?
7. Pourquoi le quorum seul ne suffit-il pas toujours à prévenir une double écriture ?
8. Qu’est-ce que le fencing doit empêcher concrètement ?
9. Pourquoi un cluster de pare-feu peut-il accepter de nouvelles connexions mais perdre des sessions existantes ?
10. Comment différencier une panne DNS d’une panne IP lorsque l’utilisateur accède par nom ?
11. Pourquoi la réplication ne remplace-t-elle pas les sauvegardes ?
12. Qu’est-ce qu’un SLI, un SLO et un SLA ?
13. Quelle information doit-on collecter pour reconstruire une chronologie de bascule ?
14. Pourquoi un test depuis la console du routeur ne suffit-il pas ?
15. Quelle est la différence entre perte d’un membre LACP et perte d’un port-channel entier ?
16. Donne deux exemples de défaillance corrélée dans une architecture supposée redondante.
17. Pourquoi le retour du nœud préféré peut-il être risqué ?
18. Comment doit être conçue une sonde applicative utile ?
19. Quels éléments distinguent une asymétrie de routage acceptable d’une asymétrie qui casse un service stateful ?
20. Quelles preuves faut-il réunir avant de déclarer une campagne HA réussie ?

### Corrigés commentés

**1.** Les deux routeurs peuvent partager un commutateur, une alimentation, un opérateur, une route ou une dépendance DNS unique. Il faut vérifier les domaines de panne et tester le parcours complet.

**2.** `up` décrit principalement l’état du lien ou de l’interface. Une transaction réussie prouve qu’un parcours défini a pu effectuer une fonction utile, sans pour autant prouver que tous les scénarios sont disponibles.

**3.** La modification de route peut modifier le chemin de la sonde et la rendre inaccessible. La sonde déclenche alors une seconde modification. Il faut vérifier l’indépendance de la cible et concevoir des seuils stables.

**4.** Capacité CPU, support de la plate-forme, comportement du transport, timer minimum réellement négocié, risque de faux positifs, impact de la charge et budget de convergence mesuré.

**5.** Le retrait change la sélection du chemin et le hachage. Les états intermédiaires peuvent être absents, les chemins de retour différents ou les équipements stateful peuvent ne pas voir les deux directions.

**6.** L’agrégat classique regroupe plusieurs liens vers un même système logique de terminaison ; un multi-châssis ajoute une coordination de plusieurs châssis et des scénarios de partition/peer-link qui doivent être explicitement gérés.

**7.** Un quorum décide quel groupe peut agir, mais l’ancien propriétaire peut encore avoir accès à la ressource. Le fencing doit empêcher cette propriété concurrente réelle.

**8.** Retirer l’accès du nœud qui ne doit plus être propriétaire : par exemple l’autorité d’écrire, l’accès au volume ou la capacité d’annoncer/utiliser une ressource exclusive, selon le système.

**9.** Le mécanisme peut répliquer certains états mais pas tous, ou le retard peut rendre la table de secours incomplète. Les nouveaux flux sont créés sur le nœud actif après bascule ; les anciens dépendent de l’état conservé.

**10.** Vérifier la réponse A/AAAA, tester les destinations résolues directement, puis comparer route, filtrage et service. Une résolution réussie ne garantit pas la route, et un accès IP réussi ne garantit pas un DNS correct.

**11.** Une suppression ou corruption peut être propagée au réplique. Les sauvegardes versionnées permettent de retrouver un état antérieur sain, si la restauration a été testée.

**12.** SLI : mesure concrète. SLO : cible définie pour une période. SLA : engagement formel de niveau de service, souvent contractuel. Les termes ne sont pas interchangeables.

**13.** Horodatages synchronisés, état de lien, logs de protocole, changement RIB/FIB, mesures de perte, état de cluster, sonde et résultat de transaction applicative.

**14.** La console peut se situer dans un plan d’administration différent du chemin utilisateur. Le test doit partir d’un point représentatif et couvrir le service attendu.

**15.** La perte d’un membre laisse le bundle actif si les membres restants suffisent ; la perte entière du port-channel supprime le chemin logique, sauf si une autre route alternative est utilisable.

**16.** Deux liens dans le même conduit ; deux nœuds dans le même rack/alimentation ; deux sites dépendant du même DNS/IdP ; deux nœuds mis à jour par le même changement erroné.

**17.** La reprise de rôle peut produire une deuxième bascule, couper des sessions ou déplacer le trafic vers un équipement encore instable. La préemption doit être mesurée et gouvernée.

**18.** Elle teste une opération représentative, utilise des seuils et délais cohérents, couvre les dépendances sans amplifier la charge, et est corrélée à une validation utilisateur.

**19.** Si tous les équipements et la politique permettent le retour asymétrique, le service peut rester valide. Si un pare-feu stateful, un NAT ou un contrôle exige un état symétrique, les paquets retour peuvent être rejetés ou associés à aucune session.

**20.** Résultats horodatés, critères de réussite, journaux, métriques, pertes, tests de sessions et transactions, preuve du retour, tests de scénarios distincts et documentation des limites non couvertes.


## 15. Glossaire expert

| Terme | Définition opérationnelle |
|---|---|
| BFD | Protocole de détection de certaines pannes de chemin de forwarding ; il ne remplace pas le routage. |
| ECMP | Utilisation de plusieurs next-hops de coût égal selon les règles de la plate-forme. |
| Fencing | Mécanisme empêchant un ancien propriétaire d’accéder à une ressource exclusive après changement d’autorité. |
| FMEA | Analyse structurée des modes de panne, effets, détection et traitements. |
| GSLB | Répartition/choix global de site, souvent à partir de DNS et de contrôles de santé. |
| HA | Haute disponibilité : architecture et opérations qui réduisent les interruptions de service définies. |
| Hysteresis | Seuils ou temporisations visant à empêcher les oscillations autour d’une condition de bascule. |
| LACP | Protocole de négociation d’agrégation de liens ; la redondance multi-châssis relève d’un modèle supplémentaire. |
| MLAG | Famille d’approches d’agrégation vers plusieurs châssis ; comportement spécifique au produit. |
| N-1 | Capacité ou comportement attendu après perte de l’élément défini dans le scénario N-1. |
| RIB/FIB | Table de routage du plan de contrôle / structure de transfert du plan de données. |
| RPO | Perte de données maximale admissible selon la définition du service. |
| RTO | Objectif de délai pour rétablir le service après une interruption. |
| SLI | Indicateur mesuré de niveau de service. |
| SLO | Objectif mesurable sur une période définie. |
| Split-brain | Deux membres prennent des décisions incompatibles en se croyant autorisés à agir. |


## 16. Références techniques

Les références normatives décrivent des protocoles, mais pas tous les détails d’une implémentation constructeur. Confirme toujours la version logicielle, les fonctions prises en charge et la procédure de retour arrière.

- **IETF RFC 9568 — VRRP Version 3 for IPv4 and IPv6** (2024) : protocole standard de redondance de passerelle, remplace RFC 5798. https://www.rfc-editor.org/rfc/rfc9568.html
- **IETF RFC 5880 — Bidirectional Forwarding Detection (BFD)** : détection de défaillances du chemin de forwarding. https://www.rfc-editor.org/rfc/rfc5880.html
- **IEEE 802.1AX — Link Aggregation** : cadre normalisé pour l’agrégation de liens. https://standards.ieee.org/ieee/802.1AX/6768/
- **IETF RFC 7432 — BGP MPLS-Based Ethernet VPN** : contexte EVPN, dont les services Ethernet multi-homing selon la conception. https://www.rfc-editor.org/rfc/rfc7432.html
- **IETF RFC 9099 — Operational Security Considerations for IPv6 Networks** : considérations opérationnelles de sécurité IPv6. https://www.rfc-editor.org/rfc/rfc9099.html
- **Cisco IOS XE — High Availability Configuration Guides** : consulter la section correspondant exactement à HSRP, IP SLA/object tracking, EtherChannel, StackWise Virtual/vPC ou au modèle utilisé. https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe-17/series.html
- Documentation officielle du fournisseur de pare-feu/cluster : modes de failover, état répliqué, split-brain, quorum et procédure de récupération.
- Documentation d’exploitation des outils de supervision, de capture et des plateformes applicatives utilisées dans les laboratoires.


## Conclusion — Le niveau Expert

Un design HA n’est pas validé parce qu’il contient deux équipements, deux liens ou un protocole de bascule. Il est validé lorsque les dépendances ont été inventoriées, les domaines de panne communs compris, les mécanismes de détection et de décision cohérents, l’état nécessaire protégé, la capacité après panne suffisante et la reprise démontrée par des mesures depuis le point utilisateur.

L’expertise consiste à définir précisément ce que l’on protège, à choisir une architecture adaptée, à maîtriser les risques de concurrence et de convergence, à construire une campagne de tests reproductible et à rapporter les preuves comme les limites. Une conception qui sait expliquer ses modes de panne est plus fiable qu’une architecture qui n’a été testée que dans son scénario nominal.
