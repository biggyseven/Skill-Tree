# Cisco SD-Access — Niveau Intermédiaire

> **Fichier :** `sd-access-intermediaire.md`  
> **Parcours :** Architecture Réseau → Cisco SD-Access → Niveau Intermédiaire  
> **Objectif :** passer des concepts du niveau débutant à la conception, à la préparation du déploiement et au diagnostic d’une fabric de campus de taille moyenne.  
> **Public :** techniciens réseau ayant acquis les notions de VLAN, IPv4/IPv6, routage, underlay/overlay, rôles fabric, LISP, VXLAN, VN/VRF et SGT.  
> **Important :** les exemples décrivent des intentions de conception. Les workflows, rôles supportés, commandes, limites et versions doivent être vérifiés dans la documentation Cisco correspondant au matériel, aux licences et à la version de Catalyst Center / IOS XE déployés.

## Comment utiliser ce cours

Ce cours poursuit le niveau débutant. Il ne re-développe pas chaque protocole élémentaire : il s’intéresse surtout aux interactions entre les composants, aux choix d’architecture, aux dépendances et aux preuves nécessaires avant une mise en production. Pour chaque section, essaie de produire un livrable concret : schéma, table de décision, liste de prérequis, test ou procédure de retour arrière.

### Prérequis conseillés

- Savoir distinguer underlay et overlay ; comprendre LISP, VXLAN, VN/VRF et SGT à un niveau introductif.
- Connaître les bases du routage IP, de la redondance L2/L3, de DHCP/DNS/NTP et de l’authentification 802.1X.
- Comprendre que Catalyst Center orchestre la solution, qu’ISE fournit les fonctions d’identité et que les équipements fabric assurent le forwarding.

## 1. Passer du concept à la conception

Au niveau débutant, on a décrit les fonctions principales de SD-Access. Au niveau intermédiaire, l’enjeu est de décider **où placer les rôles**, **quels réseaux logiques créer**, **comment raccorder les services partagés**, **quels chemins doivent survivre à une panne** et **comment prouver que le résultat répond aux besoins métier**.

Une bonne conception ne part pas d’une liste d’équipements, mais des flux, des objectifs de disponibilité, des contraintes de sécurité, de la topologie physique et des opérations quotidiennes. Le contrôleur facilite l’implémentation, mais il ne remplace ni l’analyse des dépendances ni une conception IP cohérente.

### Livrables minimaux de conception

1. Diagramme physique et diagramme logique, chacun avec légende claire.
2. Plan d’adressage et rôle des loopbacks/RLOC dans l’underlay.
3. Table des VN, pools, passerelles, services et domaines de sécurité.
4. Matrice de flux autorisés et refusés, y compris les flux nécessaires aux services d’infrastructure.
5. Matrice de compatibilité du matériel, du logiciel, des licences et des fonctions retenues.
6. Plan de migration, tests d’acceptation, critères d’arrêt et procédure de rollback.

### Diagramme 1 — Cycle de conception et d’exploitation

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="455" viewBox="0 0 1000 455"><rect x="1" y="1" width="998" height="453" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Cycle de conception et d’exploitation SD-Access</text><rect x="28" y="82" width="284" height="300" rx="16" fill="#111D30" stroke="#3E536F" stroke-width="2" /><rect x="358" y="82" width="284" height="300" rx="16" fill="#111D30" stroke="#3E536F" stroke-width="2" /><rect x="688" y="82" width="284" height="300" rx="16" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="170" y="117" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="600" fill="#C4A1FF" text-anchor="middle">PLANIFICATION</text><text x="500" y="117" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="600" fill="#36D6B0" text-anchor="middle">FABRIC</text><text x="830" y="117" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="600" fill="#68AEFF" text-anchor="middle">EXPLOITATION</text><rect x="54" y="147" width="232" height="58" rx="10" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="170" y="170" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Politique cible</text><text x="170" y="190" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN / SGT / identité</text><rect x="54" y="222" width="232" height="58" rx="10" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="170" y="245" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Modèle du site</text><text x="170" y="265" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">rôles / capacité</text><rect x="54" y="297" width="232" height="58" rx="10" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="170" y="320" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Pré-requis</text><text x="170" y="340" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">IP / DNS / NTP / AAA</text><rect x="384" y="147" width="232" height="58" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="500" y="170" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Underlay L3</text><text x="500" y="190" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">reachability / MTU</text><rect x="384" y="222" width="232" height="58" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="500" y="245" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Overlay fabric</text><text x="500" y="265" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">LISP / VXLAN</text><rect x="384" y="297" width="232" height="58" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="500" y="320" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Politique</text><text x="500" y="340" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN / SGT</text><rect x="714" y="147" width="232" height="58" rx="10" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="830" y="170" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Assurance</text><text x="830" y="190" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">état / chemins</text><rect x="714" y="222" width="232" height="58" rx="10" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="830" y="245" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Changements</text><text x="830" y="265" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">contrôle / rollback</text><rect x="714" y="297" width="232" height="58" rx="10" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="830" y="320" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Incidents</text><text x="830" y="340" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">preuve / RCA</text><line x1="312" y1="231" x2="347.0" y2="231.0" stroke="#F4F7FB" stroke-width="3" stroke-linecap="round" /><polygon points="358,231 347.0,236.72 347.0,225.28" fill="#F4F7FB" /><line x1="642" y1="231" x2="677.0" y2="231.0" stroke="#F4F7FB" stroke-width="3" stroke-linecap="round" /><polygon points="688,231 677.0,236.72 677.0,225.28" fill="#F4F7FB" /><text x="500" y="426" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#C1CCDA" text-anchor="middle">Une bonne fabric commence par les dépendances, les objectifs et les critères de validation.</text></svg>

## 2. Modèles de site et placement des rôles

Un site SD-Access possède des fonctions d’edge, de control plane et de border lorsque l’accès aux réseaux externes est nécessaire. Un nœud peut parfois héberger plusieurs rôles, mais la colocalisation n’est pas gratuite : elle modifie le domaine de panne, la capacité, la convergence et la facilité de maintenance. Séparer les rôles peut améliorer l’isolation des pannes et l’évolutivité, tandis que les colocaliser peut réduire les coûts et la complexité dans un petit site.

Le bon choix dépend de la taille du site, du nombre d’endpoints, du débit attendu, de la croissance, du nombre de VN, de la topologie WAN, de la disponibilité exigée et des combinaisons de rôles effectivement supportées. Ne pas extrapoler un modèle « Fabric in a Box » à un campus important sans analyser ses limites et ses objectifs de résilience.

| Sujet | Questions à se poser | Risque si ignoré |
|---|---|---|
| Edge | Combien d’accès, de terminaux, de ports et de flux ? | Saturation ou domaine de panne trop large |
| Control plane | Comment préserver la disponibilité des mappings ? | Incidents de localisation et impact sur les changements/mobilités |
| Border | Combien de domaines externes, VN, routes et handoffs ? | Goulot d’étranglement ou sortie unique |
| Intermediate | Le transport L3 et le MTU sont-ils uniformes ? | Pertes sélectives et tunnels instables |
| Wireless | Quels modes, contrôleurs, AP et domaines de mobilité ? | Chemins inattendus ou expérience Wi-Fi dégradée |

### Diagramme 2 — Disponibilité et domaines de panne

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="435" viewBox="0 0 1000 435"><rect x="1" y="1" width="998" height="433" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Checklist de l’underlay : dépendances du transport</text><rect x="35" y="100" width="210" height="82" rx="13" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="140" y="132" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Loopbacks / RLOC</text><text x="140" y="153" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">adressage cohérent</text><rect x="285" y="100" width="210" height="82" rx="13" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="390" y="132" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Routage L3</text><text x="390" y="153" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">OSPF / IS-IS*</text><rect x="535" y="100" width="210" height="82" rx="13" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="640" y="132" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">MTU de bout en bout</text><text x="640" y="153" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VXLAN + marge</text><rect x="785" y="100" width="180" height="82" rx="13" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="875" y="132" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">ECMP / chemins</text><text x="875" y="153" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">redondants</text><line x1="245" y1="141" x2="274.0" y2="141.0" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="285,141 274.0,146.72 274.0,135.28" fill="#68AEFF" /><line x1="495" y1="141" x2="524.0" y2="141.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="535,141 524.0,146.72 524.0,135.28" fill="#36D6B0" /><line x1="745" y1="141" x2="774.0" y2="141.0" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="785,141 774.0,146.72 774.0,135.28" fill="#FFBD69" /><rect x="90" y="260" width="820" height="92" rx="16" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="500" y="292" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="600" fill="#F4F7FB" text-anchor="middle">Avant d’analyser l’overlay</text><text x="500" y="322" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#C1CCDA" text-anchor="middle">Vérifier l’adjacence L3, la route RLOC, le MTU, la perte et la stabilité des liens.</text><line x1="500" y1="182" x2="500.0" y2="249.0" stroke="#F4F7FB" stroke-width="3" stroke-linecap="round" /><polygon points="500,260 494.28,249.0 505.72,249.0" fill="#F4F7FB" /><text x="500" y="398" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#FFBD69" text-anchor="middle">*Le protocole exact dépend du design pris en charge et de la politique d’exploitation.</text></svg>

### Méthode de décision

1. Écris l’objectif de disponibilité en langage mesurable : par exemple, perte acceptable, temps maximal de bascule et fenêtre de maintenance.
2. Identifie les pannes indépendantes et les dépendances communes (alimentation, rack, fibre, logiciel, contrôleur de gestion, services AAA, WAN).
3. Choisis la séparation des rôles et les chemins redondants à partir de ces scénarios.
4. Valide la conception par des tests de panne : retirer un lien, perdre un uplink, arrêter un nœud ou simuler l’indisponibilité d’un service non critique, selon le plan autorisé.
5. Documente le comportement attendu, le comportement mesuré et les écarts.

## 3. Underlay : conditions de stabilité avant l’overlay

Le underlay est le transport IP entre les points nécessaires à la fabric. La fabric ne peut pas compenser des routes RLOC manquantes, une convergence non déterministe, un filtrage de contrôle involontaire ou un MTU trop faible. Le routage underlay doit être prévisible, documenté et observable.

### Adressage et reachability

- Utiliser un plan d’adressage cohérent pour les liens routés et les loopbacks définies par le design.
- Vérifier les préfixes, les masques, la portée des annonces et l’absence de chevauchement avec les environnements externes.
- Déterminer les interfaces qui portent les RLOC et valider le chemin aller **et** le chemin retour.
- Éviter les dépendances implicites à une route par défaut lorsqu’une fonction requiert une reachability spécifique entre nœuds fabric.
- Maintenir des sources de temps et de résolution de noms fiables pour les systèmes de gestion et d’identité.

### Routage et convergence

Le protocole exact dépend du design validé et des fonctionnalités supportées. L’objectif est que chaque RLOC requis soit joignable via des chemins connus, que les adjacences se rétablissent de façon prévisible et que les boucles soient évitées. Les métriques et les chemins ECMP doivent être considérés avec les limites matérielles et l’objectif de convergence.

### MTU et encapsulation

VXLAN ajoute un en-tête extérieur au paquet interne ; la taille maximale sur le chemin doit donc être suffisante. Mesurer le MTU local d’un lien ne prouve pas que le plus petit MTU de toute la route est compatible. Vérifier les trunks, les interfaces L3, les liens d’agrégation, les opérateurs WAN et tout équipement intermédiaire. Les valeurs recommandées dans les guides peuvent être élevées ; choisir la valeur depuis le guide officiel de la version et tester le chemin réel.

### Diagramme 3 — Dépendances underlay

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="435" viewBox="0 0 1000 435"><rect x="1" y="1" width="998" height="433" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Disponibilité : penser aux domaines de panne</text><rect x="60" y="95" width="255" height="100" rx="14" fill="#182941" stroke="#C4A1FF" stroke-width="3" /><text x="187" y="126" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Control plane A</text><text x="187" y="147" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Mappings endpoint ↔ RLOC</text><rect x="60" y="238" width="255" height="100" rx="14" fill="#182941" stroke="#C4A1FF" stroke-width="3" /><text x="187" y="269" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Control plane B</text><text x="187" y="290" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Redondance / disponibilité</text><rect x="380" y="160" width="230" height="100" rx="14" fill="#1D3553" stroke="#36D6B0" stroke-width="3" /><text x="495" y="191" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Edge nodes</text><text x="495" y="213" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">accès et Anycast GW</text><rect x="680" y="160" width="260" height="100" rx="14" fill="#182941" stroke="#FFBD69" stroke-width="3" /><text x="810" y="191" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Border nodes</text><text x="810" y="213" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">sortie / interconnexion</text><line x1="315" y1="145" x2="370.95588589191846" y2="183.73869023286662" stroke="#C4A1FF" stroke-width="3" stroke-linecap="round" /><polygon points="380,190 367.7000048130091,188.44162956906902 374.2117669708278,179.0357508966642" fill="#C4A1FF" /><line x1="315" y1="287" x2="371.72954324657" y2="237.25255438377707" stroke="#C4A1FF" stroke-width="3" stroke-linecap="round" /><polygon points="380,230 375.5008715261341,241.55319189556067 367.9582149670059,232.95191687199346" fill="#C4A1FF" /><line x1="610" y1="210" x2="669.0" y2="210.0" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="680,210 669.0,215.72 669.0,204.28" fill="#FFBD69" /><text x="495" y="308" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">Les rôles peuvent être colocalisés selon design et plateforme</text><rect x="375" y="355" width="570" height="54" rx="10" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="660" y="388" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#FF7788" text-anchor="middle">Redondance ≠ absence de point commun de panne</text><text x="185" y="390" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">Tester perte du nœud</text></svg>

### Plan de validation underlay

| Test | Résultat recherché | Preuve |
|---|---|---|
| Reachability des loopbacks/RLOC | Chaque source atteint les destinations requises | Ping sourcé, route et tracé adaptés |
| Adjacences | État stable, pas de flapping | État du protocole et journaux horodatés |
| MTU | Paquets de taille requise traversent le chemin | Test de taille contrôlée sans fragmentation inattendue |
| Redondance | Un chemin alternatif prend le relais | Test de retrait d’un lien approuvé |
| Filtrage | Le contrôle nécessaire est permis | ACL / pare-feu / compteurs examinés |

## 4. VN/VRF, adressage et services partagés

Une VN correspond à un réseau logique de la fabric ; dans les conceptions courantes, elle s’appuie sur une instance de routage VRF. Les VN doivent être créées en fonction des besoins réels d’isolation, pas simplement parce que deux types d’équipements portent des étiquettes différentes. Multiplier les VN augmente aussi les exigences de routage, de pools, de services partagés et de tests.

### Construire une table de conception

| VN de l’exemple | Population | Exemple de services requis | Restrictions initiales |
|---|---|---|---|
| `VN_CORP` | Personnel interne | DHCP, DNS, NTP, applications métier | Accès selon fonction et groupe |
| `VN_GUEST` | Visiteurs | DHCP, DNS, portail, Internet | Refus d’accès aux réseaux internes |
| `VN_IOT` | Capteurs, bâtiment | DNS/NTP si nécessaire, brokers/serveurs dédiés | Flux strictement allowlistés |
| `VN_IT` | Administration | AAA, bastion, supervision | Accès limité aux administrateurs autorisés |

Les plages ci-dessus sont des noms de conception, pas des valeurs ou capacités imposées par Cisco. Attribuer ensuite les pools non chevauchants, les plages DHCP, les réservations, les options requises, les relais si nécessaires et les routes vers les services.

### Services partagés : trois modèles

1. **Services dans une VN partagée** : un design peut rendre certains services accessibles depuis plusieurs VN à travers des mécanismes explicitement conçus. Il faut contrôler le routage, les ACL et le chemin retour.
2. **Services répliqués par domaine** : certains services peuvent être distribués pour réduire les dépendances inter-VN ou inter-sites, au prix d’une gestion supplémentaire.
3. **Accès par frontière contrôlée** : un pare-feu ou un point de service VRF-aware applique des règles entre la VN source et le réseau des services.

Ne considère pas un serveur « partagé » comme automatiquement accessible à toutes les VN. Le routage et la politique doivent rendre chaque flux explicite.

### Diagramme 4 — VN et services partagés

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="435" viewBox="0 0 1000 435"><rect x="1" y="1" width="998" height="433" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">VN/VRF et SGT : deux dimensions complémentaires</text><rect x="35" y="88" width="440" height="320" rx="16" fill="#111D30" stroke="#3E536F" stroke-width="2" /><rect x="525" y="88" width="440" height="320" rx="16" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="255" y="121" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="600" fill="#68AEFF" text-anchor="middle">MACRO-SEGMENTATION</text><text x="745" y="121" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="600" fill="#FFBD69" text-anchor="middle">MICRO-SEGMENTATION</text><rect x="65" y="150" width="170" height="72" rx="11" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="150" y="178" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN CORP</text><text x="150" y="199" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VRF A</text><rect x="265" y="150" width="170" height="72" rx="11" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="350" y="178" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN IOT</text><text x="350" y="199" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VRF B</text><line x1="235" y1="185" x2="265" y2="185" stroke="#FF7788" stroke-width="4" stroke-linecap="round" /><text x="250" y="172" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="600" fill="#FF7788" text-anchor="middle">isolé</text><text x="255" y="260" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">VRF sépare les tables de routage</text><text x="255" y="295" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Une route entre VN doit être prévue</text><text x="255" y="340" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#68AEFF" text-anchor="middle">Ne remplace pas toute politique d’accès</text><rect x="560" y="151" width="112" height="64" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="616" y="177" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="middle">SGT 10</text><text x="616" y="195" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="middle">Employés</text><rect x="690" y="151" width="112" height="64" rx="10" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="746" y="177" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="middle">SGT 20</text><text x="746" y="195" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="middle">IoT</text><rect x="820" y="151" width="112" height="64" rx="10" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="876" y="177" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="middle">SGT 30</text><text x="876" y="195" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="middle">IT</text><rect x="565" y="244" width="365" height="106" rx="9" fill="#1D3553" stroke="#526984" stroke-width="1" /><text x="585" y="269" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#36D6B0" text-anchor="start">Source</text><text x="700" y="269" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#36D6B0" text-anchor="start">Cible</text><text x="825" y="269" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#36D6B0" text-anchor="start">Décision</text><text x="585" y="296" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="start">Employés</text><text x="700" y="296" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="start">Serveur</text><text x="825" y="296" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="start">Autoriser*</text><text x="585" y="323" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="start">IoT</text><text x="700" y="323" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="start">Postes</text><text x="825" y="323" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#FF7788" text-anchor="start">Refuser*</text><text x="745" y="378" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#FFBD69" text-anchor="middle">Classification → propagation → enforcement</text><text x="745" y="396" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="600" fill="#C1CCDA" text-anchor="middle">*Exemple illustratif : valider la matrice métier.</text></svg>

### Vérifier un flux entre VN

Pour une connexion de `VN_CORP` vers une application partagée, documente le terminal source, le SGT associé, le préfixe destination, la route, le point d’interconnexion entre les VRF/VN, la règle de sécurité et le chemin retour. Vérifie séparément le DNS, la connectivité IP et l’application. Un ping réussi ne prouve pas que le service TCP, TLS ou applicatif fonctionne correctement.

## 5. Segmentation basée sur l’identité : VN, SGT et règles

La macro-segmentation avec les VN/VRF sépare les tables de routage. La micro-segmentation avec les Security Group Tags (SGT) permet d’exprimer des politiques entre groupes d’endpoints. Les deux sont complémentaires : la VN définit un domaine de routage, tandis que le SGT représente un groupe de sécurité utilisé dans les décisions de politique.

Le workflow de politique comprend au minimum la **classification**, la **propagation** du contexte de groupe et l’**enforcement** de la règle. Une règle dans la matrice n’est utile que si l’identité est attribuée de manière fiable et si le tag est conservé jusqu’au point qui applique la politique. Les frontières vers des équipements ou réseaux classiques méritent une analyse dédiée : un handoff IP traditionnel ne propage pas automatiquement toutes les informations de sécurité de la fabric.

### Construire une matrice de politique

| Groupe source | Groupe cible | Exemple de décision | Justification à inscrire |
|---|---|---|---|
| Employés | Applications métier | Autoriser certains ports | Besoin applicatif validé |
| IoT | Serveurs de collecte IoT | Autoriser le strict nécessaire | Flux de télémétrie connu |
| IoT | Postes utilisateurs | Refuser par défaut | Éviter les mouvements latéraux |
| Invités | Réseaux internes | Refuser | Isolation des visiteurs |
| IT admin | Équipements administrés | Autoriser via chemin contrôlé | Opérations et audit |

Il faut compléter la matrice par les protocoles et ports, les exceptions temporaires, les propriétaires métier, les logs requis et les tests négatifs. Ne laisse pas des règles « permit any » comme solution provisoire sans date d’expiration, responsable et contrôle de retrait.

### Diagramme 5 — Macro et micro-segmentation

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="435" viewBox="0 0 1000 435"><rect x="1" y="1" width="998" height="433" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Chemin de politique SGT et frontière de fabric</text><rect x="28" y="146" width="165" height="98" rx="12" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="110" y="177" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Endpoint</text><text x="110" y="198" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">SGT 10</text><rect x="240" y="146" width="170" height="98" rx="12" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="325" y="177" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Fabric edge</text><text x="325" y="198" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">classification</text><rect x="455" y="146" width="170" height="98" rx="12" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="540" y="177" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">VXLAN fabric</text><text x="540" y="198" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">SGT propagé*</text><rect x="670" y="146" width="155" height="98" rx="12" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="747" y="177" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Border</text><text x="747" y="198" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">handoff</text><rect x="870" y="146" width="100" height="98" rx="12" fill="#182941" stroke="#FF7788" stroke-width="2" /><text x="920" y="177" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Réseau</text><text x="920" y="197" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">peer</text><line x1="193" y1="195" x2="229.0" y2="195.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="240,195 229.0,200.72 229.0,189.28" fill="#36D6B0" /><line x1="410" y1="195" x2="444.0" y2="195.0" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="455,195 444.0,200.72 444.0,189.28" fill="#68AEFF" /><line x1="625" y1="195" x2="659.0" y2="195.0" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="670,195 659.0,200.72 659.0,189.28" fill="#FFBD69" /><line x1="825" y1="195" x2="859.0" y2="195.0" stroke="#FF7788" stroke-width="3" stroke-linecap="round" /><polygon points="870,195 859.0,200.72 859.0,189.28" fill="#FF7788" /><text x="500" y="290" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#F4F7FB" text-anchor="middle">La conservation du tag dépend du type de transit et du design.</text><text x="500" y="324" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#FFBD69" text-anchor="middle">Un IP handoff classique ne doit pas être supposé transporter le SGT de bout en bout.</text><rect x="110" y="365" width="780" height="45" rx="9" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="500" y="394" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Vérifier point de classification, propagation, frontière et enforcement.</text></svg>

### Exemple : un objet IoT est connecté mais son service ne fonctionne pas

1. Vérifier que le port ou le Wi-Fi est opérationnel et que le terminal a une adresse correcte.
2. Examiner la méthode d’authentification, la classification, le groupe de sécurité ou le profil attribué.
3. Confirmer la VN, la passerelle et la route vers le serveur.
4. Vérifier que le chemin transporte le contexte de politique jusqu’au point d’enforcement attendu.
5. Confirmer le protocole et le port applicatifs ; consulter journaux et compteurs de refus.
6. Tester une source autorisée et une source non autorisée pour prouver que la politique est à la fois fonctionnelle et restrictive.

## 6. Cisco ISE, identité et cycle de vie des terminaux

Dans une architecture intégrée, Cisco ISE fournit les fonctions d’authentification et d’autorisation selon la méthode retenue. 802.1X utilise une identité et une méthode d’authentification définies. MAB, lorsqu’il est autorisé pour des terminaux qui ne supportent pas 802.1X, ne doit pas être considéré comme une identité forte, car une adresse MAC peut être usurpée.

### Concevoir les profils sans supposer une certitude absolue

Le profiling peut aider à estimer le type de terminal à partir de signaux réseau et d’autres attributs. Un profil est une preuve parmi d’autres, pas nécessairement une vérité cryptographique. Les systèmes doivent prévoir le cas où un appareil est inconnu, mal classé ou change de comportement.

### Principes opérationnels

- Définir les résultats d’autorisation attendus, y compris l’accès de remédiation si nécessaire.
- Documenter la relation entre groupes métier, SGT et politiques effectives.
- Gérer les certificats, les secrets, les droits d’administration et les intégrations AAA avec des pratiques de sécurité adaptées.
- Tester l’expiration, le renouvellement et le changement de méthode d’authentification.
- Prévoir des exceptions limitées pour les équipements hérités, avec un propriétaire et une revue périodique.
- Vérifier que les journaux ISE peuvent être corrélés à l’heure et aux identifiants utilisés par les outils d’assurance.

### Diagramme 6 — De l’identité à la politique effective

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="450" viewBox="0 0 1000 450"><rect x="1" y="1" width="998" height="448" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Interconnexion de fabric : transit IP et SD-Access</text><rect x="30" y="80" width="450" height="350" rx="16" fill="#111D30" stroke="#3E536F" stroke-width="2" /><rect x="520" y="80" width="450" height="350" rx="16" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="255" y="116" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="600" fill="#68AEFF" text-anchor="middle">IP-BASED TRANSIT</text><text x="745" y="116" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="600" fill="#36D6B0" text-anchor="middle">SD-ACCESS TRANSIT</text><rect x="65" y="145" width="135" height="60" rx="10" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="132" y="169" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Site A</text><text x="132" y="189" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Border</text><rect x="310" y="145" width="135" height="60" rx="10" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="377" y="169" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Site B</text><text x="377" y="189" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Border</text><line x1="200" y1="175" x2="299.0" y2="175.0" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="310,175 299.0,180.72 299.0,169.28" fill="#68AEFF" /><text x="255" y="233" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">VXLAN terminé au border</text><text x="255" y="258" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">Routage IP traditionnel entre sites</text><text x="255" y="292" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#FFBD69" text-anchor="middle">VRF/SGT à mapper selon design</text><rect x="555" y="145" width="135" height="60" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="622" y="169" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Site A</text><text x="622" y="189" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Border</text><rect x="800" y="145" width="135" height="60" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="867" y="169" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Site B</text><text x="867" y="189" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Border</text><line x1="690" y1="175" x2="789.0" y2="175.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="800,175 789.0,180.72 789.0,169.28" fill="#36D6B0" /><text x="745" y="233" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">VXLAN entre sites</text><text x="745" y="258" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">Conserve les VN/SGT pris en charge</text><text x="745" y="292" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#FFBD69" text-anchor="middle">Contrôle de transit dédié</text><text x="255" y="352" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="middle">Réutilise l’infrastructure IP existante</text><text x="745" y="352" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="middle">Natif fabric, exigences spécifiques</text><text x="500" y="402" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Choisir selon politique, MTU, portée des tags, échelle et support officiel.</text></svg>

## 7. Border nodes et connectivité externe

Le border node connecte la fabric aux réseaux externes. La conception varie selon que la destination est un réseau de centre de données, Internet, un WAN, un campus classique, une infrastructure partenaire ou un autre site fabric. Il est essentiel de séparer la décision de routage et la décision de sécurité : une route présente n’implique pas que le flux soit autorisé, et une politique autorisante ne crée pas une route absente.

### Choisir un modèle de handoff

Évaluer au moins : les VN à exporter, les préfixes autorisés, le protocole de routage ou la méthode statique retenue, l’instance VRF côté peer, les SGT préservés ou non, la redondance, le MTU, les règles firewall, l’asymétrie potentielle et le support de la combinaison matériel/logiciel.

Éviter d’annoncer des préfixes trop larges ou d’importer des routes externes non filtrées. Pour chaque VN, indiquer les routes apprises, les routes annoncées, les routes exclues, les préférences de chemin, les mécanismes de détection de panne et le comportement en cas de perte d’un border.

### Diagramme 7 — Border et réseaux extérieurs

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="450" viewBox="0 0 1000 450"><rect x="1" y="1" width="998" height="448" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Mobilité endpoint : maintien de la passerelle, mise à jour du mapping</text><rect x="35" y="85" width="190" height="88" rx="12" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="130" y="115" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Endpoint</text><text x="130" y="136" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">10.20.30.40</text><rect x="305" y="75" width="190" height="105" rx="12" fill="#1D3553" stroke="#68AEFF" stroke-width="3" /><text x="400" y="105" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Edge A</text><text x="400" y="126" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Anycast gateway</text><rect x="305" y="270" width="190" height="105" rx="12" fill="#1D3553" stroke="#68AEFF" stroke-width="3" /><text x="400" y="300" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Edge B</text><text x="400" y="321" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Même GW logique</text><rect x="650" y="155" width="290" height="120" rx="12" fill="#182941" stroke="#C4A1FF" stroke-width="3" /><text x="795" y="187" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">Control plane</text><text x="795" y="209" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="500" fill="#F4F7FB" text-anchor="middle">mapping actualisé</text><line x1="225" y1="125" x2="294.0" y2="125.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="305,125 294.0,130.72 294.0,119.28" fill="#36D6B0" /><line x1="225" y1="145" x2="300.4266426370543" y2="309.9957807685562" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="305,320 295.22444863670347,312.37392659728795 305.6288366374051,307.6176349398244" fill="#36D6B0" /><line x1="495" y1="125" x2="639.741750918985" y2="181.02906487186516" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="650,185 637.6768646523549,186.36335439399295 641.806637185615,175.69477534973737" fill="#68AEFF" /><line x1="495" y1="320" x2="640.0982482344293" y2="249.79117020914708" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="650,245 642.5896567431859,254.94008112724381 637.6068397256728,244.64225929105035" fill="#68AEFF" /><text x="500" y="220" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#FFBD69" text-anchor="middle">Déplacement</text><line x1="400" y1="180" x2="400.0" y2="259.0" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="400,270 394.28,259.0 405.72,259.0" fill="#FFBD69" /><text x="500" y="412" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#C1CCDA" text-anchor="middle">Adresse/gateway cohérentes ne signifient pas que toute session applicative sera sans interruption.</text></svg>

### Test de bout en bout

Pour chaque destination importante, tester depuis une source représentative dans chaque VN. Examiner route aller, résolution DNS, règles firewall, NAT le cas échéant, route retour et politiques d’identité. Inclure le cas où un chemin primaire est absent. Une topologie redondante ne garantit pas un comportement correct si le chemin retour reste attaché à l’équipement défaillant.

## 8. Transit entre sites : IP-based et SD-Access transit

Ces deux modes ne sont pas interchangeables. Avec un **IP-based transit**, l’encapsulation fabric est terminée au border et les paquets sont routés entre les sites selon les mécanismes IP du réseau de transit. Il faut concevoir la correspondance des VRF et vérifier ce qui arrive aux SGT au niveau de la frontière. Avec un **SD-Access transit**, la fabric peut étendre l’encapsulation VXLAN entre sites et préserver les VN/SGT pris en charge dans le design. Ce mode nécessite le contrôle de transit prévu et des exigences spécifiques de reachability et de MTU.

### Critères de décision

| Critère | IP-based transit | SD-Access transit |
|---|---|---|
| Réutilisation d’un WAN IP existant | Souvent adaptée | Dépend de l’architecture choisie |
| Encapsulation de fabric entre sites | Terminée à la frontière | Préservée entre les frontières prises en charge |
| Continuité des constructs VN/SGT | À concevoir / mapper | Peut être conservée nativement dans le design pris en charge |
| Dépendances | Routage, VRF handoff, politique des peers | Contrôle de transit, reachability, MTU et support spécifiques |
| Choix final | Selon besoins, fonctions et compatibilité | Selon besoins, fonctions et compatibilité |

Ne pas interpréter ce tableau comme une déclaration que toutes les politiques fonctionnent automatiquement à travers n’importe quel WAN. Les modes disponibles, le rôle des transit control plane nodes, la capacité et les recommandations varient selon l’architecture et la version. Vérifier les guides officiels applicables.

### Diagramme 8 — Comparer les modèles de transit

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="425" viewBox="0 0 1000 425"><rect x="1" y="1" width="998" height="423" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Fabric wireless : radio, contrôle et politique</text><rect x="30" y="105" width="170" height="88" rx="12" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="115" y="135" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Client Wi-Fi</text><text x="115" y="156" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">identité</text><rect x="250" y="105" width="170" height="88" rx="12" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="335" y="135" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Fabric-mode AP</text><text x="335" y="156" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">accès radio</text><rect x="470" y="105" width="170" height="88" rx="12" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="555" y="135" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">WLC fabric</text><text x="555" y="156" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">contrôle WLAN</text><rect x="690" y="105" width="130" height="88" rx="12" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="755" y="135" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">Edge node</text><text x="755" y="156" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="500" fill="#F4F7FB" text-anchor="middle">fabric</text><rect x="860" y="105" width="110" height="88" rx="12" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="915" y="135" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">VN / policy</text><text x="915" y="155" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">services</text><line x1="200" y1="149" x2="239.0" y2="149.0" stroke="#36D6B0" stroke-width="3" stroke-linecap="round" /><polygon points="250,149 239.0,154.72 239.0,143.28" fill="#36D6B0" /><line x1="420" y1="149" x2="459.0" y2="149.0" stroke="#68AEFF" stroke-width="3" stroke-linecap="round" /><polygon points="470,149 459.0,154.72 459.0,143.28" fill="#68AEFF" /><line x1="640" y1="149" x2="679.0" y2="149.0" stroke="#C4A1FF" stroke-width="3" stroke-linecap="round" /><polygon points="690,149 679.0,154.72 679.0,143.28" fill="#C4A1FF" /><line x1="820" y1="149" x2="849.0" y2="149.0" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="860,149 849.0,154.72 849.0,143.28" fill="#FFBD69" /><rect x="120" y="255" width="760" height="92" rx="14" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="500" y="286" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="600" fill="#F4F7FB" text-anchor="middle">À valider dans la conception</text><text x="500" y="314" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Mode WLAN, tunnelisation, mobilité, MTU, redondance WLC, AAA/ISE et couverture RF.</text><line x1="755" y1="193" x2="755.0" y2="244.0" stroke="#FFBD69" stroke-width="3" stroke-linecap="round" /><polygon points="755,255 749.28,244.0 760.72,244.0" fill="#FFBD69" /><text x="500" y="391" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#FFBD69" text-anchor="middle">Le chemin réel des données varie selon le mode et la version déployés.</text></svg>

## 9. Fabric wireless et cohérence de la mobilité

L’intégration sans fil doit considérer les AP, WLC, underlay, nœuds fabric, l’identité et les politiques. La simple présence d’un SSID ne décrit ni le chemin de données ni le comportement de mobilité. Le mode WLAN, la version, les options prises en charge et le design déterminent comment les clients sont associés à la fabric et où le trafic est encapsulé ou traité.

### Conception à vérifier

- Le mapping SSID / profil d’accès / VLAN ou VN est clair et contrôlé.
- L’authentification, l’autorisation ISE et l’affectation des politiques sont testées pour différents profils de terminal.
- Le MTU est suffisant sur le chemin réellement utilisé, y compris les tunnels sans fil et la fabric, selon la solution déployée.
- Les contrôleurs WLAN et leurs chemins de redondance ont des domaines de panne compris.
- Les limites RF — couverture, interférences, canaux, capacité — sont suivies séparément de la santé IP.
- La mobilité entre AP/edge a un test reproductible, avec durée de coupure et sessions applicatives mesurées.

### Diagramme 9 — Parcours du client sans fil

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="430" viewBox="0 0 1000 430"><rect x="1" y="1" width="998" height="428" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Migration vers SD-Access : portes de validation</text><circle cx="66" cy="154" r="25" fill="#182941" stroke="#C4A1FF" stroke-width="3" /><text x="66" y="161" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="600" fill="#F4F7FB" text-anchor="middle">1</text><rect x="24" y="198" width="120" height="99" rx="10" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="84" y="224" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="middle">Découverte</text><text x="84" y="250" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">Inventaire</text><text x="84" y="266" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">compatibilité</text><line x1="144" y1="248" x2="154.0" y2="248.0" stroke="#F4F7FB" stroke-width="2" stroke-linecap="round" /><polygon points="162,248 154.0,252.16 154.0,243.84" fill="#F4F7FB" /><circle cx="204" cy="154" r="25" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="204" y="161" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="600" fill="#F4F7FB" text-anchor="middle">2</text><rect x="162" y="198" width="120" height="99" rx="10" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="222" y="224" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="middle">Préparation</text><text x="222" y="250" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">IP</text><text x="222" y="266" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">DNS</text><text x="222" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">NTP</text><text x="222" y="298" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">AAA</text><line x1="282" y1="248" x2="292.0" y2="248.0" stroke="#F4F7FB" stroke-width="2" stroke-linecap="round" /><polygon points="300,248 292.0,252.16 292.0,243.84" fill="#F4F7FB" /><circle cx="342" cy="154" r="25" fill="#182941" stroke="#36D6B0" stroke-width="3" /><text x="342" y="161" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="600" fill="#F4F7FB" text-anchor="middle">3</text><rect x="300" y="198" width="120" height="99" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="360" y="224" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="middle">Underlay</text><text x="360" y="250" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">Routage</text><text x="360" y="266" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">MTU</text><text x="360" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">redondance</text><line x1="420" y1="248" x2="430.0" y2="248.0" stroke="#F4F7FB" stroke-width="2" stroke-linecap="round" /><polygon points="438,248 430.0,252.16 430.0,243.84" fill="#F4F7FB" /><circle cx="480" cy="154" r="25" fill="#182941" stroke="#FFBD69" stroke-width="3" /><text x="480" y="161" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="600" fill="#F4F7FB" text-anchor="middle">4</text><rect x="438" y="198" width="120" height="99" rx="10" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="498" y="224" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="middle">Fabric</text><text x="498" y="250" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">Rôles</text><text x="498" y="266" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">VN</text><text x="498" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">pools</text><line x1="558" y1="248" x2="568.0" y2="248.0" stroke="#F4F7FB" stroke-width="2" stroke-linecap="round" /><polygon points="576,248 568.0,252.16 568.0,243.84" fill="#F4F7FB" /><circle cx="618" cy="154" r="25" fill="#182941" stroke="#FF7788" stroke-width="3" /><text x="618" y="161" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="600" fill="#F4F7FB" text-anchor="middle">5</text><rect x="576" y="198" width="120" height="99" rx="10" fill="#182941" stroke="#FF7788" stroke-width="2" /><text x="636" y="224" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="middle">Politique</text><text x="636" y="250" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">ISE</text><text x="636" y="266" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">SGT</text><text x="636" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">tests</text><line x1="696" y1="248" x2="706.0" y2="248.0" stroke="#F4F7FB" stroke-width="2" stroke-linecap="round" /><polygon points="714,248 706.0,252.16 706.0,243.84" fill="#F4F7FB" /><circle cx="756" cy="154" r="25" fill="#182941" stroke="#68AEFF" stroke-width="3" /><text x="756" y="161" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="600" fill="#F4F7FB" text-anchor="middle">6</text><rect x="714" y="198" width="120" height="99" rx="10" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="774" y="224" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="middle">Migration</text><text x="774" y="250" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">Pilote</text><text x="774" y="266" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">rollback</text><line x1="834" y1="248" x2="844.0" y2="248.0" stroke="#F4F7FB" stroke-width="2" stroke-linecap="round" /><polygon points="852,248 844.0,252.16 844.0,243.84" fill="#F4F7FB" /><circle cx="894" cy="154" r="25" fill="#182941" stroke="#36D6B0" stroke-width="3" /><text x="894" y="161" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="600" fill="#F4F7FB" text-anchor="middle">7</text><rect x="852" y="198" width="120" height="99" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="912" y="224" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="middle">Assurance</text><text x="912" y="250" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">SLA</text><text x="912" y="266" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">preuves</text><text x="912" y="282" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="500" fill="#C1CCDA" text-anchor="middle">runbook</text><text x="500" y="360" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="600" fill="#FFBD69" text-anchor="middle">Passage à l’étape suivante seulement après preuve de validation</text><text x="500" y="395" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Prévoir une étape de retour arrière testée avant chaque bascule majeure.</text></svg>

## 10. Haute disponibilité, convergence et domaines de panne

Il faut séparer disponibilité du plan de données, disponibilité du control plane, gestion/orchestration et disponibilité des services d’identité. Une panne de Catalyst Center ne signifie pas nécessairement que chaque paquet déjà provisionné cesse immédiatement de circuler ; inversement, le fait que le forwarding continue ne garantit pas la possibilité de faire des changements, d’apprendre de nouveaux terminaux ou de voir les événements attendus. Les effets exacts doivent être vérifiés dans le design et avec des tests.

### Construire un registre de panne

Pour chaque composant, noter : scénario, service touché, détection, convergence attendue, observabilité, actions opérateur, méthode de retour arrière et résultat mesuré. Inclure les pannes communes : un seul chemin d’énergie ou de fibre, un seul service DNS/NTP, un seul lien vers le pare-feu, une intégration ISE non redondante ou une version logicielle commune à toute la fabric.

### Convergence mesurable

Mesurer la perte de paquets, la durée d’interruption applicative, la durée de reconstruction des adjacences, le retour des mappings et la stabilité après convergence. Le temps annoncé par une fonction de protocole n’est pas équivalent au temps de rétablissement d’une transaction applicative. Toujours horodater les tests et les corréler avec la topologie réellement utilisée.

## 11. Capacité, échelle et croissance

Les limites doivent être évaluées avec la documentation officielle correspondant à la version et au modèle. Le nombre d’endpoints, de VN, de SGT, de règles, de routes, de flux, de voisins externes, d’AP et d’événements de mobilité peut affecter différentes ressources. Ne dimensionne pas la solution sur une seule métrique moyenne : prévoir les pics, la croissance, les événements de panne et les changements de configuration.

### Les dimensions à inventorier

- Endpoints moyens et maximums par site, edge et VN.
- Nombre de VN et de pools ; taille des sous-réseaux et taux de consommation.
- Nombre de groupes et complexité de la matrice de politiques.
- Nombre de préfixes externes, VRF peers et chemins de routage.
- Débit par lien, trafic est-ouest, trafic nord-sud, multicast le cas échéant et surcoût d’encapsulation.
- Nombre d’AP, densité de clients, modèles de mobilité et trafic de pointe.
- Volume des logs, rétention, assurance et capacité des systèmes de gestion.

### Diagramme 10 — Modèle d’échelle et capacité

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="435" viewBox="0 0 1000 435"><rect x="1" y="1" width="998" height="433" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Dépannage SD-Access : vérifier de bas en haut</text><rect x="115" y="75" width="770" height="39" rx="9" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="145" y="100" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#36D6B0" text-anchor="middle">1</text><text x="185" y="100" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#F4F7FB" text-anchor="start">Terminal et accès</text><text x="860" y="100" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="500" fill="#C1CCDA" text-anchor="end">Port / AP / VLAN de transport</text><line x1="500" y1="114" x2="500" y2="125" stroke="#52708F" stroke-width="2" stroke-linecap="round" /><rect x="115" y="126" width="770" height="39" rx="9" fill="#182941" stroke="#C4A1FF" stroke-width="2" /><text x="145" y="151" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#C4A1FF" text-anchor="middle">2</text><text x="185" y="151" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#F4F7FB" text-anchor="start">Identité et politique</text><text x="860" y="151" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="500" fill="#C1CCDA" text-anchor="end">802.1X / ISE / VN / SGT</text><line x1="500" y1="165" x2="500" y2="176" stroke="#52708F" stroke-width="2" stroke-linecap="round" /><rect x="115" y="177" width="770" height="39" rx="9" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="145" y="202" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#68AEFF" text-anchor="middle">3</text><text x="185" y="202" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#F4F7FB" text-anchor="start">Underlay</text><text x="860" y="202" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="500" fill="#C1CCDA" text-anchor="end">Routes RLOC / perte / MTU</text><line x1="500" y1="216" x2="500" y2="227" stroke="#52708F" stroke-width="2" stroke-linecap="round" /><rect x="115" y="228" width="770" height="39" rx="9" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="145" y="253" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#FFBD69" text-anchor="middle">4</text><text x="185" y="253" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#F4F7FB" text-anchor="start">Control plane</text><text x="860" y="253" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="500" fill="#C1CCDA" text-anchor="end">Registration / mapping LISP</text><line x1="500" y1="267" x2="500" y2="278" stroke="#52708F" stroke-width="2" stroke-linecap="round" /><rect x="115" y="279" width="770" height="39" rx="9" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="145" y="304" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#36D6B0" text-anchor="middle">5</text><text x="185" y="304" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#F4F7FB" text-anchor="start">Data plane</text><text x="860" y="304" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="500" fill="#C1CCDA" text-anchor="end">VXLAN / passerelle / compteurs</text><line x1="500" y1="318" x2="500" y2="329" stroke="#52708F" stroke-width="2" stroke-linecap="round" /><rect x="115" y="330" width="770" height="39" rx="9" fill="#182941" stroke="#FF7788" stroke-width="2" /><text x="145" y="355" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#FF7788" text-anchor="middle">6</text><text x="185" y="355" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#F4F7FB" text-anchor="start">Sortie externe</text><text x="860" y="355" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="500" fill="#C1CCDA" text-anchor="end">Border / VRF handoff / firewall</text><text x="500" y="407" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#FFBD69" text-anchor="middle">Comparer le même terminal, la même destination, le même horaire et le même sens de trafic.</text></svg>

### Marge de capacité

Il n’existe pas de pourcentage universel valide pour chaque déploiement. Définis une marge par ressource en fonction de la croissance, du comportement à la panne, des mesures de pointe et des recommandations du constructeur. Le mode dégradé compte : après la perte d’un lien, l’équipement survivant peut devoir transporter plus de trafic et de tables. Teste ce cas plutôt que de regarder seulement les moyennes en situation normale.

## 12. Supervision, assurance et observabilité

Une architecture pilotée par l’intention nécessite une vérification de l’intention et du résultat. Les tableaux de bord sont utiles, mais doivent être associés à des indicateurs métier et aux preuves du plan de données. Un statut vert ne prouve pas que tous les flux sont autorisés, que toutes les applications sont disponibles ou que le chemin retour est sain.

### Modèle d’observabilité en couches

1. **Expérience utilisateur :** disponibilité applicative, temps de réponse, pertes et plaintes reproductibles.
2. **Endpoint :** identité, adresse, VN, SGT, AP/port et historique de mobilité.
3. **Fabric :** état edge/border/control plane, mappings, tunnels, compteurs et événements.
4. **Underlay :** adjacences, tables de routage, ECMP, MTU, erreurs et pertes de liens.
5. **Services :** ISE, DHCP, DNS, NTP, pare-feu, WLC, WAN et applications.
6. **Gestion :** provisioning, état d’inventaire, tâches en échec, sauvegardes, changements et assurance.

### Diagramme 11 — Corrélation d’un incident

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="430" viewBox="0 0 1000 430"><rect x="1" y="1" width="998" height="428" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Modèles de site : capacité, disponibilité et domaines de panne</text><rect x="32" y="90" width="285" height="270" rx="14" fill="#111D30" stroke="#3E536F" stroke-width="2" /><rect x="357" y="90" width="285" height="270" rx="14" fill="#111D30" stroke="#3E536F" stroke-width="2" /><rect x="682" y="90" width="285" height="270" rx="14" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="174" y="124" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="600" fill="#36D6B0" text-anchor="middle">PETIT SITE</text><text x="499" y="124" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="600" fill="#68AEFF" text-anchor="middle">SITE MOYEN</text><text x="824" y="124" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="600" fill="#FFBD69" text-anchor="middle">GRAND SITE</text><rect x="74" y="154" width="200" height="56" rx="10" fill="#182941" stroke="#36D6B0" stroke-width="2" /><text x="174" y="177" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Fabric in a Box</text><text x="174" y="197" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">si supporté</text><rect x="399" y="154" width="200" height="56" rx="10" fill="#182941" stroke="#68AEFF" stroke-width="2" /><text x="499" y="177" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Rôles répartis</text><text x="499" y="197" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">redondance</text><rect x="724" y="154" width="200" height="56" rx="10" fill="#182941" stroke="#FFBD69" stroke-width="2" /><text x="824" y="177" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">Domaines / zones</text><text x="824" y="197" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="500" fill="#F4F7FB" text-anchor="middle">design modulaire</text><text x="174" y="250" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Simplicité avant tout</text><text x="499" y="250" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Disponibilité ciblée</text><text x="824" y="250" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#C1CCDA" text-anchor="middle">Échelle et blast radius</text><text x="174" y="292" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="middle">Peu de rôles, mais</text><text x="174" y="315" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="middle">dépendances communes</text><text x="499" y="292" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="middle">Séparer les points</text><text x="499" y="315" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="middle">de défaillance critiques</text><text x="824" y="292" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="middle">Capacité, domaines,</text><text x="824" y="315" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="600" fill="#F4F7FB" text-anchor="middle">limites vérifiées</text><text x="500" y="400" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#FFBD69" text-anchor="middle">Aucun nombre universel : dimensionner avec les limites officielles et la croissance attendue.</text></svg>

### Construire une preuve exploitable

Un dossier d’incident doit fournir le site, l’équipement, l’heure et le fuseau, le terminal, l’adresse IP, la VN/SGT, la source et la destination, le protocole, le résultat attendu, le résultat observé, les tests positifs/négatifs et les traces pertinentes. Éviter les captures isolées sans contexte : une capture sans horodatage, interface ou sens de flux peut induire en erreur.

## 13. Migration depuis une LAN traditionnelle

La migration est souvent le risque principal, plus que la technologie de fabric elle-même. Il faut documenter ce que le réseau existant fait réellement, pas seulement ce que les diagrammes anciens prétendent. Inventorier les VLAN, sous-réseaux, trunks, listes de contrôle, routage, dépendances L2, DHCP relay, multicast, équipements hérités, imprimantes, systèmes de contrôle et flux peu fréquents.

### Phases de migration

1. **Découverte :** collecter la configuration, les flux, les chemins et les exceptions réellement utilisées.
2. **Conception :** décider VN, SGT, services partagés, transit, adressage et frontières ; obtenir validation sécurité et applicative.
3. **Préparation :** vérifier compatibilité, souscriptions/licences, logiciel, services d’infrastructure et accès de gestion hors bande si disponible.
4. **Pilote :** migrer un groupe limité avec des cas d’usage et critères de réussite précis.
5. **Vagues :** migrer par population ou zone, avec période d’observation et décision de continuer/stopper.
6. **Stabilisation :** supprimer les exceptions temporaires et documenter l’état final.

### Plan de rollback

Définir l’événement déclencheur, l’autorité de décision, la séquence exacte de retour, les modifications à annuler, les dépendances à restaurer, le temps maximum autorisé et la preuve que les services sont revenus. Une procédure qui n’a jamais été exécutée ou répétée dans un environnement test n’est pas un rollback éprouvé.

### Diagramme 12 — Migration par portes de validation

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="445" viewBox="0 0 1000 445"><rect x="1" y="1" width="998" height="443" rx="20" fill="#0B1220" stroke="#31445F" stroke-width="2" /><text x="500" y="42" font-family="Arial,Helvetica,sans-serif" font-size="25" font-weight="700" fill="#F4F7FB" text-anchor="middle">Revue d’architecture : décision, question et preuve</text><rect x="45" y="90" width="910" height="285" rx="14" fill="#111D30" stroke="#3E536F" stroke-width="2" /><text x="75" y="126" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#36D6B0" text-anchor="start">Décision</text><text x="300" y="126" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#36D6B0" text-anchor="start">Question de conception</text><text x="695" y="126" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#36D6B0" text-anchor="start">Preuve attendue</text><line x1="65" y1="147" x2="935" y2="147" stroke="#344A67" stroke-width="1" stroke-linecap="round" /><text x="75" y="165" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="start">Underlay</text><text x="300" y="165" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">Les RLOC sont-ils joignables sans route implicite ?</text><text x="695" y="165" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="start">Tests de reachability / tables</text><line x1="65" y1="186" x2="935" y2="186" stroke="#344A67" stroke-width="1" stroke-linecap="round" /><text x="75" y="204" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="start">Segmentation</text><text x="300" y="204" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">VN et SGT reflètent-ils les besoins métier ?</text><text x="695" y="204" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="start">Matrice autoriser/refuser</text><line x1="65" y1="225" x2="935" y2="225" stroke="#344A67" stroke-width="1" stroke-linecap="round" /><text x="75" y="243" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="start">Transit</text><text x="300" y="243" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">Les tags et le MTU traversent-ils le chemin ?</text><text x="695" y="243" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="start">Design + tests de bout en bout</text><line x1="65" y1="264" x2="935" y2="264" stroke="#344A67" stroke-width="1" stroke-linecap="round" /><text x="75" y="282" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="start">Résilience</text><text x="300" y="282" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">Quelle est la panne maximale acceptable ?</text><text x="695" y="282" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="start">Tests failover horodatés</text><line x1="65" y1="303" x2="935" y2="303" stroke="#344A67" stroke-width="1" stroke-linecap="round" /><text x="75" y="321" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="600" fill="#F4F7FB" text-anchor="start">Migration</text><text x="300" y="321" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#F4F7FB" text-anchor="start">Le rollback est-il testable ?</text><text x="695" y="321" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="500" fill="#C1CCDA" text-anchor="start">Runbook validé et approuvé</text><text x="500" y="414" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="600" fill="#FFBD69" text-anchor="middle">Une architecture est prête quand les risques ont une preuve et un propriétaire.</text></svg>

## 14. Sécurité de la plateforme et gouvernance

La sécurité inclut les équipements, les comptes administrateurs, les API, les certificats, les systèmes de gestion et les intégrations avec ISE. Les privilèges doivent être minimaux, les secrets gérés de manière contrôlée, les interfaces de gestion séparées autant que possible et les changements traçables. Les sauvegardes doivent être protégées et leur restauration testée.

### Contrôles recommandés

- Utiliser des comptes individuels et des rôles d’administration adaptés ; limiter les comptes partagés.
- Mettre en œuvre MFA et gestion des secrets lorsqu’ils sont supportés par la plateforme et l’environnement.
- Segmenter l’accès aux interfaces de gestion et restreindre les API aux consommateurs légitimes.
- Vérifier certificats, expiration, intégration AAA, NTP et journalisation.
- Enregistrer les changements d’intention et les changements manuels effectués en dehors de l’orchestration.
- Contrôler les versions et les avis de sécurité avant toute mise à niveau.
- Examiner régulièrement les exceptions de sécurité et les règles temporaires.

## 15. Automatisation et gestion des changements

L’automatisation doit être traitée comme du logiciel : versionner les modèles, relire les changements, tester les entrées, vérifier les résultats et prévoir le retour arrière. Une API disponible ne signifie pas qu’une opération donnée est supportée dans toutes les versions, ni qu’un script ancien restera compatible avec une mise à jour.

### Pipeline de changement recommandé

- Pré-vérifications : inventaire, état de santé, version, sauvegarde et portée du changement.
- Validation : schéma et entrées, impact sur VN/SGT, routes et accès externes.
- Déploiement : changement par petits lots avec points d’arrêt.
- Vérification : comparer l’intention, l’état de configuration et les tests actifs.
- Journalisation : conserver identifiant du changement, propriétaire, heure, résultats et exceptions.
- Retour arrière : exécuter la procédure prévalidée si les critères échouent.

Ne pas conserver de secrets en clair dans des scripts, exports ou fichiers de cours. Toute donnée réelle d’infrastructure doit être anonymisée avant d’être partagée.

## 16. Laboratoire de conception intermédiaire

### Scénario

Une entreprise dispose d’un campus principal, d’un petit site régional et d’un centre de données. Elle souhaite isoler les invités, les appareils de bâtiment, les employés et l’administration. Elle doit conserver certains services partagés et étudier l’interconnexion entre fabric et environnement classique.

### Travail à réaliser

1. Dessiner l’underlay et préciser les préfixes des liens et les loopbacks de laboratoire.
2. Choisir le modèle de site et justifier le placement de edge, control plane et border.
3. Concevoir au moins trois VN et associer à chacune une plage d’adressage non utilisée dans le laboratoire.
4. Définir les groupes SGT et une matrice de politique explicitant flux autorisés et refusés.
5. Décrire le raccordement aux services partagés et au pare-feu ; tracer le chemin aller/retour.
6. Comparer IP-based transit et SD-Access transit à partir des besoins de continuité des politiques, de MTU, de routage et de compatibilité.
7. Proposer un plan de redondance et cinq scénarios de panne.
8. Définir les métriques de capacité et les preuves de surveillance.
9. Rédiger un plan de migration avec seuils d’arrêt et rollback.

### Exemple de matrice de flux

| Source | Destination | Service | Décision attendue | Point de contrôle |
|---|---|---|---|---|
| Employé | Application métier | TCP/443 | Autorisé selon politique | SGT/politique et pare-feu |
| IoT | Collecteur IoT | Port documenté | Autorisé | Politique + serveur |
| IoT | Poste utilisateur | Tout sauf exception explicite | Refusé | Logs d’enforcement |
| Invité | Réseau interne | Tout | Refusé | VN/ACL/firewall selon design |
| IT admin | Switch géré | SSH/HTTPS selon besoin | Autorisé depuis bastion | AAA/logs |
| Utilisateur | DNS/DHCP | Protocoles nécessaires | Autorisé | Services partagés |

Cette matrice est illustrative : remplacer chaque ligne par un besoin applicatif confirmé, pas par une supposition.

## 17. Études de cas

### Cas A — L’endpoint a une IP, mais ne joint pas son application

**Hypothèses possibles :** mauvais profil d’identité, mauvais SGT, route absente, politique de segmentation, service DNS, pare-feu, MTU ou route retour. Le fait d’obtenir DHCP ne prouve pas que le chemin de données complet fonctionne.

**Démarche :** enregistrer l’heure et les identifiants ; vérifier identité et VN ; tester le DNS ; confirmer la route de la source et du retour ; examiner les compteurs et logs au point d’enforcement ; tester le même service depuis une source autorisée connue. Ne change pas simultanément plusieurs politiques, car la cause deviendrait difficile à isoler.

### Cas B — Les grands paquets échouent de façon intermittente

**Hypothèses possibles :** MTU de chemin, encapsulation supplémentaire, tunnel ou chemin WAN dont la capacité diffère. Comparer petits paquets et paquets de tailles progressives avec méthode adaptée à l’OS et au chemin ; vérifier le PMTUD, les compteurs d’interface et les limites de service intermédiaire. Valider le MTU bout en bout, pas uniquement sur un port d’accès.

### Cas C — Le changement d’un border perturbe une application

**Hypothèses possibles :** asymétrie, routes externes différentes, état firewall, chemin retour resté sur le border secondaire, ou politique non équivalente. Vérifier RIB/FIB, annonces et retraits de routes, état du peer, sessions applicatives et politique de sécurité. Exécuter les tests lors d’une fenêtre contrôlée.

### Cas D — Les invités peuvent atteindre une ressource interne

**Hypothèses possibles :** mauvaise VN/pool, exception de route, règle trop large, erreur de classification ou politique d’enforcement absente au point prévu. Reproduire depuis un invité de test ; confirmer la VN et le groupe ; tracer le chemin réel ; examiner les règles et leur ordre d’application ; ajouter des tests négatifs après correction.

### Cas E — Un statut de supervision reste vert malgré une panne applicative

**Hypothèses possibles :** le test synthétique ne couvre pas la transaction réelle, il passe par un autre chemin, ou le problème est au niveau DNS/TLS/serveur. Créer une sonde correspondant au service et au contexte utilisateur ; associer les résultats aux changements et à la télémétrie ; ne pas assimiler la santé du switch à la santé de l’application.

## 18. Quiz de validation

Réponds avant de consulter le corrigé.

1. Pourquoi concevoir les flux et les objectifs avant de choisir les rôles ?
2. Quels risques la colocalisation des rôles peut-elle introduire ?
3. Pourquoi une route RLOC absente rend-elle l’analyse overlay moins utile ?
4. Quelle différence existe entre la macro-segmentation VN/VRF et la micro-segmentation SGT ?
5. Quelles étapes de politique faut-il vérifier pour diagnostiquer une règle SGT ?
6. Pourquoi ne pas supposer que les SGT traversent un handoff IP classique ?
7. Quelle différence essentielle distingue IP-based transit et SD-Access transit ?
8. Pourquoi un test de MTU local ne suffit-il pas ?
9. Comment mesurer la convergence applicative après perte d’un lien ?
10. Pourquoi MAB n’offre-t-il pas la même garantie d’identité qu’un échange cryptographique robuste ?
11. Quelles preuves conserver pour une investigation reproductible ?
12. Pourquoi un rollback doit-il être testé et posséder un déclencheur explicite ?
13. Quelles métriques doivent compléter le nombre d’endpoints lors du dimensionnement ?
14. Pourquoi ne faut-il pas interpréter un tableau de bord vert comme une preuve complète de santé métier ?
15. Quel document officiel faut-il consulter avant de valider matériel, version et fonctions ?

### Corrigé

1. Les choix de rôles, l’échelle, les frontières, la politique et les tests découlent des besoins et des domaines de panne.
2. Charge et impact partagés, capacité réduite, maintenance plus risquée et domaine de panne plus large ; la colocalisation peut néanmoins être appropriée dans des sites compatibles de petite taille.
3. La fabric dépend de l’underlay pour joindre les localisateurs ; un mapping ne répare pas un transport IP absent.
4. VN/VRF sépare des contextes de routage ; SGT identifie un groupe utilisé par les politiques d’accès.
5. Classification, propagation du tag et enforcement effectif, plus l’identité et les logs.
6. Le handoff peut terminer l’encapsulation et ne transporte pas automatiquement toutes les constructions de politique de la fabric.
7. IP-based termine le tunnel fabric au border et route selon le réseau IP ; SD-Access transit peut prolonger VXLAN et préserver les VN/SGT pris en charge, avec dépendances spécifiques.
8. Le minimum de MTU du chemin complet et les encapsulations intermédiaires déterminent la taille réellement transportable.
9. Horodater la perte, la détection, la reprise de routes, la stabilité et le rétablissement de transactions représentatives.
10. MAB se fonde couramment sur la MAC, qui peut être usurpée ; elle ne prouve pas la possession d’une identité cryptographique de la même manière.
11. Topologie, version, source/destination, heure, VN/SGT, tests, routes, journaux, résultats positifs et négatifs.
12. Il doit définir qui décide, quand arrêter et comment revenir à l’état connu si le changement échoue.
13. Débit de pointe, routes, règles, VN/SGT, AP/clients, événements de mobilité, volume de logs et comportement en mode dégradé.
14. Les sondes peuvent couvrir un autre chemin ou un niveau différent de la transaction ; la santé applicative exige des tests pertinents.
15. La matrice de compatibilité Cisco, le design guide et le guide de déploiement correspondant à la version retenue.

## 19. Glossaire intermédiaire

| Terme | Rappel |
|---|---|
| Fabric site | Domaine SD-Access avec les rôles requis par le design |
| Border node | Raccordement à des réseaux externes ou à un transit |
| Control plane node | Maintien et distribution des mappings EID/RLOC selon l’architecture |
| Edge node | Accès des endpoints et fonctions fabric associées |
| VN / VRF | Segmentation logique et table de routage isolée |
| SGT | Étiquette de groupe de sécurité utilisée par les politiques |
| LISP | Mécanisme de mapping identité/localisateur |
| VXLAN | Encapsulation du trafic fabric sur un transport IP |
| IP-based transit | Interconnexion avec terminaison fabric au border et routage IP entre sites |
| SD-Access transit | Interconnexion fabric par overlay VXLAN et plan de contrôle prévu |
| MTU | Taille maximale de paquet supportée sur un chemin au niveau considéré |
| Assurance | Corrélation d’états, événements, mesures et expérience réseau |
| Rollback | Procédure testée de retour à une situation antérieure connue |

## 20. Checklist de revue avant déploiement

- [ ] Besoins métier, flux et contraintes de disponibilité approuvés.
- [ ] Matériel, logiciel, licences, rôles et fonctions validés dans la documentation de compatibilité.
- [ ] Plan IP, RLOC, reachability et routage underlay vérifiés.
- [ ] MTU de bout en bout et chemins alternatifs testés.
- [ ] Modèle de site, colocalisation et domaines de panne justifiés.
- [ ] VN, pools, services partagés et routage inter-VN documentés.
- [ ] Classification, SGT, propagation et enforcement vérifiés par tests positifs et négatifs.
- [ ] Border, transit, annonces et chemins retour testés.
- [ ] Wi-Fi, mobilité et contraintes RF inclus dans le périmètre de test.
- [ ] Supervision, preuves, capacité et mode dégradé documentés.
- [ ] Migration par étapes, rollback et critères d’arrêt approuvés.
- [ ] Comptes, API, certificats, sauvegardes et journaux sécurisés.

## 21. Références officielles

1. **Cisco Design Zone — Software-Defined Access** : https://www.cisco.com/c/en/us/td/docs/solutions/CVD/Campus/cisco-sda-design-guide.html
2. **Cisco SD-Access Deployment Using Catalyst Center** : https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/cisco-validated-solution-profiles/validated-profile-sda-deployment.html
3. **Cisco Catalyst Center Compatibility Matrix** : consulter la section de compatibilité depuis la documentation Cisco correspondant à la version déployée.

### Limites et prudence

Ce cours est un support pédagogique, pas un design certifié, un BOM, un guide officiel de migration ni une procédure de changement de production. Les fonctions disponibles et leurs limites varient selon le matériel, le logiciel, les licences et la topologie. Toujours valider la documentation actuelle, tester dans un environnement approprié et utiliser une procédure de changement et de retour arrière approuvée avant toute modification en production.
