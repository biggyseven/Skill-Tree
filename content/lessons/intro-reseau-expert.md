
# Qu'est-ce qu'un réseau informatique ? — Niveau expert

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Prérequis :** maîtriser les modèles en couches, les sous-réseaux, les VLAN, les tables de routage et les principaux protocoles réseau.  
> **Objectif :** concevoir, analyser et dépanner des architectures réseau complexes en tenant compte de la disponibilité, de la sécurité, des performances et de l'exploitation.

---

## Sommaire

1. Vision systémique du réseau
2. Architecture et plans de fonctionnement
3. Conception du plan d'adressage
4. Routage dynamique et politiques de chemin
5. Commutation, boucles et redondance
6. IPv6 et coexistence IPv4/IPv6
7. Segmentation et architecture de sécurité
8. Haute disponibilité et convergence
9. Performances, QoS et MTU
10. Observabilité et télémétrie
11. Méthode d'analyse des incidents complexes
12. Architecture de référence
13. Étude de panne
14. Atelier expert
15. Évaluation corrigée

---

# 1. Vision systémique du réseau

## 1.1 Un réseau est un système interdépendant

Un réseau d'entreprise ne se réduit pas à un ensemble de câbles et d'adresses IP. Il associe des équipements physiques ou virtuels, des protocoles, des politiques et des services.

Une architecture peut inclure :

- des réseaux d'accès ;
- des commutateurs de distribution et de cœur ;
- des routeurs de bordure ;
- des pare-feu ;
- des liaisons opérateur ;
- des réseaux de centres de données ;
- des services DNS et DHCP ;
- des systèmes d'identité ;
- des mécanismes de supervision ;
- des outils d'automatisation et de gestion.

Une panne locale peut avoir des conséquences bien au-delà du composant qui l'a provoquée. Une route manquante peut isoler un site ; une mauvaise règle de filtrage peut empêcher l'accès à un service partagé ; une erreur DNS peut affecter un grand nombre d'applications.

La qualité d'une architecture dépend donc de la façon dont les composants s'articulent et des mécanismes qui détectent et maîtrisent leurs défaillances.

## 1.2 Objectifs experts

À la fin de ce cours, vous serez capable de :

1. décrire les fonctions principales d'une architecture réseau ;
2. distinguer les plans de contrôle et de transfert ;
3. concevoir un plan d'adressage cohérent ;
4. expliquer les rôles du routage interne et du routage interdomaines ;
5. comprendre les boucles de couche 2 et les mécanismes de redondance ;
6. concevoir une coexistence IPv4/IPv6 ;
7. structurer une segmentation de sécurité ;
8. analyser la disponibilité et la convergence ;
9. comprendre les compromis de performance et de qualité de service ;
10. organiser la supervision et la collecte de preuves ;
11. conduire un diagnostic d'incident complexe ;
12. transformer les enseignements d'un incident en améliorations techniques.

---

# 2. Architecture et plans de fonctionnement

## 2.1 Plan de données

Le plan de données, ou plan de transfert, est responsable du traitement et du transfert du trafic utilisateur selon les informations déjà installées dans les équipements.

Dans un routeur, cela comprend notamment les décisions de transfert appliquées à partir des routes et des structures dérivées utilisées par l'implémentation.

Dans un switch, cela comprend le transfert des trames selon les informations de commutation et la configuration des VLAN.

## 2.2 Plan de contrôle

Le plan de contrôle construit ou maintient les informations qui permettent au plan de données de fonctionner.

Il comprend, par exemple :

- les calculs et échanges des protocoles de routage ;
- les mécanismes de découverte des voisins ;
- les échanges qui construisent certaines tables de contrôle ;
- les mécanismes de convergence après une modification de topologie.

Une panne du plan de contrôle peut empêcher la mise à jour correcte des chemins alors que certains flux déjà établis continuent temporairement de fonctionner.

Cette distinction dépend de l'architecture des équipements : les détails d'implémentation varient selon les plateformes.

## 2.3 Plan de gestion

Le plan de gestion donne accès aux fonctions d'administration, de configuration, de supervision et de maintenance.

Il peut utiliser SSH, HTTPS, SNMP, NETCONF, RESTCONF, des API propriétaires ou d'autres mécanismes.

Une défaillance du plan de gestion peut empêcher l'administration à distance sans nécessairement interrompre immédiatement le transfert de trafic. Inversement, le réseau peut être joignable tout en étant mal configuré.

Les interfaces de gestion doivent donc être protégées et surveillées séparément des flux applicatifs.

## 2.4 Schéma des trois plans

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="375" viewBox="0 0 960 375" role="img" aria-labelledby="planes-title planes-desc">
  <title id="planes-title">Plans de données, de contrôle et de gestion</title>
  <desc id="planes-desc">Le plan de contrôle construit les informations de routage et de transfert. Le plan de données transfère les paquets. Le plan de gestion permet de configurer et superviser les équipements. Les flèches animées représentent les relations logiques, sans particule mobile.</desc>
  <defs>
    <marker id="planes-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .pn-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .pn-control{fill:#302044;stroke:#c4b5fd;stroke-width:2}
      .pn-data{fill:#123126;stroke:#4ade80;stroke-width:2}
      .pn-title{font:700 16px Arial,sans-serif;fill:#f8fafc}
      .pn-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .pn-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#planes-arrow);animation:pn-dash 1.8s linear infinite}
      @keyframes pn-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="373" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">TROIS RESPONSABILITÉS À DISTINGUER</text>
  <rect class="pn-control" x="35" y="70" width="260" height="95" rx="12"/>
  <text class="pn-title" x="165" y="101" text-anchor="middle">Plan de contrôle</text>
  <text class="pn-text" x="165" y="126" text-anchor="middle">Protocoles et calcul des chemins</text>
  <text class="pn-text" x="165" y="146" text-anchor="middle">RIB et informations de contrôle</text>
  <rect class="pn-data" x="350" y="70" width="260" height="95" rx="12"/>
  <text class="pn-title" x="480" y="101" text-anchor="middle">Plan de données</text>
  <text class="pn-text" x="480" y="126" text-anchor="middle">Transfert des trames et paquets</text>
  <text class="pn-text" x="480" y="146" text-anchor="middle">Tables et structures de transfert</text>
  <rect class="pn-box" x="665" y="70" width="260" height="95" rx="12"/>
  <text class="pn-title" x="795" y="101" text-anchor="middle">Plan de gestion</text>
  <text class="pn-text" x="795" y="126" text-anchor="middle">Configuration et supervision</text>
  <text class="pn-text" x="795" y="146" text-anchor="middle">Accès administratifs contrôlés</text>
  <path class="pn-flow" d="M295 116 H342"/>
  <rect class="pn-box" x="185" y="230" width="590" height="75" rx="12"/>
  <text class="pn-title" x="480" y="259" text-anchor="middle">Équipement réseau</text>
  <text class="pn-text" x="480" y="282" text-anchor="middle">Les trois plans interagissent sans se confondre.</text>
  <path class="pn-flow" d="M480 165 V222"/>
  <path class="pn-flow" d="M795 165 V195 H720 V222"/>
  <text class="pn-text" x="480" y="337" text-anchor="middle">Le diagnostic doit établir quel plan est affecté, plutôt que conclure à une panne totale du réseau.</text>
</svg>

## 2.5 RIB et FIB

Dans de nombreux routeurs, la RIB (*Routing Information Base*) représente les routes connues par le plan de contrôle.

La FIB (*Forwarding Information Base*) représente les informations utilisées pour le transfert des paquets.

Ces structures sont liées, mais elles ne sont pas identiques. Toutes les routes présentes dans la RIB ne sont pas nécessairement installées dans la FIB.

Lorsqu'un routeur connaît une route dans son processus de routage mais ne l'installe pas dans la structure de transfert, il faut examiner le processus de sélection, les dépendances et les contraintes propres à la plateforme.

---

# 3. Conception du plan d'adressage

## 3.1 Un plan d'adressage est une décision d'architecture

Un plan d'adressage ne doit pas être improvisé à mesure que les réseaux sont créés.

Il doit tenir compte :

- du nombre de sites ;
- des catégories de systèmes ;
- de la croissance prévue ;
- du routage inter-sites ;
- des interconnexions externes ;
- des besoins de segmentation ;
- des mécanismes de résumé de routes ;
- de la coexistence IPv4 et IPv6 ;
- des politiques de sécurité et de gouvernance.

Un bon plan cherche à limiter les chevauchements, à rendre les préfixes lisibles et à simplifier le diagnostic.

## 3.2 Agrégation et résumé de routes

Un résumé de routes regroupe plusieurs préfixes en un préfixe plus large lorsque l'ensemble d'adresses est compatible avec cette agrégation.

Par exemple, plusieurs blocs contigus correctement alignés peuvent être agrégés pour réduire le nombre de routes annoncées.

Le résumé doit être exact : agréger des préfixes sans tenir compte des trous peut annoncer une plage pour laquelle le routeur n'a aucun chemin valide.

Il faut également tenir compte de l'impact sur le trafic destiné aux préfixes absents de la topologie.

## 3.3 Exemple d'allocation hiérarchique

Une organisation peut réserver un bloc pour chaque site, puis des sous-blocs pour les fonctions locales.

Exemple purement pédagogique :

```text
10.0.0.0/8
├── 10.10.0.0/16   Site A
│   ├── 10.10.10.0/24   Utilisateurs
│   ├── 10.10.20.0/24   Serveurs
│   └── 10.10.30.0/24   Administration
└── 10.20.0.0/16   Site B
    ├── 10.20.10.0/24   Utilisateurs
    ├── 10.20.20.0/24   Serveurs
    └── 10.20.30.0/24   Administration
```

Les préfixes sont illustratifs. En production, il faut vérifier l'unicité du plan, la compatibilité avec les réseaux interconnectés et les contraintes d'exploitation.

## 3.4 Vérifier l'absence de chevauchement

Deux sous-réseaux ne doivent pas être assignés de façon contradictoire à des segments qui doivent fonctionner comme des préfixes distincts.

Un chevauchement peut provoquer une sélection de chemin inattendue, une difficulté à déterminer si une destination est locale ou distante et des problèmes lors de l'interconnexion de sites.

Une base de données d'adressage ou un outil de gestion IP (IPAM) permet de réserver les allocations, de documenter les propriétaires et d'éviter les doublons.

---

# 4. Routage dynamique et politiques de chemin

## 4.1 Le routage est plus qu'une liste de destinations

Les protocoles de routage découvrent ou échangent des informations selon des mécanismes différents.

Le choix d'un protocole dépend notamment :

- de la taille du réseau ;
- de la topologie ;
- du nombre de domaines administratifs ;
- des besoins de convergence ;
- des politiques de sécurité ;
- de la facilité d'exploitation ;
- des compétences et outils disponibles.

Le but n'est pas d'activer tous les protocoles possibles, mais de choisir les mécanismes qui satisfont les exigences de l'architecture.

## 4.2 OSPF

OSPF est un protocole de routage à état de liens utilisé notamment dans les réseaux d'entreprise.

Les routeurs échangent des informations de topologie au moyen de mécanismes définis par le protocole. Ils construisent une représentation de cette topologie et calculent des routes.

La conception doit tenir compte des zones, des relations entre routeurs, du résumé lorsqu'il est approprié et des paramètres de coût.

Un voisinage OSPF établi ne garantit pas que toutes les routes attendues sont installées ou que les services distants fonctionnent. Le diagnostic doit vérifier plusieurs étapes : adjacency, base de données de liens, calcul de routes, installation et transfert.

## 4.3 BGP

BGP est un protocole de routage interdomaines utilisé notamment entre systèmes autonomes et dans certaines architectures internes avancées.

La sélection d'un chemin BGP dépend de règles et d'attributs, ainsi que de la politique configurée.

Un chemin reçu n'est pas nécessairement annoncé à d'autres voisins ni choisi comme meilleur chemin. Les filtres d'entrée et de sortie, les préférences locales et les politiques d'annonce sont essentiels.

Une erreur de politique BGP peut affecter non seulement l'accessibilité, mais aussi le chemin emprunté et l'exposition des préfixes.

## 4.4 Route statique ou dynamique ?

| Critère | Routage statique | Routage dynamique |
|---|---|---|
| Configuration | Chemins définis explicitement | Routes apprises ou calculées par protocole |
| Adaptation aux pannes | Dépend de la configuration et des mécanismes associés | Peut reconverger selon le protocole |
| Complexité initiale | Faible dans un réseau simple | Plus élevée |
| Évolutivité | Peut devenir difficile à maintenir à grande échelle | Adapté à des topologies nécessitant des échanges dynamiques |
| Contrôle | Explicite, mais peut être rigide | Politique et protocoles à maîtriser |
| Diagnostic | Vérifier route et prochain saut | Vérifier voisinage, sélection, installation et transfert |

Les routes statiques peuvent être tout à fait appropriées dans un réseau conçu pour elles. Le routage dynamique n'est pas automatiquement supérieur dans toutes les situations.

## 4.5 Schéma du parcours d'une route

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-labelledby="expert-route-title expert-route-desc">
  <title id="expert-route-title">Du protocole de routage au transfert IP</title>
  <desc id="expert-route-desc">Les informations du protocole contribuent à la RIB. La sélection des routes détermine celles installées dans la FIB. Le plan de données utilise la FIB pour transférer les paquets. Un paquet peut échouer même si une information de routage existe au départ.</desc>
  <defs>
    <marker id="expert-route-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .er-control{fill:#302044;stroke:#c4b5fd;stroke-width:2}
      .er-data{fill:#123126;stroke:#4ade80;stroke-width:2}
      .er-title{font:700 16px Arial,sans-serif;fill:#f8fafc}
      .er-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .er-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#expert-route-arrow);animation:er-dash 1.8s linear infinite}
      @keyframes er-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="358" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">CONNAÎTRE UNE ROUTE NE SUFFIT PAS TOUJOURS À TRANSFÉRER</text>
  <rect class="er-control" x="25" y="90" width="190" height="90" rx="12"/>
  <text class="er-title" x="120" y="119" text-anchor="middle">Protocole de routage</text>
  <text class="er-text" x="120" y="143" text-anchor="middle">Échange de chemins</text>
  <text class="er-text" x="120" y="163" text-anchor="middle">Exemple : OSPF/BGP</text>
  <rect class="er-control" x="270" y="90" width="190" height="90" rx="12"/>
  <text class="er-title" x="365" y="119" text-anchor="middle">RIB</text>
  <text class="er-text" x="365" y="143" text-anchor="middle">Routes connues</text>
  <text class="er-text" x="365" y="163" text-anchor="middle">Sélection</text>
  <rect class="er-data" x="515" y="90" width="190" height="90" rx="12"/>
  <text class="er-title" x="610" y="119" text-anchor="middle">FIB</text>
  <text class="er-text" x="610" y="143" text-anchor="middle">Informations de transfert</text>
  <text class="er-text" x="610" y="163" text-anchor="middle">Routes installées</text>
  <rect class="er-data" x="760" y="90" width="175" height="90" rx="12"/>
  <text class="er-title" x="847" y="119" text-anchor="middle">Plan de données</text>
  <text class="er-text" x="847" y="143" text-anchor="middle">Transfert du paquet</text>
  <text class="er-text" x="847" y="163" text-anchor="middle">Prochain saut</text>
  <path class="er-flow" d="M215 135 H262"/>
  <path class="er-flow" d="M460 135 H507"/>
  <path class="er-flow" d="M705 135 H752"/>
  <text class="er-text" x="480" y="237" text-anchor="middle">Vérifier le protocole, la route sélectionnée, la FIB et le prochain saut.</text>
  <text class="er-text" x="480" y="263" text-anchor="middle">Puis confirmer le chemin retour et les politiques de filtrage.</text>
  <text class="er-text" x="480" y="301" text-anchor="middle">Un échec peut se situer à n'importe quelle étape du parcours.</text>
</svg>

---

# 5. Commutation, boucles et redondance

## 5.1 Les boucles Ethernet

Dans une topologie de couche 2, des liaisons redondantes peuvent créer une boucle de commutation.

Les boucles peuvent provoquer des tempêtes de broadcast, des changements rapides dans les tables MAC et une dégradation importante du réseau.

Des mécanismes comme Spanning Tree Protocol (STP) aident à construire une topologie logique sans boucle de transfert active dans le domaine concerné.

## 5.2 STP et topologie logique

STP et ses variantes utilisent des échanges de contrôle pour déterminer les chemins qui doivent transférer le trafic et ceux qui doivent être bloqués ou écartés pour empêcher les boucles.

Les détails dépendent de la variante, de la configuration et de la plateforme.

Une mauvaise configuration de STP, des changements inattendus de topologie ou une perte de connectivité entre équipements peuvent affecter le trafic de plusieurs VLAN.

La présence de liens redondants n'implique donc pas que tous les liens transfèrent simultanément tout le trafic.

## 5.3 Link aggregation

L'agrégation de liens permet de présenter plusieurs liens physiques comme un groupe logique, dans les conditions prévues par la technologie utilisée, par exemple LACP.

Elle peut augmenter la capacité disponible pour un ensemble de flux et fournir une certaine tolérance à la perte d'un lien.

Elle ne signifie pas nécessairement qu'un flux individuel utilisera la capacité additionnée de tous les liens. La distribution dépend notamment de l'algorithme de répartition et de la nature des flux.

Les deux extrémités doivent être configurées de façon compatible.

## 5.4 Schéma des chemins redondants

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-labelledby="redundancy-title redundancy-desc">
  <title id="redundancy-title">Redondance de commutation et contrôle des boucles</title>
  <desc id="redundancy-desc">Deux switches sont reliés par des chemins redondants. Le mécanisme de prévention des boucles doit déterminer quelles liaisons transfèrent le trafic dans le domaine concerné. La redondance nécessite une configuration cohérente.</desc>
  <defs>
    <marker id="red-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .rd-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .rd-control{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .rd-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .rd-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .rd-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#red-arrow);animation:rd-dash 1.8s linear infinite}
      .rd-alt{fill:none;stroke:#c4b5fd;stroke-width:3;stroke-dasharray:5 7}
      @keyframes rd-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="358" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">REDONDANCE PHYSIQUE ET TOPOLOGIE DE TRANSFERT</text>
  <rect class="rd-box" x="80" y="112" width="220" height="90" rx="12"/>
  <text class="rd-title" x="190" y="145" text-anchor="middle">Switch A</text>
  <text class="rd-text" x="190" y="170" text-anchor="middle">Accès utilisateurs</text>
  <rect class="rd-box" x="660" y="112" width="220" height="90" rx="12"/>
  <text class="rd-title" x="770" y="145" text-anchor="middle">Switch B</text>
  <text class="rd-text" x="770" y="170" text-anchor="middle">Distribution</text>
  <path class="rd-flow" d="M300 136 C410 65 550 65 660 136"/>
  <path class="rd-alt" d="M300 177 C410 255 550 255 660 177"/>
  <rect class="rd-control" x="350" y="278" width="260" height="48" rx="9"/>
  <text class="rd-title" x="480" y="298" text-anchor="middle">STP / variante configurée</text>
  <text class="rd-text" x="480" y="316" text-anchor="middle">Contrôle des boucles</text>
  <text class="rd-text" x="480" y="230" text-anchor="middle">Chemins redondants représentés</text>
  <text class="rd-text" x="480" y="249" text-anchor="middle">Un lien peut ne pas transférer dans un état donné</text>
</svg>

## 5.5 Redondance sans dépendance commune excessive

La redondance doit prendre en compte les défaillances de cause commune.

Deux liens ne constituent pas une vraie diversité si les deux passent par le même câble, la même gaine, le même équipement ou le même circuit opérateur susceptible de tomber en panne simultanément.

L'analyse doit distinguer la redondance logique et la diversité physique.

---

# 6. IPv6 et coexistence IPv4/IPv6

## 6.1 Pourquoi IPv6 ?

IPv6 utilise des adresses de 128 bits. Il fournit un espace d'adressage beaucoup plus vaste qu'IPv4 et définit ses propres mécanismes de découverte des voisins, de configuration et de transmission.

IPv6 n'est pas simplement IPv4 avec des adresses plus longues. Sa conception et certains comportements diffèrent.

## 6.2 Représentation d'une adresse IPv6

Exemple :

```text
2001:db8:1234:10::25/64
```

Cette adresse utilise une représentation abrégée. Les groupes peuvent comporter des zéros en tête omis et une séquence de groupes nuls peut être comprimée à l'aide de `::` une fois dans une adresse.

Le préfixe `/64` signifie que 64 bits identifient le préfixe réseau dans cet exemple. Le choix du préfixe doit suivre l'architecture IPv6 adoptée.

Les adresses qui commencent par `2001:db8::/32` sont réservées à la documentation ; cette adresse est donc un exemple et n'est pas destinée à un routage public normal.

## 6.3 Concepts IPv6 essentiels

- **Unicast :** adresse d'une interface ou d'une destination individuelle.
- **Multicast :** adresse d'un groupe de destinataires.
- **Link-local :** adresse utilisée dans le contexte d'un lien, notamment pour certaines fonctions de voisinage.
- **NDP :** protocole de découverte des voisins et de fonctions liées, basé sur ICMPv6.
- **SLAAC :** mécanisme permettant à un hôte de configurer certaines informations d'adressage à partir d'annonces de routeur.
- **DHCPv6 :** mécanisme de configuration qui peut fournir des paramètres IPv6 selon l'architecture.

IPv6 n'utilise pas de broadcast au même sens qu'IPv4. Le multicast et NDP jouent des rôles importants.

## 6.4 Dual stack

Le dual stack permet de faire fonctionner IPv4 et IPv6 sur un même équipement ou une même infrastructure.

Il peut faciliter une transition progressive, mais impose de maîtriser deux ensembles de paramètres et de chemins. Une application peut réussir en IPv4 mais échouer en IPv6, ou l'inverse.

Les tests doivent vérifier les deux familles lorsque les services sont censés les prendre en charge.

## 6.5 Sécurité IPv6

Ne supposez pas qu'IPv6 est absent ou inoffensif simplement parce que l'infrastructure est principalement administrée en IPv4.

Il faut contrôler :

- les annonces de routeur ;
- les politiques de filtrage IPv6 ;
- l'accès de gestion ;
- les règles appliquées aux flux entrants et sortants ;
- le comportement des équipements qui prennent en charge les deux familles ;
- la visibilité des adresses et routes IPv6 dans les outils de supervision.

Une politique qui ne filtre que l'IPv4 peut laisser des chemins IPv6 insuffisamment contrôlés.

---

# 7. Segmentation et architecture de sécurité

## 7.1 La segmentation comme réduction du risque

La segmentation permet de séparer des domaines de trafic selon les fonctions, les identités, les niveaux de confiance ou les besoins métier.

Exemples :

- utilisateurs ;
- serveurs ;
- administration ;
- invités ;
- équipements industriels ;
- services sensibles.

Les VLAN peuvent assurer une séparation de couche 2, mais les politiques de communication entre segments doivent être appliquées par les mécanismes de sécurité et de routage appropriés.

## 7.2 Défense en profondeur

Une architecture sécurisée ne dépend pas d'une seule barrière.

Elle peut combiner :

- segmentation ;
- politiques de pare-feu ;
- contrôle d'accès réseau ;
- authentification et autorisation ;
- protection des interfaces de gestion ;
- journalisation ;
- mises à jour ;
- supervision ;
- séparation des responsabilités ;
- sauvegarde et récupération.

Ces contrôles doivent être conçus ensemble. Ajouter un nouveau dispositif sans intégrer sa gestion ni sa supervision peut introduire des points aveugles.

## 7.3 Zones de confiance

Une architecture peut définir plusieurs zones :

| Zone | Exemple de contenu | Politique générale |
|---|---|---|
| Utilisateurs | Postes et terminaux | Accès aux services autorisés |
| Serveurs | Applications métier | Flux nécessaires aux applications |
| Administration | Outils et interfaces de gestion | Accès fortement restreint |
| Invités | Appareils non gérés | Accès Internet limité, isolation interne |
| Industrielle | Contrôleurs et automates | Flux explicitement définis selon les besoins |

Cette classification est illustrative. Les zones réelles et les politiques doivent être définies selon les activités et les exigences de sécurité.

## 7.4 Vérifier les flux attendus

Une politique de sécurité devrait préciser :

- la source ;
- la destination ;
- le protocole et le port lorsque c'est pertinent ;
- la justification métier ;
- le sens du flux ;
- le responsable ;
- la durée ou la condition de maintien ;
- les journaux et contrôles nécessaires.

Des règles trop permissives augmentent la portée d'un incident. Des règles trop restrictives peuvent interrompre des services. La bonne configuration résulte d'une analyse et de tests appropriés.

---

# 8. Haute disponibilité et convergence

## 8.1 Disponibilité et redondance

La disponibilité dépend de plusieurs composants : équipements, liens, alimentation, opérateurs, services d'infrastructure, configuration, surveillance et capacité à récupérer.

Ajouter deux équipements sans analyser les dépendances communes peut donner une illusion de haute disponibilité.

Une architecture réellement résiliente identifie les scénarios de panne et prévoit des chemins ou services alternatifs.

## 8.2 Convergence

La convergence est le processus par lequel le réseau retrouve un état cohérent de contrôle et de transfert après un changement ou une défaillance.

Sa durée dépend du protocole, de la topologie, des minuteries, de l'implémentation et des mécanismes complémentaires.

Une convergence rapide peut limiter l'interruption, mais ne garantit pas à elle seule une continuité parfaite : les sessions applicatives, les buffers, les mécanismes de redondance et les chemins retour influencent également le résultat.

## 8.3 Redondance active et passive

Selon la technologie, une architecture peut utiliser :

- un chemin préféré et un chemin de secours ;
- plusieurs chemins actifs ;
- des équipements en haute disponibilité ;
- des liens agrégés ;
- des passerelles virtuelles redondantes.

La stratégie doit définir comment le trafic bascule, comment le retour au chemin normal s'effectue et comment éviter des oscillations ou des basculements répétés.

## 8.4 Analyse des risques

Pour chaque composant critique, demandez-vous :

1. quel est son mode de défaillance ?
2. quels services seront touchés ?
3. existe-t-il une redondance indépendante ?
4. le mécanisme de bascule a-t-il été testé ?
5. les équipes seront-elles alertées ?
6. une intervention manuelle sera-t-elle nécessaire ?
7. le rétablissement pourra-t-il être vérifié ?

Un mécanisme de secours qui n'a jamais été testé peut échouer au moment précis où il est nécessaire.

---

# 9. Performances, QoS et MTU

## 9.1 Le débit ne suffit pas à caractériser la qualité

Une application peut être affectée par la latence, la gigue, les pertes, les délais de traitement ou la saturation d'un lien.

L'impact varie selon l'application. Une sauvegarde volumineuse ne réagit pas comme une conversation en temps réel ou une application transactionnelle.

Il faut donc identifier la métrique qui correspond au service à protéger.

## 9.2 QoS

La qualité de service (QoS) comprend les mécanismes permettant de classifier, marquer, mettre en file d'attente, ordonnancer et parfois limiter le trafic.

L'objectif est de gérer la congestion selon des politiques définies, et non de créer de la capacité physique supplémentaire.

Les classes et priorités doivent être cohérentes de bout en bout. Un marquage seul ne garantit pas un traitement prioritaire si les équipements ne l'interprètent pas conformément à la politique.

Une mauvaise politique QoS peut pénaliser des flux légitimes ou permettre à un trafic non prioritaire d'occuper des ressources destinées aux services critiques.

## 9.3 MTU et découverte du chemin

La MTU limite la taille de l'unité de transmission gérée par un lien ou une interface.

La MTU de bout en bout peut être limitée par le maillon le plus contraignant sur le chemin, selon les mécanismes de fragmentation et de découverte utilisés.

Dans IPv6, les routeurs ne fragmentent pas les paquets en transit comme les routeurs IPv4 pouvaient le faire historiquement : la fragmentation IPv6 est réalisée par les nœuds source à l'aide des mécanismes prévus. La découverte de MTU du chemin et le traitement correct d'ICMPv6 sont donc importants.

Un filtrage inadapté de certains messages ICMP peut provoquer des problèmes de connectivité difficiles à comprendre, notamment pour des paquets de grande taille.

## 9.4 Mesurer les performances

Une méthode correcte doit distinguer :

- la capacité théorique du lien ;
- le débit négocié ;
- le débit utile mesuré ;
- la charge au moment de la mesure ;
- la latence ;
- la variation de latence ;
- les pertes ;
- la qualité observée par l'application.

Un test isolé ne reflète pas nécessairement l'expérience réelle de tous les utilisateurs.

---

# 10. Observabilité et télémétrie

## 10.1 Pourquoi superviser ?

La supervision fournit une visibilité sur l'état du réseau, les performances et les événements.

Un réseau sans visibilité peut continuer à fonctionner tout en subissant des dégradations qui ne sont détectées que lorsque les utilisateurs signalent un incident.

Les systèmes de supervision doivent couvrir à la fois l'état des équipements, les interfaces, les chemins, les services et les événements de sécurité pertinents.

## 10.2 Les sources de données

| Source | Informations possibles |
|---|---|
| SNMP | Compteurs, états et informations des équipements selon les MIB exposées |
| Syslog | Événements et messages d'exploitation |
| NetFlow/IPFIX | Informations agrégées sur certains flux |
| Télémétrie en continu | Mesures structurées envoyées par les équipements compatibles |
| Capture de paquets | Détails des échanges observés sur un point donné |
| Logs applicatifs | Erreurs et délais constatés par les applications |
| Tests synthétiques | Vérification périodique d'un service ou d'un chemin |

Aucune source ne fournit à elle seule une vue parfaite. Les données doivent être corrélées et interprétées selon leurs limites.

## 10.3 Indicateurs importants

Un système de supervision peut suivre :

- disponibilité des interfaces ;
- erreurs et abandons de paquets ;
- utilisation des liens ;
- état des voisinages de routage ;
- changements de topologie ;
- pertes et délais ;
- qualité d'un service ;
- état des alimentations et du matériel ;
- changements de configuration ;
- incidents de sécurité.

Les seuils doivent être adaptés à l'infrastructure. Une alerte qui se déclenche continuellement sans action possible perd rapidement son utilité.

## 10.4 Baselines

Une baseline décrit un comportement de référence dans des conditions définies.

Elle permet de comparer l'état présent aux périodes habituelles : charge, trafic, latence ou fréquence d'événements.

Les anomalies doivent être interprétées dans leur contexte. Une hausse de trafic est parfois normale ; à d'autres moments, elle peut indiquer une boucle, une attaque ou une dégradation.

---

# 11. Méthode d'analyse des incidents complexes

## 11.1 Formuler des hypothèses testables

Face à un incident, évitez les conclusions immédiates comme « le routeur est en panne » sans preuve.

Formulez plusieurs hypothèses :

- lien physique dégradé ;
- mauvais état de VLAN ;
- adresse ou masque incorrect ;
- route manquante ;
- chemin retour absent ;
- règle de sécurité bloquante ;
- problème DNS ;
- service distant indisponible ;
- MTU ou filtrage ICMP inadapté ;
- saturation ou pertes sur un lien.

Pour chaque hypothèse, définissez une observation qui permet de la confirmer ou de la réduire.

## 11.2 Séparer l'état du contrôle et celui du transfert

Lorsque c'est pertinent, vérifiez :

1. les interfaces physiques et logiques ;
2. les VLAN et tables de commutation ;
3. les voisins et sessions des protocoles de routage ;
4. les routes connues ;
5. les routes installées dans les structures de transfert ;
6. les prochains sauts ;
7. les règles de sécurité ;
8. le chemin retour ;
9. la réponse du service applicatif.

Cette liste constitue un guide, pas un ordre universel. Le choix des tests dépend du symptôme, de l'architecture et de l'impact d'une éventuelle collecte.

## 11.3 Captures de paquets

Une capture permet d'examiner les échanges réels : demandes, réponses, retransmissions, erreurs ou absence de réponse au point d'observation.

Une capture est limitée à l'endroit où elle est effectuée. L'absence d'un paquet sur une interface ne prouve pas à elle seule que l'émetteur ne l'a jamais envoyé ; le paquet peut avoir été perdu ou filtré avant le point de capture.

La capture peut également contenir des données sensibles. Contrôlez la collecte, la conservation et le partage des fichiers.

## 11.4 Schéma d'une démarche d'incident

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-labelledby="expert-troubleshoot-title expert-troubleshoot-desc">
  <title id="expert-troubleshoot-title">Démarche experte de diagnostic</title>
  <desc id="expert-troubleshoot-desc">Le diagnostic commence par le symptôme et le périmètre, construit plusieurs hypothèses, recueille les observations, identifie le point de divergence, puis prépare une action maîtrisée et vérifie le résultat. Les flèches animées se limitent aux traits.</desc>
  <defs>
    <marker id="ex-tr-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .xt-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .xt-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .xt-ok{fill:#123126;stroke:#4ade80;stroke-width:2}
      .xt-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .xt-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .xt-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#ex-tr-arrow);animation:xt-dash 1.8s linear infinite}
      @keyframes xt-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="378" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DE L'OBSERVATION À UNE CORRECTION VÉRIFIÉE</text>
  <rect class="xt-box" x="25" y="80" width="165" height="76" rx="10"/>
  <text class="xt-title" x="107" y="108" text-anchor="middle">1. Symptôme</text>
  <text class="xt-text" x="107" y="131" text-anchor="middle">Périmètre et impact</text>
  <rect class="xt-box" x="220" y="80" width="165" height="76" rx="10"/>
  <text class="xt-title" x="302" y="108" text-anchor="middle">2. Hypothèses</text>
  <text class="xt-text" x="302" y="131" text-anchor="middle">Causes possibles</text>
  <rect class="xt-box" x="415" y="80" width="165" height="76" rx="10"/>
  <text class="xt-title" x="497" y="108" text-anchor="middle">3. Collecte</text>
  <text class="xt-text" x="497" y="131" text-anchor="middle">Mesures et traces</text>
  <rect class="xt-gate" x="610" y="80" width="165" height="76" rx="10"/>
  <text class="xt-title" x="692" y="108" text-anchor="middle">4. Localisation</text>
  <text class="xt-text" x="692" y="131" text-anchor="middle">Point de divergence</text>
  <rect class="xt-ok" x="805" y="80" width="130" height="76" rx="10"/>
  <text class="xt-title" x="870" y="108" text-anchor="middle">5. Action</text>
  <text class="xt-text" x="870" y="131" text-anchor="middle">Contrôlée</text>
  <path class="xt-flow" d="M190 118 H213"/>
  <path class="xt-flow" d="M385 118 H408"/>
  <path class="xt-flow" d="M580 118 H603"/>
  <path class="xt-flow" d="M775 118 H798"/>
  <rect class="xt-box" x="205" y="235" width="550" height="70" rx="10"/>
  <text class="xt-title" x="480" y="263" text-anchor="middle">6. Vérification indépendante</text>
  <text class="xt-text" x="480" y="286" text-anchor="middle">Confirmer le rétablissement et fermer l'incident avec des preuves</text>
  <path class="xt-flow" d="M870 156 V202 H755 V243"/>
  <text class="xt-text" x="480" y="338" text-anchor="middle">Si le test échoue, reprendre l'analyse au lieu de répéter la même action sans preuve.</text>
  <text class="xt-text" x="480" y="358" text-anchor="middle">Toute modification doit respecter le périmètre, les autorisations et les procédures de changement.</text>
</svg>

---

# 12. Architecture de référence

## 12.1 Exemple de réseau d'entreprise

Une architecture d'entreprise peut séparer les réseaux d'accès, de distribution, de cœur et de bordure. Cette organisation logique doit être adaptée à la taille et aux exigences réelles.

Exemple conceptuel :

```text
                    Internet / opérateurs
                            |
                     Routeurs de bordure
                            |
                      Pare-feu externes
                            |
                    Cœur de réseau redondant
                       /             \
                Distribution A    Distribution B
                  /      \          /      \
             Accès A1  Accès A2  Accès B1  Accès B2
                 |        |         |        |
             Utilisateurs, téléphones, points d'accès
                            |
                Réseaux serveurs et services internes
```

Ce dessin ne définit pas les mécanismes précis de redondance, les protocoles de routage ou les zones de sécurité. Il constitue une vue d'organisation. Un design réel doit inclure les liens, les chemins retour, les dépendances électriques et physiques et les modes de panne.

## 12.2 Choisir une architecture selon les besoins

Une petite organisation peut fonctionner correctement avec une conception relativement simple. Une infrastructure importante peut nécessiter plusieurs domaines de routage, des mécanismes de redondance et des politiques de segmentation plus élaborées.

La complexité doit être justifiée par des exigences identifiables : disponibilité, évolutivité, sécurité, débit, latence ou séparation administrative.

Ajouter des équipements ou des protocoles sans définir leur rôle augmente les coûts, les risques de configuration et la difficulté de diagnostic.

---

# 13. Étude de panne

## Situation

Un site distant perd l'accès à une application située dans le centre de données. Certains services restent accessibles, et une partie du trafic passe encore entre les sites.

## 13.1 Hypothèses initiales

Les causes possibles comprennent :

- une route vers le préfixe de l'application absente ou modifiée ;
- une politique de routage qui préfère un chemin inattendu ;
- une règle de pare-feu qui bloque le flux ;
- une panne partielle de liaison ;
- un problème de chemin retour ;
- une MTU incompatible ;
- une résolution DNS vers une mauvaise adresse ;
- un incident propre au serveur ou à l'application.

## 13.2 Collecter les faits

Il faut préciser :

- quels utilisateurs et sous-réseaux sont touchés ;
- les destinations concernées ;
- les protocoles et ports ;
- l'heure du début de l'incident ;
- les changements récemment effectués ;
- l'état des interfaces et liens ;
- les routes pertinentes dans les deux sens ;
- les compteurs d'erreurs et de pertes ;
- les journaux de pare-feu et du service concerné.

La collecte doit utiliser des sources autorisées et conserver les traces nécessaires à l'analyse.

## 13.3 Localiser le point de divergence

Comparez un flux fonctionnel à un flux en échec lorsque les deux peuvent être observés dans des conditions comparables.

Vérifiez progressivement :

1. la résolution du nom ;
2. l'adresse IP de destination ;
3. le prochain saut ;
4. les routes d'aller et de retour ;
5. les règles de sécurité ;
6. le port et la réponse applicative ;
7. les MTU et les pertes si les symptômes le suggèrent.

Un chemin aller correct ne garantit pas que le retour utilise un chemin fonctionnel ou autorisé.

## 13.4 Corriger et confirmer

Lorsque la cause est suffisamment étayée :

1. définir une action de correction adaptée ;
2. vérifier les risques et dépendances ;
3. obtenir l'autorisation nécessaire ;
4. appliquer le changement contrôlé ;
5. répéter les tests pertinents ;
6. confirmer le fonctionnement des services ;
7. documenter la cause, la correction et les mesures préventives.

Ne clôturez pas l'incident au seul motif que l'interface physique est remontée ou qu'un test ICMP réussit.

---

# 14. Atelier expert

## Scénario

Vous devez examiner une architecture comportant deux sites, plusieurs VLAN, un routage dynamique et une connexion Internet redondante.

L'objectif est de produire un plan d'analyse et une architecture documentée, pas de reconfigurer immédiatement les routeurs de production.

## Étape A — Documenter la topologie

Pour chaque site, identifiez :

- les préfixes IPv4 et IPv6 ;
- les VLAN ;
- les passerelles ;
- les équipements de routage ;
- les liens principaux et de secours ;
- les services DNS et DHCP ;
- les zones de sécurité ;
- les chemins vers les applications centrales.

## Étape B — Vérifier la cohérence d'adressage

Recherchez :

- les chevauchements entre préfixes ;
- les allocations qui ne correspondent à aucun site ;
- les plages insuffisantes ;
- les résumés qui englobent des réseaux inexistants ;
- les différences entre le plan et les paramètres opérationnels.

## Étape C — Définir les scénarios de panne

Exemples :

- perte d'un lien WAN ;
- défaillance d'un routeur ;
- perte d'un voisinage de routage ;
- erreur de politique de routage ;
- panne DNS ;
- rupture d'un lien inter-VLAN ;
- problème MTU sur un chemin redondant.

Pour chaque scénario, décrivez l'impact, les signes attendus, les tests qui permettent de le détecter et la procédure de récupération.

## Étape D — Formaliser les critères de service

Identifiez les services prioritaires et les résultats mesurables :

- disponibilité ;
- délai acceptable ;
- taux de pertes ;
- temps de bascule ;
- accessibilité des destinations ;
- maintien des restrictions de sécurité.

Les valeurs cibles doivent être définies selon les besoins de l'organisation et ses engagements de service.

## Étape E — Préparer une amélioration

Choisissez une faiblesse identifiée et formulez une mesure concrète : corriger un résumé de routes, améliorer la supervision d'un voisinage, clarifier la segmentation ou tester une procédure de bascule.

La mesure doit posséder un critère de réussite vérifiable.

---

# 15. Évaluation corrigée

## Questions

1. Quelle différence existe entre le plan de contrôle et le plan de données ?
2. Quelle différence existe entre la RIB et la FIB ?
3. Pourquoi faut-il éviter les chevauchements de préfixes ?
4. À quoi sert l'agrégation de routes ?
5. Quelle différence existe entre OSPF et BGP dans leurs usages habituels ?
6. Pourquoi une boucle de couche 2 peut-elle provoquer une panne étendue ?
7. Quel est le rôle de STP ?
8. Pourquoi une agrégation de liens ne double-t-elle pas forcément le débit d'un seul flux ?
9. Quelle différence existe entre IPv4 et IPv6 concernant le broadcast et la découverte des voisins ?
10. Pourquoi une politique de sécurité doit-elle couvrir IPv6 lorsque celui-ci est activé ?
11. Pourquoi la redondance logique ne garantit-elle pas une diversité physique ?
12. Quelle différence existe entre latence, gigue, pertes et débit ?
13. Pourquoi la découverte de MTU du chemin est-elle importante ?
14. Quelle est la méthode correcte pour traiter un incident complexe ?

## Corrigé

**1. Plan de contrôle et plan de données**

Le plan de contrôle construit ou maintient les informations utilisées par le réseau ; le plan de données transfère effectivement les paquets et les trames.

**2. RIB et FIB**

La RIB conserve les routes connues par le système de routage. La FIB contient les informations utilisées pour transférer les paquets.

**3. Chevauchements de préfixes**

Ils compliquent la sélection des chemins, l'interconnexion et le diagnostic ; ils peuvent créer des décisions de routage inattendues.

**4. Agrégation**

Elle regroupe des préfixes compatibles afin de réduire la quantité de routes annoncées ou stockées, à condition que le résumé corresponde réellement au réseau desservi.

**5. OSPF et BGP**

OSPF est un protocole à état de liens utilisé notamment à l'intérieur d'un domaine de routage. BGP est un protocole interdomaines fondé sur l'échange de chemins et des politiques de sélection.

**6. Boucle de couche 2**

Elle peut faire circuler de nombreuses trames de manière répétée, saturer le réseau et provoquer une instabilité des tables MAC.

**7. STP**

Il aide à empêcher les boucles de transfert dans une topologie Ethernet redondante.

**8. Débit d'une agrégation**

La distribution des flux dépend de l'algorithme de répartition. Un flux unique peut rester affecté à un seul lien physique.

**9. IPv4 et IPv6**

IPv4 utilise le broadcast dans plusieurs mécanismes locaux, alors qu'IPv6 s'appuie notamment sur le multicast et NDP pour la découverte des voisins.

**10. Sécurité IPv6**

Un filtrage uniquement IPv4 peut laisser des voies de communication IPv6 insuffisamment contrôlées.

**11. Redondance et diversité physique**

Deux liens logiquement distincts peuvent partager un même chemin physique ou équipement critique, et échouer ensemble.

**12. Mesures de performance**

La latence mesure un délai, la gigue sa variation, les pertes les paquets qui n'atteignent pas la destination prévue et le débit la quantité de données transportée par unité de temps.

**13. MTU du chemin**

Des tailles incompatibles ou une mauvaise gestion des messages nécessaires à la découverte peuvent empêcher certains paquets de circuler correctement.

**14. Incident complexe**

Il faut établir le symptôme, former des hypothèses testables, recueillir des preuves, localiser le point de divergence, appliquer une correction autorisée et confirmer le résultat réel.

---

# Conclusion — Comprendre un réseau au niveau expert

Un réseau fiable résulte d'une architecture cohérente, de chemins maîtrisés, d'un adressage organisé, de politiques de sécurité explicites et de mécanismes de supervision adaptés.

La maîtrise experte implique :

- de comprendre les interactions entre les composants ;
- de concevoir des chemins de données robustes ;
- de distinguer les informations de contrôle du transfert réel ;
- de limiter les boucles et les effets de panne ;
- d'intégrer IPv4 et IPv6 dans une politique commune ;
- de tester la redondance ;
- de mesurer les services et non seulement l'état des interfaces ;
- de dépanner à partir de preuves ;
- d'améliorer continuellement l'architecture à partir des incidents observés.

Le parcours complet est désormais structuré :

**Débutant :** comprendre les réseaux, les équipements et les protocoles essentiels.

**Intermédiaire :** expliquer l'adressage, les VLAN, le routage et les mécanismes de dépannage.

**Expert :** concevoir l'architecture, maîtriser la résilience, la sécurité, les performances et les incidents complexes.

**La compétence réseau ne consiste pas seulement à faire communiquer deux appareils : elle consiste à concevoir, maintenir et vérifier un système de communication qui reste maîtrisé lorsque les conditions changent et que des composants tombent en panne.**

---

## Références utiles

- RFC 1918 — Adresses privées IPv4 : https://www.rfc-editor.org/rfc/rfc1918.html
- RFC 791 — Internet Protocol IPv4 : https://www.rfc-editor.org/rfc/rfc791.html
- RFC 8200 — IPv6 : https://www.rfc-editor.org/rfc/rfc8200.html
- RFC 4271 — BGP-4 : https://www.rfc-editor.org/rfc/rfc4271.html
- RFC 2328 — OSPF version 2 : https://www.rfc-editor.org/rfc/rfc2328.html
- RFC 9293 — TCP : https://www.rfc-editor.org/rfc/rfc9293.html
- RFC 1191 — Découverte de la MTU du chemin IPv4 : https://www.rfc-editor.org/rfc/rfc1191.html
- RFC 8201 — Découverte de la MTU du chemin IPv6 : https://www.rfc-editor.org/rfc/rfc8201.html
- RFC 4861 — Neighbor Discovery IPv6 : https://www.rfc-editor.org/rfc/rfc4861.html
- RFC 3411 — Architecture SNMP : https://www.rfc-editor.org/rfc/rfc3411.html
- IEEE 802.1Q — VLAN : https://standards.ieee.org/standard/802_1Q-2022.html

**Fichier :** `intro-reseau-expert.md`  
**Niveau :** Expert  
**Fin du cours**
