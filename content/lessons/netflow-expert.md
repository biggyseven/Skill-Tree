# IP SLA & NetFlow — Niveau Expert

> **Fichier :** `netflow-expert.md`  
> **Parcours :** Débutant → Intermédiaire → Expert  
> **Niveau visé :** ingénierie réseau, observabilité, exploitation et dépannage à grande échelle  
> **Prérequis :** maîtriser les records, monitors, exporters, cache, templates, IP SLA, sampling et lecture de flux abordés aux niveaux précédents.

## Objectif général

Ce cours traite NetFlow et IP SLA comme une chaîne de mesure de production : du point d’observation sur le routeur jusqu’à la décision opérationnelle. Au niveau expert, l’enjeu n’est plus seulement de « faire apparaître des flux », mais de garantir que les mesures sont interprétables, comparables dans le temps, suffisamment fiables, correctement dimensionnées et utiles pour une décision technique.

À la fin, tu dois pouvoir concevoir une architecture de télémétrie multi-sites, dimensionner l’export et la rétention, réduire les biais de mesure, raisonner sur les templates, corréler les flux aux mesures de qualité, bâtir des détections défendables et conduire une investigation reproductible.

## Ce que ce cours n’affirme pas

NetFlow ne capture pas le contenu complet des paquets. IP SLA ne prouve pas à lui seul que l’application fonctionne. Un échantillon n’est pas le trafic complet. Un export reçu ne signifie pas nécessairement qu’il a été décodé correctement. Enfin, les capacités de Flexible NetFlow, les champs disponibles, les directions supportées, la taille du cache et les commandes varient selon la plateforme, le matériel et la version logicielle. Les exemples Cisco de ce document sont des modèles de raisonnement et de configuration, pas une promesse de compatibilité universelle.


## 1. Architecture experte : séparer les plans de mesure

Une architecture exploitable sépare au minimum cinq étapes :

1. **Observation** : interface, direction, VRF, type de trafic et point exact où les paquets sont vus.
2. **Métrage** : classification, record, cache, compteurs, vieillissement et ressources consommées sur l’équipement.
3. **Export** : version, transport, destination, source, templates et comportement en cas de perte ou de reprise.
4. **Ingestion** : réception, état de session, décodage, validation des champs, horodatage, buffering et gestion des erreurs.
5. **Analyse** : normalisation, enrichissement, stockage, requêtes, tableaux de bord, alertes et réponses à incident.

Un défaut à chaque étage se manifeste différemment. Si l’interface ne voit pas le trafic, le problème est en amont de NetFlow. Si le cache se remplit mais n’exporte rien, il faut étudier les règles de vieillissement et l’exportateur. Si les datagrammes arrivent mais que le collecteur ne produit pas de flux, il faut étudier les templates, la version et le parseur. Si les flux sont décodés mais que les volumes semblent faux, il faut revoir l’observation, la direction, le sampling et la sémantique des champs.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="355" viewBox="0 0 960 355" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-1-title nfexp-1-desc"><title id="nfexp-1-title">Architecture de télémétrie de flux à l’échelle</title><desc id="nfexp-1-desc">Du point d’observation à l’analyse, distinguer mesure, export, ingestion, décodage et stockage.</desc><rect x="1" y="1" width="958" height="353" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">Architecture de télémétrie de flux à l’échelle</text><rect x="30" y="82" width="165" height="112" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="112.5" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Points d’observation</text><text x="112.5" y="134" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">Routeur / switch</text><text x="112.5" y="157" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">ingress, egress</text><rect x="220" y="82" width="165" height="112" rx="12" fill="#1b2b3a" stroke="#60a5fa" stroke-width="2"/><text x="302.5" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Métrage</text><text x="302.5" y="134" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">Records + cache</text><text x="302.5" y="157" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">compteurs</text><rect x="410" y="82" width="165" height="112" rx="12" fill="#332817" stroke="#fbbf24" stroke-width="2"/><text x="492.5" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Export</text><text x="492.5" y="134" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">NetFlow v9</text><text x="492.5" y="157" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">ou IPFIX</text><rect x="600" y="82" width="165" height="112" rx="12" fill="#193628" stroke="#4ade80" stroke-width="2"/><text x="682.5" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Ingestion</text><text x="682.5" y="134" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">parseur</text><text x="682.5" y="157" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">templates / files</text><rect x="790" y="82" width="140" height="112" rx="12" fill="#292642" stroke="#a78bfa" stroke-width="2"/><text x="860.0" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Analyse</text><text x="860.0" y="134" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">stockage</text><text x="860.0" y="157" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">alertes</text><line x1="195" y1="137" x2="212.0" y2="137.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="220,137 212.0,141.4 212.0,132.6" fill="#9fb5d0"/><line x1="385" y1="137" x2="402.0" y2="137.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="410,137 402.0,141.4 402.0,132.6" fill="#9fb5d0"/><line x1="575" y1="137" x2="592.0" y2="137.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="600,137 592.0,141.4 592.0,132.6" fill="#9fb5d0"/><line x1="765" y1="137" x2="782.0" y2="137.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="790,137 782.0,141.4 782.0,132.6" fill="#9fb5d0"/><rect x="65" y="235" width="830" height="95" rx="12" fill="#101c2b" stroke="#334a66" stroke-width="2"/><text x="480" y="262" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">La télémétrie est une chaîne : une rupture à chaque étage produit un symptôme différent</text><text x="480" y="289" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">Trafic valide ≠ cache valide ≠ export reçu ≠ template décodé ≠ interprétation correcte</text><text x="480" y="313" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#9fb2c9">Chaque étape doit avoir ses propres compteurs, journaux et tests de santé.</text></svg>

### 1.1 Construire un contrat de télémétrie

Avant d’installer un monitor, définis un contrat de mesure documenté :

| Question | Exigence à consigner |
|---|---|
| Quel trafic ? | IPv4/IPv6, unicast/multicast si supporté, applications ou sous-réseaux ciblés |
| Où observe-t-on ? | Routeur, interface, direction, VRF, avant/après NAT, zone réseau |
| Quelle identité de flux ? | Champs `match`, clés de conversation, prise en compte des ports et protocoles |
| Quelles mesures ? | Octets, paquets, horodatages, interfaces, TCP flags ou autres champs réellement disponibles |
| Quelle qualité ? | Sampling, perte acceptable, délai maximal, précision recherchée |
| Qui consomme ? | NOC, capacité, sécurité, équipe applicative, facturation interne |
| Quelle rétention ? | Résolution, durée, index, accès et suppression |

Sans ce contrat, les équipes peuvent utiliser le même mot « débit » pour décrire des mesures produites à des points différents. Cela crée de faux écarts, des alertes contradictoires et des analyses impossibles à reproduire.

### 1.2 Mesure contre capture

Un enregistrement de flux représente généralement une agrégation de paquets qui partagent des attributs de clé et un cycle de vie dans le cache. Ce n’est pas l’équivalent d’un PCAP : on n’obtient pas automatiquement la charge utile, les retransmissions complètes, le contenu HTTP ou la cause applicative d’une transaction. Pour comprendre un protocole ou valider une séquence précise, il peut être nécessaire de compléter NetFlow par une capture ciblée, des journaux applicatifs, des compteurs d’interface, une télémétrie de file ou une trace de bout en bout.


## 2. Conception avancée des records et cardinalité

Le record définit la manière dont des paquets deviennent des flux. Les champs clés (« match ») décident si deux paquets appartiennent à la même entrée ; les champs collectés (« collect ») ajoutent des mesures ou du contexte. Une clé plus détaillée donne davantage de visibilité, mais augmente normalement le nombre de flux distincts. À grande échelle, le choix de clé est une décision de capacité autant qu’une décision d’analyse.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-2-title nfexp-2-desc"><title id="nfexp-2-title">Choisir la granularité d’un flow record</title><desc id="nfexp-2-desc">Comparer une clé trop grossière, un record bien dimensionné et un record trop granulaire.</desc><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">Choisir la granularité d’un flow record</text><rect x="26" y="82" width="286" height="225" rx="12" fill="#3a202a" stroke="#fb7185" stroke-width="2"/><text x="169.0" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Trop agrégé</text><text x="169.0" y="134" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">Clé : protocole</text><text x="169.0" y="157" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">Volume global du réseau</text><text x="169.0" y="180" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">Peu de séries à stocker</text><text x="169.0" y="203" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">Mais peu de diagnostic</text><rect x="337" y="82" width="286" height="225" rx="12" fill="#193628" stroke="#4ade80" stroke-width="2"/><text x="480.0" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Granularité équilibrée</text><text x="480.0" y="134" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">IP source / destination</text><text x="480.0" y="157" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">protocole + ports, VRF</text><text x="480.0" y="180" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">direction / interface si utile</text><text x="480.0" y="203" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">Bon compromis pour l’incident</text><rect x="648" y="82" width="286" height="225" rx="12" fill="#332817" stroke="#fbbf24" stroke-width="2"/><text x="791.0" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Trop granulaire</text><text x="791.0" y="134" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">Clés variables / champs rares</text><text x="791.0" y="157" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">trop de dimensions</text><text x="791.0" y="180" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">cardinalité et cache élevés</text><text x="791.0" y="203" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">coût sans gain analytique</text><text x="480" y="344" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="600" fill="#c3d2e5">Une clé plus détaillée augmente le nombre de flux distincts : mesure la cardinalité avant le déploiement.</text></svg>

### 2.1 Pourquoi la cardinalité devient critique

Supposons qu’un routeur observe 800 000 tuples source/destination/ports/protocole différents pendant une fenêtre courte. Si l’on ajoute l’interface d’entrée, la direction, la VRF et un champ variable à la clé, plusieurs paquets auparavant agrégés deviennent des entrées distinctes. Les dimensions supplémentaires peuvent être utiles, mais elles ont un prix : nombre d’entrées dans le cache, consommation mémoire, fréquence d’expiration, volume exporté, charge du collecteur et coût des index.

La règle d’ingénierie n’est pas « choisir toujours la clé la plus précise ». Elle est : **choisir la clé la moins coûteuse qui répond à la question opérationnelle**. Pour un tableau de capacité, un niveau d’agrégation par préfixe ou interface peut être préférable à un détail par port source. Pour une investigation de scan TCP, les ports et les destinations deviennent pertinents, pendant une durée et sur un périmètre limités.

### 2.2 Exemples de choix de clé

| Cas d’usage | Clé souvent pertinente | Risque à éviter |
|---|---|---|
| Capacité WAN | préfixes, interface, direction, protocole | ajouter trop de champs qui n’améliorent pas la décision |
| Diagnostic d’un service | IP source/destination, ports, protocole, VRF | comparer des points d’observation différents sans normalisation |
| Investigation de scan | source, destination, ports, protocole, fenêtre temporelle | laisser une clé très fine active en permanence si elle épuise le cache |
| Analyse multi-tenant | VRF / contexte de tenant si supporté | mélanger des espaces d’adressage chevauchants |
| Détection de volumes sortants | direction, destination, volume, durée et contexte | supposer qu’un volume élevé est malveillant sans baseline |

### 2.3 Champs manquants, champs inconnus, champs à zéro

Un collecteur peut afficher une valeur vide parce que l’exportateur ne l’a pas fourni, parce que le template ne la décrit pas, parce que le parseur ne la comprend pas ou parce que la valeur n’est pas observable au point de mesure. Ne traite pas automatiquement `0`, `unknown`, `null` et « absent du template » comme une même valeur. Elles peuvent correspondre à des situations différentes.

Pour chaque champ analytique important, documente : type, unité, sémantique, source, condition d’observabilité, valeur d’absence et éventuelle conversion. C’est particulièrement important pour les octets, paquets, temps de début/fin, interfaces, direction, identifiants de VRF, AS BGP et champs spécifiques au fournisseur.

### 2.4 Records dédiés plutôt qu’un record universel

Un « record universel » très large peut paraître pratique, mais ne convient pas à tous les usages. Une pratique plus contrôlable consiste à séparer, lorsque le matériel le permet, les profils :

- **Capacité** : clés plus agrégées, mesures compactes, longue rétention.
- **Diagnostic** : clés plus détaillées, périmètre de déploiement restreint et durée contrôlée.
- **Sécurité** : champs de contexte utiles à la détection, gouvernance des accès et conservation définie.

La séparation augmente la complexité de configuration et peut augmenter la charge du routeur. Il faut donc mesurer le coût réel sur une plateforme représentative avant de généraliser.


## 3. Points d’observation, direction, NAT et chemins asymétriques

Le point d’observation fait partie de la sémantique de la donnée. Deux exportateurs peuvent décrire le même trafic avec des adresses différentes, des compteurs différents ou un seul sens de la conversation. Le routeur de bord peut voir le trafic avant traduction d’adresses, tandis qu’un autre point voit la version traduite. Un chemin retour peut passer par un autre routeur, notamment avec ECMP, multihoming ou routage asymétrique.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="385" viewBox="0 0 960 385" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-3-title nfexp-3-desc"><title id="nfexp-3-title">Le point d’observation détermine le sens des données</title><desc id="nfexp-3-desc">Le NAT, le multi-chemin et les observations à plusieurs interfaces peuvent modifier les clés observées et provoquer un double comptage.</desc><rect x="1" y="1" width="958" height="383" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">Le point d’observation détermine le sens des données</text><rect x="28" y="98" width="172" height="100" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="114.0" y="124" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Client</text><text x="114.0" y="150" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">10.1.4.20</text><rect x="258" y="98" width="190" height="100" rx="12" fill="#332817" stroke="#fbbf24" stroke-width="2"/><text x="353.0" y="124" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Edge / NAT</text><text x="353.0" y="150" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">IP privée → publique</text><text x="353.0" y="173" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">frontière de traduction</text><rect x="515" y="98" width="178" height="100" rx="12" fill="#1b2b3a" stroke="#60a5fa" stroke-width="2"/><text x="604.0" y="124" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Cœur réseau</text><text x="604.0" y="150" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">ECMP / chemins</text><text x="604.0" y="173" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">asymétrie possible</text><rect x="760" y="98" width="172" height="100" rx="12" fill="#193628" stroke="#4ade80" stroke-width="2"/><text x="846.0" y="124" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Serveur</text><text x="846.0" y="150" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">203.0.113.80</text><line x1="200" y1="148" x2="250.0" y2="148.0" stroke="#38bdf8" stroke-width="2.5"/><polygon points="258,148 250.0,152.4 250.0,143.6" fill="#38bdf8"/><line x1="448" y1="148" x2="507.0" y2="148.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="515,148 507.0,152.4 507.0,143.6" fill="#9fb5d0"/><line x1="693" y1="148" x2="752.0" y2="148.0" stroke="#4ade80" stroke-width="2.5"/><polygon points="760,148 752.0,152.4 752.0,143.6" fill="#4ade80"/><rect x="65" y="242" width="382" height="84" rx="12" fill="#111c30" stroke="#334a66" stroke-width="2"/><text x="256" y="270" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15px" font-weight="700" fill="#f4f8ff">Mesure avant NAT</text><text x="256" y="295" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">voit la source privée et le sens côté LAN</text><rect x="513" y="242" width="382" height="84" rx="12" fill="#111c30" stroke="#334a66" stroke-width="2"/><text x="704" y="270" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15px" font-weight="700" fill="#f4f8ff">Mesure après NAT / au cœur</text><text x="704" y="295" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">voit d’autres adresses et peut manquer le retour</text><text x="480" y="355" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="600" fill="#fbbf24">Ne fusionne pas deux observations sans identifier leur point, leur direction et leur périmètre.</text></svg>

### 3.1 Méthode de normalisation

Lorsqu’on agrège les données provenant de plusieurs routeurs, stocke au minimum le nom stable de l’exportateur, l’interface d’observation, la direction, l’Observation Domain ID lorsque le protocole l’utilise, la version d’export et la fenêtre temporelle. Si le collecteur remplace ou normalise ces identifiants, conserve aussi la valeur d’origine pour le dépannage.

Ne somme pas les compteurs de plusieurs points d’observation pour calculer un volume réseau global sans démontrer que les points représentent des populations distinctes. Mesurer le même paquet à l’entrée et à la sortie d’un routeur peut compter deux fois le trafic logique. Inversement, mesurer sur un seul lien peut ignorer un chemin de retour alternatif.

### 3.2 Avant et après NAT

Le NAT peut modifier les adresses et les ports visibles. Si les flux sont corrélés entre un point avant NAT et un point après NAT, il faut disposer d’un lien fiable entre les tuples d’origine et traduits : journaux NAT, métadonnées fournies par l’équipement ou autre mécanisme supporté. Une simple proximité temporelle n’est pas une preuve suffisante, notamment en présence de nombreux clients partageant une adresse publique.

### 3.3 VRF, VLAN, interface et contexte de routage

Des espaces d’adresses peuvent se chevaucher dans des VRF différentes. Une adresse seule ne suffit donc pas toujours à identifier un hôte. De même, un index d’interface peut changer après un redémarrage ou une modification de configuration ; privilégie les données de référence permettant de retrouver le nom et le rôle de l’interface au moment de la mesure. Si cette table de référence est exportée sous forme d’options/templates, vérifie la prise en charge de la plateforme et du collecteur.


## 4. NetFlow v9 et IPFIX : templates, sessions et décodage

NetFlow v9 et IPFIX utilisent des templates qui décrivent la structure des enregistrements. Le collecteur doit connaître le template applicable aux données qu’il reçoit. Le template n’est pas simplement un en-tête décoratif : il associe un identifiant à une séquence de champs et à leurs longueurs. Sans cet état, le collecteur ne sait pas interpréter correctement les Data Sets.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-4-title nfexp-4-desc"><title id="nfexp-4-title">Template IPFIX / NetFlow v9 : la dépendance à l’état</title><desc id="nfexp-4-desc">L’exportateur décrit le format; le collecteur doit connaître le template applicable avant de décoder les Data Sets.</desc><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">Template IPFIX / NetFlow v9 : la dépendance à l’état</text><rect x="30" y="92" width="245" height="118" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="152.5" y="118" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Exportateur</text><text x="152.5" y="144" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">ID de template</text><text x="152.5" y="167" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">champs + longueurs</text><text x="152.5" y="190" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">données de flux</text><rect x="356" y="92" width="245" height="118" rx="12" fill="#332817" stroke="#fbbf24" stroke-width="2"/><text x="478.5" y="118" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Transport</text><text x="478.5" y="144" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">UDP / TCP / SCTP</text><text x="478.5" y="167" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">selon protocole</text><text x="478.5" y="190" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">et plateforme</text><rect x="682" y="92" width="245" height="118" rx="12" fill="#193628" stroke="#4ade80" stroke-width="2"/><text x="804.5" y="118" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Collecteur</text><text x="804.5" y="144" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">cache de templates</text><text x="804.5" y="167" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">puis décodage</text><text x="804.5" y="190" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">des Data Sets</text><line x1="275" y1="130" x2="348.0" y2="130.0" stroke="#38bdf8" stroke-width="2.5"/><polygon points="356,130 348.0,134.4 348.0,125.6" fill="#38bdf8"/><line x1="275" y1="174" x2="348.0" y2="174.0" stroke="#38bdf8" stroke-width="2.5"/><polygon points="356,174 348.0,178.4 348.0,169.6" fill="#38bdf8"/><text x="315" y="119" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="700" fill="#38bdf8">Template</text><text x="315" y="198" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="700" fill="#38bdf8">Data</text><line x1="601" y1="130" x2="674.0" y2="130.0" stroke="#4ade80" stroke-width="2.5"/><polygon points="682,130 674.0,134.4 674.0,125.6" fill="#4ade80"/><line x1="601" y1="174" x2="674.0" y2="174.0" stroke="#4ade80" stroke-width="2.5"/><polygon points="682,174 674.0,178.4 674.0,169.6" fill="#4ade80"/><text x="642" y="119" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="700" fill="#4ade80">Template reçu</text><text x="642" y="198" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="700" fill="#4ade80">Data Set</text><rect x="90" y="256" width="780" height="83" rx="12" fill="#3a202a" stroke="#fb7185" stroke-width="2"/><text x="480" y="282" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15px" font-weight="700" fill="#f4f8ff">Si le template manque ou a expiré, les paquets peuvent arriver sans être décodables.</text><text x="480" y="310" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">Vérifier la session, l’Observation Domain ID, les refreshes et les compteurs du collecteur.</text></svg>

### 4.1 NetFlow v9 et IPFIX ne sont pas synonymes

NetFlow v9 est un format export propriétaire de Cisco largement implémenté, fondé sur les templates. IPFIX est un protocole normalisé par l’IETF ; son numéro de version dans l’en-tête est `10`. Les deux modèles partagent l’approche par templates, mais ne doivent pas être considérés comme interchangeables octet pour octet. Le support des transports, des éléments d’information et des extensions dépend de l’exportateur et du collecteur.

### 4.2 État de template et perte d’information

Avec UDP, la perte d’un message de template peut empêcher le collecteur de décoder les Data Sets correspondants jusqu’à ce qu’un template utilisable soit reçu de nouveau. Le mécanisme de rafraîchissement des templates, les délais de validité et les diagnostics diffèrent selon la solution. IPFIX conserve l’état de templates dans le contexte de transport et de l’Observation Domain ; un collecteur ne doit pas réutiliser aveuglément un template issu d’une session distincte. Cette nuance est importante lors d’un redémarrage de l’exportateur, d’une bascule de collecteur ou d’une réinitialisation de session.

### 4.3 Numéros de séquence et perte apparente

Les champs de séquence servent à détecter certains trous dans le flux d’export. Leur sémantique dépend du format. Pour IPFIX, le Sequence Number reflète le nombre cumulatif de Data Records envoyés dans le domaine d’observation au sein de la session concernée. Ce n’est pas un numéro de séquence TCP et ce n’est pas un compteur de tous les paquets utilisateurs. Pour NetFlow v9, vérifie la définition exacte du format et l’interprétation de l’exportateur/collecteur utilisé.

Un trou de séquence peut être un indice de perte d’export ou d’un redémarrage, mais il ne prouve pas automatiquement une perte de trafic utilisateur. Compare les compteurs de l’exportateur, l’état des templates, les statistiques de transport, les logs du collecteur et la continuité des horodatages.

### 4.4 Contrôles à automatiser

- Détecter une disparition anormale de templates connus.
- Alerter sur l’absence de nouveaux records alors que l’interface reste active.
- Compter les datagrammes reçus, les messages décodés et les enregistrements rejetés séparément.
- Documenter les versions et les éléments d’information pris en charge par l’exportateur et le collecteur.
- Vérifier l’horloge, la continuité après redémarrage et les changements d’Observation Domain ID.
- Conserver des tests de compatibilité lors d’une montée de version du collecteur.


## 5. Cache, expiration et charge de l’exportateur

Le cache rassemble les paquets en entrées de flux. Il ne s’agit pas d’une base de données infinie : ses capacités et mécanismes de vieillissement sont propres à la plateforme. Le timeout inactif permet de fermer des entrées qui ne reçoivent plus de paquets ; un timeout actif peut déclencher l’export périodique d’une entrée toujours active. La fréquence d’export influence la fraîcheur et le volume d’enregistrements.

### 5.1 Compromis entre fraîcheur, volume et ressources

Des expirations très courtes peuvent fournir des données plus fraîches, mais générer davantage d’enregistrements, de messages et de charge pour l’exportateur et le collecteur. Des expirations longues peuvent réduire le nombre de records, mais retarder les analyses et conserver davantage d’entrées actives. La meilleure valeur dépend du trafic, de la capacité du routeur, de la granularité de clé, du besoin de temps réel et de la politique de stockage.

### 5.2 Symptômes de pression sur le cache

Les symptômes possibles comprennent un nombre d’entrées qui approche la limite, une hausse des créations/expirations, des pertes ou rejets signalés par la plateforme, des exportations retardées ou une charge CPU anormale. Les commandes exactes de diagnostic sont propres à la version IOS/IOS XE ou à la gamme matérielle. Il faut surveiller les statistiques que la plateforme expose plutôt que présumer qu’un compteur universel existe.

### 5.3 Procédure de mise à l’échelle

1. Mesurer le nombre d’entrées et le nombre de records exportés sur une période représentative.
2. Tester le record et le monitor sur une interface pilote au débit de pointe.
3. Ajouter progressivement les interfaces, pas toutes en même temps.
4. Comparer l’usage CPU/mémoire et le débit de forwarding à la baseline sans télémétrie.
5. Vérifier si le nombre de records augmente comme prévu après chaque nouvelle clé ou chaque nouveau monitor.
6. Définir une procédure de désactivation rapide et testée.

Une configuration syntaxiquement valide n’est pas nécessairement adaptée à la capacité matérielle. Le matériel peut imposer des limites par ASIC, direction, type de trafic, nombre de monitors ou type de cache.


## 6. Sampling : qualité statistique et biais d’analyse

Le sampling réduit la quantité de paquets ou de flux sélectionnés. Il est utile lorsque la collecte exhaustive est trop coûteuse, mais ses résultats dépendent de la technique utilisée, de sa fraction, du trafic et de la façon dont le collecteur applique ou non une extrapolation. Une mesure extrapolée ne devient pas équivalente à une mesure exhaustive.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-5-title nfexp-5-desc"><title id="nfexp-5-title">Échantillonnage : mesure, estimation et incertitude</title><desc id="nfexp-5-desc">Un échantillon sert à estimer la population, sans être identique au trafic complet.</desc><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">Échantillonnage : mesure, estimation et incertitude</text><rect x="30" y="95" width="185" height="112" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="122.5" y="121" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Population</text><text x="122.5" y="147" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">1 000 000 paquets</text><text x="122.5" y="170" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">volume réel</text><rect x="260" y="95" width="185" height="112" rx="12" fill="#332817" stroke="#fbbf24" stroke-width="2"/><text x="352.5" y="121" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Sélecteur</text><text x="352.5" y="147" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">1:100</text><text x="352.5" y="170" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">type documenté</text><rect x="490" y="95" width="185" height="112" rx="12" fill="#1b2b3a" stroke="#60a5fa" stroke-width="2"/><text x="582.5" y="121" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Échantillon</text><text x="582.5" y="147" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">≈ 10 000 paquets</text><text x="582.5" y="170" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">variabilité</text><rect x="720" y="95" width="210" height="112" rx="12" fill="#193628" stroke="#4ade80" stroke-width="2"/><text x="825.0" y="121" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Estimation</text><text x="825.0" y="147" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">multiplier / 100</text><text x="825.0" y="170" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">pas une vérité exacte</text><line x1="215" y1="151" x2="252.0" y2="151.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="260,151 252.0,155.4 252.0,146.6" fill="#9fb5d0"/><line x1="445" y1="151" x2="482.0" y2="151.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="490,151 482.0,155.4 482.0,146.6" fill="#9fb5d0"/><line x1="675" y1="151" x2="712.0" y2="151.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="720,151 712.0,155.4 712.0,146.6" fill="#9fb5d0"/><rect x="74" y="248" width="812" height="84" rx="12" fill="#111c30" stroke="#334a66" stroke-width="2"/><text x="480" y="276" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15px" font-weight="700" fill="#f4f8ff">La fraction d’échantillonnage doit être conservée avec les données.</text><text x="480" y="303" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">Risque : les petits flux et les événements rares peuvent être sous-représentés.</text></svg>

### 6.1 Paquet sélectionné ou flux sélectionné

L’échantillonnage de paquets et l’échantillonnage de flux ne sont pas la même chose. Avec une sélection de paquets, seuls certains paquets contribuent à la mesure ; les compteurs doivent être interprétés en tenant compte du mécanisme. Avec une sélection de flux, le mécanisme choisit des flux selon une logique définie. Les deux approches peuvent donner des biais différents selon la distribution des tailles de flux et les paramètres de sélection.

### 6.2 Pourquoi les petits flux sont difficiles

Avec un échantillonnage systématique très faible, un flux de quelques paquets peut ne jamais être représenté, alors qu’un flux volumineux a plus de chances d’être observé. Il est dangereux d’utiliser un jeu de données échantillonné pour conclure à l’absence d’une activité rare. Un analyste doit connaître la méthode de sélection, la fraction, le point d’application, la configuration de l’équipement et l’approximation produite par le collecteur.

### 6.3 Métadonnées à conserver

Conserve la méthode et la fraction d’échantillonnage, l’intervalle temporel, le point d’observation et les informations d’export pertinentes. Lorsque les paramètres changent, marque le changement dans les données ou les métadonnées d’inventaire. Comparer des périodes échantillonnées différemment sans correction peut créer une fausse hausse ou baisse.

### 6.4 Exemple de raisonnement

Si une méthode sélectionne approximativement un paquet sur 100, un volume observé de 10 000 paquets peut suggérer environ 1 000 000 de paquets dans la population. Cette estimation n’est pas une garantie exacte : il existe une variabilité de sélection, et l’estimation dépend de la méthode. Pour un incident de sécurité à faible volume, l’échantillonnage peut manquer précisément les paquets qui importent. Pour des tendances de capacité, une estimation peut être acceptable si ses limites sont explicites.


## 7. IP SLA avancé : qualité réseau, seuils et tracking

IP SLA mesure une opération active : par exemple l’écho ICMP, le délai, la gigue ou certaines transactions applicatives prises en charge par la plateforme. Le choix du type d’opération et de la cible est essentiel. Une sonde doit tester le chemin correspondant à la question opérationnelle, et non simplement une adresse facile à joindre.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-6-title nfexp-6-desc"><title id="nfexp-6-title">IP SLA expert : sonde, seuil, tracking et action contrôlée</title><desc id="nfexp-6-desc">La sonde produit des mesures; une logique d’état les interprète; le tracking peut déclencher une action supportée.</desc><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">IP SLA expert : sonde, seuil, tracking et action contrôlée</text><rect x="28" y="100" width="170" height="112" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="113.0" y="126" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Sonde active</text><text x="113.0" y="152" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">ICMP / UDP / HTTP*</text><text x="113.0" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">source + cible</text><text x="113.0" y="198" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">fréquence définie</text><rect x="232" y="100" width="170" height="112" rx="12" fill="#1b2b3a" stroke="#60a5fa" stroke-width="2"/><text x="317.0" y="126" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Mesures</text><text x="317.0" y="152" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">RTT / gigue</text><text x="317.0" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">perte / timeout</text><text x="317.0" y="198" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">historique</text><rect x="436" y="100" width="170" height="112" rx="12" fill="#332817" stroke="#fbbf24" stroke-width="2"/><text x="521.0" y="126" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Évaluation</text><text x="521.0" y="152" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">seuil de délai</text><text x="521.0" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">état de reachability</text><text x="521.0" y="198" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">N mesures / délai</text><rect x="640" y="100" width="130" height="112" rx="12" fill="#193628" stroke="#4ade80" stroke-width="2"/><text x="705.0" y="126" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Track</text><text x="705.0" y="152" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">UP / DOWN</text><text x="705.0" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">stabilisation</text><text x="705.0" y="198" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">journal</text><rect x="804" y="100" width="128" height="112" rx="12" fill="#292642" stroke="#a78bfa" stroke-width="2"/><text x="868.0" y="126" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Action</text><text x="868.0" y="152" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="400" fill="#c3d2e5">route / HSRP</text><text x="868.0" y="175" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="400" fill="#c3d2e5">alerte</text><text x="868.0" y="198" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="400" fill="#c3d2e5">selon support</text><line x1="198" y1="155" x2="224.0" y2="155.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="232,155 224.0,159.4 224.0,150.6" fill="#9fb5d0"/><line x1="402" y1="155" x2="428.0" y2="155.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="436,155 428.0,159.4 428.0,150.6" fill="#9fb5d0"/><line x1="606" y1="155" x2="632.0" y2="155.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="640,155 632.0,159.4 632.0,150.6" fill="#9fb5d0"/><line x1="770" y1="155" x2="796.0" y2="155.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="804,155 796.0,159.4 796.0,150.6" fill="#9fb5d0"/><rect x="55" y="252" width="850" height="84" rx="12" fill="#111c30" stroke="#334a66" stroke-width="2"/><text x="480" y="278" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15px" font-weight="700" fill="#f4f8ff">Une mesure de performance et un état de joignabilité sont deux signaux distincts.</text><text x="480" y="304" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">Le tracking doit inclure temporisations de transition, validation du retour et scénario de faux positif.</text><text x="480" y="324" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#9fb2c9">* Le type exact de sonde et les actions disponibles varient selon la plateforme.</text></svg>

### 7.1 Conception d’une sonde de qualité

Précise le type d’opération, l’adresse cible, l’interface ou l’adresse source, la fréquence, le timeout, le seuil, la planification et le comportement attendu si la cible ne répond pas. Sur un réseau multi-VRF, vérifie que la sonde utilise le contexte de routage attendu. Une sonde envoyée depuis la mauvaise source peut emprunter un chemin différent du trafic utilisateur.

### 7.2 Seuil, timeout et état ne sont pas interchangeables

Le **timeout** limite la durée d’attente d’une opération. Le **threshold** représente une limite de performance pour certaines opérations prises en charge. Le **state/reachability** reflète si l’opération est réussie ou joignable selon les règles de la plateforme. Une opération peut être joignable tout en dépassant un seuil de délai ; inversement, un délai mesuré peut être absent lorsqu’une opération expire. Il faut préciser quel état est utilisé par l’alerte ou par le tracking.

### 7.3 Hystérésis, temporisation et faux positifs

Les variations brèves de délai et de perte sont courantes. Une alerte qui bascule au premier échantillon hors seuil peut osciller pendant un incident. Selon la fonctionnalité disponible, utilise des délais de transition, plusieurs mesures consécutives, une fenêtre glissante ou un mécanisme d’hystérésis. Le choix exact doit être testé : trop de stabilisation retarde la détection ; trop peu produit des alertes inutiles.

### 7.4 Tracking et actions automatiques

Un objet de tracking peut relier l’état d’une opération IP SLA à une route, à une politique ou à un mécanisme de redondance, selon la plateforme. Toute action automatique doit être conçue avec un état de retour, un délai de stabilisation, des conditions de rétablissement et un journal. Une sonde mal conçue peut retirer une route fonctionnelle ou déclencher une bascule instable. Teste séparément la perte de la cible, le filtrage ICMP, la perte de l’accès de management et une panne d’application.

### 7.5 Éviter les sondes qui mentent

- Une cible proche ne mesure pas le service distant.
- Une cible qui répond à ICMP n’assure pas la disponibilité de HTTP, DNS ou d’une base de données.
- Une sonde depuis le routeur peut suivre un chemin différent de celui d’un hôte utilisateur.
- Une sonde trop fréquente consomme des ressources et peut elle-même charger le réseau.
- Une cible filtrant l’ICMP peut provoquer une fausse alerte de disponibilité si le protocole n’est pas adapté.


## 8. Corréler IP SLA, NetFlow et santé des interfaces

La corrélation fiable repose sur trois facteurs : même fenêtre temporelle, même chemin logique et métriques ayant une sémantique connue. Quand le délai augmente, les données NetFlow permettent de rechercher des changements de volumes ou de populations, tandis que les compteurs d’interface et de QoS montrent si le lien, la file ou le routeur est sous pression. Aucune source seule ne donne automatiquement la cause.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="365" viewBox="0 0 960 365" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-7-title nfexp-7-desc"><title id="nfexp-7-title">Corrélation IP SLA, NetFlow et compteurs d’interface</title><desc id="nfexp-7-desc">Un événement de latence doit être comparé aux volumes de flux et aux compteurs physiques dans la même fenêtre temporelle.</desc><rect x="1" y="1" width="958" height="363" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">Corrélation IP SLA, NetFlow et compteurs d’interface</text><text x="480" y="72" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Corrélation temporelle multi-source autour d’un incident</text><line x1="160" y1="105" x2="160" y2="305" stroke="#263c57" stroke-width="1" stroke-dasharray="4 5"/><line x1="300" y1="105" x2="300" y2="305" stroke="#263c57" stroke-width="1" stroke-dasharray="4 5"/><line x1="440" y1="105" x2="440" y2="305" stroke="#263c57" stroke-width="1" stroke-dasharray="4 5"/><line x1="580" y1="105" x2="580" y2="305" stroke="#263c57" stroke-width="1" stroke-dasharray="4 5"/><line x1="720" y1="105" x2="720" y2="305" stroke="#263c57" stroke-width="1" stroke-dasharray="4 5"/><line x1="860" y1="105" x2="860" y2="305" stroke="#263c57" stroke-width="1" stroke-dasharray="4 5"/><text x="38" y="138" text-anchor="start" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="700" fill="#38bdf8">IP SLA</text><text x="38" y="208" text-anchor="start" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="700" fill="#4ade80">NetFlow</text><text x="38" y="278" text-anchor="start" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="700" fill="#fbbf24">Interface</text><line x1="135" y1="145" x2="910" y2="145" stroke="#38bdf8" stroke-width="2"/><polyline points="160,139 230,137 300,132 370,123 440,114 510,116 580,130 650,138 720,139 790,137 860,136" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><line x1="135" y1="215" x2="910" y2="215" stroke="#4ade80" stroke-width="2"/><rect x="151" y="201" width="18" height="14" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><rect x="221" y="197" width="18" height="18" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><rect x="291" y="195" width="18" height="20" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><rect x="361" y="181" width="18" height="34" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><rect x="431" y="159" width="18" height="56" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><rect x="501" y="151" width="18" height="64" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><rect x="571" y="167" width="18" height="48" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><rect x="641" y="185" width="18" height="30" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><rect x="711" y="195" width="18" height="20" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><rect x="781" y="198" width="18" height="17" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><rect x="851" y="201" width="18" height="14" rx="3" fill="#4ade80" stroke="#4ade80" stroke-width="1"/><line x1="135" y1="285" x2="910" y2="285" stroke="#fbbf24" stroke-width="2"/><rect x="151" y="277" width="18" height="8" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><rect x="221" y="276" width="18" height="9" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><rect x="291" y="273" width="18" height="12" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><rect x="361" y="257" width="18" height="28" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><rect x="431" y="247" width="18" height="38" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><rect x="501" y="239" width="18" height="46" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><rect x="571" y="245" width="18" height="40" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><rect x="641" y="254" width="18" height="31" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><rect x="711" y="267" width="18" height="18" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><rect x="781" y="275" width="18" height="10" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><rect x="851" y="276" width="18" height="9" rx="3" fill="#332817" stroke="#fbbf24" stroke-width="1"/><line x1="440" y1="95" x2="440" y2="314" stroke="#fb7185" stroke-width="3" stroke-dasharray="6 4"/><text x="454" y="100" text-anchor="start" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="700" fill="#fb7185">t₀</text><text x="480" y="340" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">Aligner les horodatages, la direction, le point d’observation et les fenêtres d’agrégation.</text></svg>

### 8.1 Méthode d’investigation

1. **Valider le symptôme** : quelle sonde, quelle cible, quelle valeur, depuis quel contexte, à quelle heure ?
2. **Comparer avec la baseline** : est-ce une hausse de latence, de gigue, de perte, ou simplement un changement attendu de trafic ?
3. **Examiner NetFlow** : top talkers, protocoles, destinations, sens, durées, volumes et nouvelles populations.
4. **Examiner l’interface et la QoS** : débit, erreurs, drops, files, policers, congestion, CPU et compteurs par classe si disponibles.
5. **Vérifier le chemin** : route, ECMP, asymétrie, NAT, politique de routage et changements récents.
6. **Formuler une hypothèse falsifiable** : par exemple « la latence vers la cible augmente pendant que la file de sortie WAN est saturée par tel agrégat de flux ».
7. **Valider ou rejeter** avec une mesure indépendante, un test contrôlé ou un autre point d’observation.

### 8.2 Exemple de matrice de corrélation

| IP SLA | NetFlow | Compteurs interface / QoS | Interprétation initiale |
|---|---|---|---|
| Délai en hausse | Flux dominants en forte hausse | Utilisation et drops en hausse | Congestion plausible, à confirmer par la file et le chemin |
| Délai en hausse | Volumes stables | Interface saine | Chercher chemin, serveur, traitement, filtrage ou cible |
| Perte SLA | Flux absents au collecteur | Interface voit du trafic | Défaillance de collecte possible, mais vérifier le point d’observation |
| SLA stable | Gros flux sortant | Aucun drop | Volume potentiellement légitime ; évaluer la capacité et le contexte |
| SLA instable | Peu de flux visibles | Compteurs d’erreurs en hausse | Problème physique ou visibilité insuffisante à étudier |

### 8.3 Aligner les horodatages

La différence entre l’heure d’export, l’heure de collecte et l’heure réelle de mesure peut fausser l’analyse. Vérifie NTP, timezone, la sémantique des champs temporels, les délais d’export et la résolution d’agrégation du collecteur. Ne compare pas un point IP SLA toutes les dix secondes avec une agrégation NetFlow de cinq minutes sans comprendre ce que cette agrégation masque.


## 9. Détection et analytique réseau avancées

NetFlow apporte une vue comportementale : qui communique avec qui, sur quel protocole, à quel moment, et avec quel volume selon les champs exportés. Cette vue aide à repérer les écarts, mais elle ne prouve pas une intention malveillante. Les résultats doivent être contextualisés et enrichis par des sources adaptées.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-8-title nfexp-8-desc"><title id="nfexp-8-title">Interpréter des motifs de sécurité sans surconclure</title><desc id="nfexp-8-desc">Exemples de motifs de flux utiles à la détection, toujours à confirmer par d’autres sources.</desc><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">Interpréter des motifs de sécurité sans surconclure</text><rect x="25" y="82" width="190" height="42" rx="8" fill="#1c3049" stroke="#405a78" stroke-width="1"/><text x="120.0" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="700" fill="#f4f8ff">Signal de flux</text><rect x="225" y="82" width="310" height="42" rx="8" fill="#1c3049" stroke="#405a78" stroke-width="1"/><text x="380.0" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="700" fill="#f4f8ff">Motif observé</text><rect x="545" y="82" width="390" height="42" rx="8" fill="#1c3049" stroke="#405a78" stroke-width="1"/><text x="740.0" y="108" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="700" fill="#f4f8ff">Contrôles complémentaires</text><rect x="25" y="136" width="190" height="48" rx="6" fill="#111c30" stroke="#2c415b" stroke-width="1"/><text x="120" y="164" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="700" fill="#f4f8ff">DDoS / flood</text><rect x="225" y="136" width="310" height="48" rx="6" fill="#111c30" stroke="#2c415b" stroke-width="1"/><text x="380" y="156" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">Beaucoup de sources ou</text><text x="380" y="172" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">pps vers peu de cibles</text><rect x="545" y="136" width="390" height="48" rx="6" fill="#111c30" stroke="#2c415b" stroke-width="1"/><text x="740" y="156" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">pps, drops, état du service</text><text x="740" y="172" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">ACL / mitigation</text><rect x="25" y="189" width="190" height="48" rx="6" fill="#0f1929" stroke="#2c415b" stroke-width="1"/><text x="120" y="217" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="700" fill="#f4f8ff">Scan de ports</text><rect x="225" y="189" width="310" height="48" rx="6" fill="#0f1929" stroke="#2c415b" stroke-width="1"/><text x="380" y="209" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">Une source → nombreux</text><text x="380" y="225" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">hôtes ou ports</text><rect x="545" y="189" width="390" height="48" rx="6" fill="#0f1929" stroke="#2c415b" stroke-width="1"/><text x="740" y="209" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">Fenêtre, logs pare-feu</text><text x="740" y="225" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">autorisation du scan</text><rect x="25" y="242" width="190" height="48" rx="6" fill="#111c30" stroke="#2c415b" stroke-width="1"/><text x="120" y="270" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="700" fill="#f4f8ff">Exfiltration possible</text><rect x="225" y="242" width="310" height="48" rx="6" fill="#111c30" stroke="#2c415b" stroke-width="1"/><text x="380" y="262" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">Volume sortant soutenu</text><text x="380" y="278" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">destination inhabituelle</text><rect x="545" y="242" width="390" height="48" rx="6" fill="#111c30" stroke="#2c415b" stroke-width="1"/><text x="740" y="262" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">DNS / proxy / endpoint</text><text x="740" y="278" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">baseline + propriétaire</text><rect x="25" y="295" width="190" height="48" rx="6" fill="#0f1929" stroke="#2c415b" stroke-width="1"/><text x="120" y="323" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="700" fill="#f4f8ff">Top talker légitime</text><rect x="225" y="295" width="310" height="48" rx="6" fill="#0f1929" stroke="#2c415b" stroke-width="1"/><text x="380" y="315" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">Volume élevé sur une</text><text x="380" y="331" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">plage habituelle</text><rect x="545" y="295" width="390" height="48" rx="6" fill="#0f1929" stroke="#2c415b" stroke-width="1"/><text x="740" y="315" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">Calendrier des jobs</text><text x="740" y="331" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">propriétaire applicatif</text><text x="480" y="362" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="600" fill="#fbbf24">NetFlow décrit des motifs de trafic ; il ne démontre pas à lui seul une compromission.</text></svg>

### 9.1 Détection DDoS et floods

Un motif possible est une augmentation rapide des paquets ou octets vers une destination, l’apparition de nombreuses sources, ou l’augmentation anormale d’un protocole. Les indicateurs doivent être définis selon le type d’attaque recherché. Un volume élevé peut aussi correspondre à une diffusion vidéo ou une sauvegarde prévue. Les compteurs de débit, de paquets par seconde, les drops et les politiques de mitigation apportent un contexte nécessaire.

NetFlow échantillonné ou très agrégé peut être insuffisant pour caractériser certains floods de très courte durée. Sur un événement critique, complète l’analyse avec la télémétrie du fournisseur, les compteurs par ASIC, les statistiques de file ou les outils de mitigation disponibles.

### 9.2 Scan, balayage et reconnaissance

Un hôte qui communique avec un grand nombre de destinations ou de ports peut signaler une activité de scan. Il faut regarder la fenêtre temporelle, la répartition des ports, les réponses et le contexte de l’hôte. Des scanners légitimes, outils d’inventaire, supervision ou scanners de vulnérabilités peuvent produire un motif similaire. Les conclusions doivent intégrer l’autorisation et le propriétaire de l’actif.

### 9.3 Exfiltration et flux sortants inhabituels

Un grand volume sortant vers une destination rare, une augmentation sur une plage horaire atypique ou une connexion longue peut justifier une investigation. Le volume seul n’identifie ni le contenu ni la légitimité. Les journaux DNS, proxy, endpoint, DLP ou applicatifs peuvent être requis pour comprendre la destination et la nature des données transférées.

### 9.4 Baselines robustes

Une baseline devrait tenir compte des périodes de pointe, des jours ouvrés, des sauvegardes, des batchs, des changements d’application et des événements saisonniers. Une simple moyenne peut être dominée par quelques gros transferts. Selon le besoin, utilise des percentiles, des médianes par créneau, des fenêtres comparables ou des seuils distincts par groupe d’actifs. Documente le volume habituel, la marge tolérée et le propriétaire de l’alerte.

### 9.5 Réduire les faux positifs

- Enrichir les adresses avec l’inventaire, le rôle, le site, la VRF et le propriétaire lorsque cela est disponible.
- Distinguer nouvelles destinations, nouveaux ports, pics de volume et répétitions périodiques.
- Utiliser plusieurs signaux indépendants avant une escalade sévère.
- Maintenir des exceptions documentées avec une date d’expiration, plutôt que des exclusions permanentes sans propriétaire.
- Séparer « suspicion », « anomalie confirmée » et « incident confirmé » dans les tableaux de bord.


## 10. Dimensionnement du transport, de l’ingestion et du stockage

Le dimensionnement d’une chaîne NetFlow doit commencer par le taux d’enregistrements et la taille des enregistrements, mais il ne s’arrête pas à cette multiplication. La taille réelle dépend du format d’export, des templates, des champs, des encapsulations de transport et du regroupement des records dans les messages. Les besoins de stockage dépendent aussi de l’indexation, de la compression, du nombre de dimensions et de la rétention.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-9-title nfexp-9-desc"><title id="nfexp-9-title">Dimensionner le transport et le stockage des flux</title><desc id="nfexp-9-desc">Formule simple de premier ordre pour estimer le volume brut avant index et réplication.</desc><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">Dimensionner le transport et le stockage des flux</text><rect x="32" y="90" width="266" height="122" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="165.0" y="116" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Débit de records</text><text x="165.0" y="142" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">R = records / seconde</text><text x="165.0" y="165" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">mesuré au pic</text><rect x="347" y="90" width="266" height="122" rx="12" fill="#332817" stroke="#fbbf24" stroke-width="2"/><text x="480.0" y="116" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Taille utile moyenne</text><text x="480.0" y="142" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">S = octets / record</text><text x="480.0" y="165" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">template + champs</text><rect x="662" y="90" width="266" height="122" rx="12" fill="#193628" stroke="#4ade80" stroke-width="2"/><text x="795.0" y="116" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Volume brut journalier</text><text x="795.0" y="142" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">R × S × 86 400</text><text x="795.0" y="165" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">puis surcharge stockage</text><text x="480" y="247" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15px" font-weight="700" fill="#f4f8ff">Exemple illustratif : 25 000 records/s × 72 octets × 86 400 s ≈ 155,5 Go/jour bruts.</text><text x="480" y="277" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="400" fill="#c3d2e5">Les index, métadonnées, réplication et marges de pointe augmentent la capacité nécessaire.</text><rect x="105" y="307" width="750" height="42" rx="8" fill="#3a202a" stroke="#fb7185" stroke-width="1"/><text x="480" y="333" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="600" fill="#f4f8ff">Dimensionner sur les pics et les pertes acceptables, pas uniquement sur la moyenne quotidienne.</text></svg>

### 10.1 Formule de premier ordre

Soit :

- `R` = débit moyen de records en enregistrements/seconde ;
- `S` = taille utile moyenne retenue pour un record en octets ;
- `T` = nombre de secondes sur la période ;
- `K` = facteur d’overhead et de stockage propre à la solution.

Une estimation brute simplifiée est :

```text
Volume brut (octets) ≈ R × S × T
Volume stocké estimé ≈ R × S × T × K
```

`K` n’est pas une constante universelle : il doit être obtenu par mesure sur le collecteur réel, selon les index, la compression, le schéma de stockage, les métadonnées et la réplication. Utilise les unités décimales ou binaires de manière cohérente.

### 10.2 Exemple numérique

Avec 25 000 records/s, une taille utile moyenne illustrative de 72 octets et 86 400 secondes par jour :

```text
25 000 × 72 × 86 400 = 155 520 000 000 octets ≈ 155,5 Go/jour (décimal)
```

Ce résultat est un ordre de grandeur brut, pas un devis d’infrastructure. Les messages, le transport, le stockage indexé, les réplications et les variations de pointe changent le besoin réel. Il faut mesurer la taille à l’entrée du collecteur puis le facteur de croissance après ingestion.

### 10.3 Dimensionner sur les pointes

Une moyenne faible peut masquer des pointes qui épuisent les files, la CPU ou le disque. Mesure la distribution de `records/s`, le débit réseau, les templates/s, le temps de parsing, le retard de file, les rejets et l’espace de stockage. Teste au moins un scénario de pointe, un redémarrage d’exportateur et un redémarrage du collecteur.

### 10.4 Rétention et résolution

Conserver tous les records détaillés pendant plusieurs mois peut être disproportionné. Une approche possible est : détail court terme, agrégats à résolution moyenne pour le long terme, et rétention spécifique des événements de sécurité selon la politique de l’organisation. Les règles de rétention doivent suivre les besoins opérationnels, les obligations applicables et la gouvernance de données.


## 11. Collecteur résilient et gouvernance des données

Un collecteur robuste n’est pas simplement une VM qui écoute sur un port UDP. Il a besoin de capacité suffisante, de files d’ingestion, d’une gestion de l’état des templates, de contrôles de qualité, de supervision et d’un comportement défini lors d’une panne. Une architecture peut inclure plusieurs collecteurs, un broker ou une file persistante, un stockage analytique et un SIEM, mais les mécanismes de redondance doivent être validés avec les fonctionnalités de l’exportateur.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-10-title nfexp-10-desc"><title id="nfexp-10-title">Collecte résiliente : réception ne suffit pas</title><desc id="nfexp-10-desc">Architecture logique illustrative à adapter aux capacités effectives des exportateurs, collecteurs et transports.</desc><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">Collecte résiliente : réception ne suffit pas</text><rect x="28" y="95" width="200" height="116" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="128.0" y="121" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Exportateurs A–N</text><text x="128.0" y="147" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">sites / VRF</text><text x="128.0" y="170" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">templates surveillés</text><rect x="280" y="70" width="190" height="78" rx="12" fill="#193628" stroke="#4ade80" stroke-width="2"/><text x="375.0" y="96" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Collecteur A</text><text x="375.0" y="122" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">ingestion / decode</text><rect x="280" y="168" width="190" height="78" rx="12" fill="#193628" stroke="#4ade80" stroke-width="2"/><text x="375.0" y="194" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Collecteur B</text><text x="375.0" y="220" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">ingestion / decode</text><rect x="530" y="95" width="175" height="116" rx="12" fill="#332817" stroke="#fbbf24" stroke-width="2"/><text x="617.5" y="121" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Broker / buffer</text><text x="617.5" y="147" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">si architecture</text><text x="617.5" y="170" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">le prévoit</text><rect x="755" y="95" width="175" height="116" rx="12" fill="#292642" stroke="#a78bfa" stroke-width="2"/><text x="842.5" y="121" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Stockage + SIEM</text><text x="842.5" y="147" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">rétention</text><text x="842.5" y="170" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="400" fill="#c3d2e5">requêtes / alertes</text><line x1="228" y1="125" x2="272.3537679302244" y2="111.35268679070019" stroke="#38bdf8" stroke-width="2.5"/><polygon points="280,109 273.64774566510954,115.55811442907677 271.0597901953393,107.14725915232361" fill="#38bdf8"/><line x1="228" y1="180" x2="272.9562312006226" y2="204.20720141571985" stroke="#38bdf8" stroke-width="2.5"/><polygon points="280,208 270.8701919792685,208.08127425537742 275.0422704219767,200.33312857606228" fill="#38bdf8"/><line x1="470" y1="109" x2="522.27012048319" y2="122.93869879551734" stroke="#4ade80" stroke-width="2.5"/><polygon points="530,125 521.1364048207246,127.19013252976282 523.4038361456554,118.68726506127186" fill="#4ade80"/><line x1="470" y1="207" x2="522.7046279585992" y2="183.28291741863038" stroke="#4ade80" stroke-width="2.5"/><polygon points="530,180 524.5102325388459,187.29537204140084 520.8990233783525,179.2704627958599" fill="#4ade80"/><line x1="705" y1="153" x2="747.0" y2="153.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="755,153 747.0,157.4 747.0,148.6" fill="#9fb5d0"/><rect x="65" y="275" width="830" height="66" rx="12" fill="#111c30" stroke="#334a66" stroke-width="2"/><text x="480" y="301" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="700" fill="#f4f8ff">La haute disponibilité doit préserver le décodage, pas seulement la réception UDP.</text><text x="480" y="325" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="400" fill="#c3d2e5">Vérifier sessions, templates, Observation Domain ID, duplication et comportement au failover.</text></svg>

### 11.1 Où mesurer la disponibilité

Surveille séparément :

- le transport jusqu’au collecteur (connectivité et ACL/firewall) ;
- les paquets et messages reçus par collecteur ;
- le taux de templates reconnus et de Data Records décodés ;
- le débit de records rejetés ou mal formés ;
- la profondeur et l’âge de la file d’ingestion ;
- le délai entre export et requêtage ;
- la capacité de disque et la rétention restante ;
- la couverture par exportateur, interface et domaine d’observation.

Un test synthétique peut envoyer un flux contrôlé dont le record attendu est connu, puis vérifier que celui-ci apparaît correctement dans l’outil. Ce test doit être identifié comme trafic de test afin de ne pas polluer les métriques métier.

### 11.2 Sécurité de la collecte

La télémétrie peut révéler des top talkers, des habitudes de communication, des adresses internes et des relations entre systèmes. Il faut contrôler les accès, protéger le transport lorsque c’est possible, limiter l’exposition réseau du collecteur, sécuriser les secrets de configuration et définir les durées de rétention. IPFIX n’est pas automatiquement sécurisé simplement parce qu’il est standardisé ; les propriétés de sécurité dépendent du transport, de l’environnement et des mécanismes activés.

### 11.3 Haute disponibilité et bascule

Il faut savoir si l’exportateur sait envoyer vers plusieurs destinations, comment le collecteur gère les templates après une bascule, ce qu’il se passe si l’état de session change et si les données manquées peuvent être récupérées. Une architecture de redondance qui reçoit des paquets mais ne décode pas les templates n’offre pas une haute disponibilité utile. Teste les pannes réelles, pas uniquement un ping vers le serveur.


## 12. Runbook expert de dépannage

Une investigation reproductible commence par classer le symptôme : absence complète, absence partielle, records retardés, compteurs incohérents ou alertes erronées. Il faut ensuite remonter de l’observation vers l’analyse, en évitant de modifier plusieurs couches simultanément.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="nfexp-11-title nfexp-11-desc"><title id="nfexp-11-title">Arbre de décision de dépannage</title><desc id="nfexp-11-desc">Diagnostic séquentiel : isoler la mesure, le cache, l’export, le décodage et enfin l’analyse.</desc><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1220" stroke="#2b415d" stroke-width="2"/><text x="480" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21px" font-weight="700" fill="#f4f8ff">Arbre de décision de dépannage</text><rect x="310" y="68" width="340" height="62" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="480.0" y="94" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16px" font-weight="700" fill="#f4f8ff">Symptôme défini ?</text><text x="480.0" y="120" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12px" font-weight="400" fill="#c3d2e5">Flux absents, incomplets, retardés ou incohérents</text><line x1="480" y1="130" x2="480.0" y2="150.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="480,158 475.6,150.0 484.4,150.0" fill="#9fb5d0"/><rect x="255" y="158" width="450" height="56" rx="12" fill="#1b2b3a" stroke="#60a5fa" stroke-width="2"/><text x="480" y="182" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="700" fill="#f4f8ff">1. L’interface observe-t-elle le bon trafic ?</text><text x="480" y="201" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">Direction · ACL · VRF · NAT · capacités de la plateforme</text><line x1="480" y1="214" x2="480.0" y2="230.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="480,238 475.6,230.0 484.4,230.0" fill="#9fb5d0"/><rect x="255" y="238" width="450" height="56" rx="12" fill="#1b2b3a" stroke="#60a5fa" stroke-width="2"/><text x="480" y="262" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14px" font-weight="700" fill="#f4f8ff">2. Le cache se remplit-il et vieillit-il ?</text><text x="480" y="281" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">Record · clés · timeouts · drops / ressources</text><line x1="480" y1="294" x2="480.0" y2="310.0" stroke="#9fb5d0" stroke-width="2.5"/><polygon points="480,318 475.6,310.0 484.4,310.0" fill="#9fb5d0"/><rect x="255" y="318" width="450" height="56" rx="12" fill="#193628" stroke="#4ade80" stroke-width="2"/><text x="480" y="342" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13px" font-weight="700" fill="#f4f8ff">3. Export, templates et collecteur sont-ils cohérents ?</text><text x="480" y="361" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11px" font-weight="400" fill="#c3d2e5">Compteurs exporter · transport · version · parser · stockage</text></svg>

### 12.1 Flux totalement absents

1. Générer un trafic de test connu.
2. Confirmer que l’interface et la direction attachées au monitor correspondent au chemin utilisé.
3. Vérifier le record et le monitor appliqués, ainsi que les restrictions de plateforme.
4. Vérifier si le cache reçoit des entrées et si elles expirent.
5. Vérifier l’adresse source, la destination, le port, le routage, les ACL et le pare-feu du collecteur.
6. Vérifier le format d’export et le support du collecteur.
7. Vérifier les templates et les statistiques de décodage.

### 12.2 Flux présents mais volumes faux

- Vérifier les unités, les compteurs et l’éventuelle différence entre bytes de couche 2 et couche 3 selon la sémantique du champ.
- Vérifier le sampling et si l’outil applique déjà une extrapolation.
- Vérifier les points d’observation multiples et le double comptage.
- Vérifier le NAT, les VRF, les chemins asymétriques et la direction.
- Vérifier les horodatages, les agrégations et les changements de template.
- Comparer à un compteur indépendant sur la même interface et la même période, en tenant compte des différences de définition.

### 12.3 Retard d’export ou d’analyse

Sépare le temps passé dans le cache, le transport, la file d’ingestion, le parsing et la requête analytique. Vérifie les timeouts, les records/s au pic, les pertes de datagrammes, la CPU, la mémoire, la profondeur de file et les index. Réduire les timeouts au hasard peut aggraver la charge au lieu de corriger la cause.

### 12.4 Détecteur bruyant ou manquant des événements

Vérifie la baseline, la fréquence et la durée de mesure, les seuils, le sampling, les champs manquants, le point de mesure et le comportement du collecteur. Utilise un événement synthétique connu pour valider la chaîne. Modifie une règle à la fois puis compare précision, délai de détection et faux positifs.


## 13. Laboratoire de synthèse : déployer, mesurer, tester, observer

> **Environnement recommandé :** trois routeurs/instances compatibles IOS XE, deux réseaux utilisateurs, une destination de supervision et un collecteur NetFlow/IPFIX. Les adresses `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24` sont réservées à la documentation et doivent être remplacées par le plan d’adressage du laboratoire.

### 13.1 Topologie logique

```text
LAN-A ---- R1 (Edge / IP SLA + NetFlow) ---- R2 (cœur) ---- R3 / LAN-B
                       |
                       +---- réseau de management ---- Collecteur
                       |
                       +---- sonde IP SLA vers une cible contrôlée
```

Le but n’est pas seulement de faire apparaître des records : le laboratoire doit permettre de vérifier chaque étage et de documenter la baseline avant et après activation.

### 13.2 Exemple Flexible NetFlow sur IOS XE

L’exemple suivant illustre un record IPv4 simple, un exporter NetFlow v9 et un monitor. Il doit être adapté à la syntaxe et aux capacités exactes de la plateforme ; certains matériels n’acceptent pas tous les champs, timers ou directions.

```text
flow record NF-EXPERT-IPV4
 description IPv4 source-destination-port-protocol
 match ipv4 source address
 match ipv4 destination address
 match transport source-port
 match transport destination-port
 match ipv4 protocol
 collect counter bytes
 collect counter packets
 collect timestamp sys-uptime first
 collect timestamp sys-uptime last
!
flow exporter NF-EXPERT-EXPORT
 description Export vers le collecteur du laboratoire
 destination 192.0.2.50
 source Loopback0
 transport udp 2055
 export-protocol netflow-v9
!
flow monitor NF-EXPERT-MONITOR
 description Observation IPv4 pilote
 record NF-EXPERT-IPV4
 exporter NF-EXPERT-EXPORT
 cache timeout active 60
 cache timeout inactive 15
!
interface GigabitEthernet0/0
 ip flow monitor NF-EXPERT-MONITOR input
```

**Points à vérifier avant collage :** le nom réel de l’interface, la disponibilité des champs `timestamp`, le support de NetFlow v9, l’existence et le routage de `Loopback0`, la reachability de `192.0.2.50`, les ACL, la syntaxe de commande et la charge attendue. N’applique pas un monitor sur toutes les interfaces en une seule étape.

### 13.3 Exemple IP SLA et tracking

```text
ip sla 100
 icmp-echo 198.51.100.10 source-interface Loopback0
 timeout 1000
 threshold 200
 frequency 10
ip sla schedule 100 life forever start-time now
!
track 100 ip sla 100 reachability
 delay down 15 up 30
```

Cet exemple illustre une sonde ICMP et un tracking de reachability sur les versions qui supportent cette syntaxe. Le seuil de délai ne doit pas être confondu avec l’état de reachability. Si l’application est HTTP, DNS ou autre, sélectionne un type de sonde réellement pris en charge et pertinent pour elle. La temporisation de tracking doit être choisie en fonction du temps de rétablissement acceptable et du risque de bascule intempestive.

### 13.4 Vérification graduelle

Les commandes suivantes sont courantes dans les environnements Cisco IOS XE, mais les détails dépendent de la plateforme :

```text
show flow record NF-EXPERT-IPV4
show flow exporter NF-EXPERT-EXPORT
show flow monitor NF-EXPERT-MONITOR
show flow monitor NF-EXPERT-MONITOR cache
show flow interface
show ip sla configuration 100
show ip sla statistics 100
show track 100
show interfaces counters errors
```

Pour chaque commande, consigne le résultat attendu, le résultat réel et ce que cette donnée ne prouve pas. Le cache démontre que l’équipement a construit des entrées ; il ne prouve pas à lui seul que le collecteur a reçu et décodé chaque enregistrement.

### 13.5 Scénarios à provoquer

1. Trafic normal entre LAN-A et LAN-B.
2. Génération contrôlée d’un grand volume vers une destination connue.
3. Arrêt du service de collecte ou blocage temporaire du port d’export, dans un environnement isolé.
4. Redémarrage contrôlé du collecteur pour tester le comportement des templates et des files.
5. Perte de reachability de la cible IP SLA, puis rétablissement.
6. Changement de direction ou déplacement du point d’observation afin de démontrer les limites de comparaison.
7. Répétition avec sampling activé, si la plateforme le permet, pour observer les différences de couverture.

Après chaque scénario, note la chronologie, les compteurs, les journaux, le résultat NetFlow, l’état IP SLA et l’hypothèse retenue.


## 14. Études de cas corrigées

### Cas A — Le collecteur reçoit des datagrammes, mais aucune ligne n’apparaît

**Faits :** le port UDP reçoit du trafic ; le tableau de bord reste vide ; les interfaces du routeur acheminent normalement les paquets.

**Hypothèses à ordonner :** template absent ou non rafraîchi, mauvais format/version, mauvais Observation Domain ID, parser incompatible, records invalides ou pipeline d’ingestion bloqué. La première action utile consiste à comparer les statistiques de messages reçus et de records décodés, puis à vérifier les templates. Il serait prématuré de conclure à une panne du trafic utilisateur.

### Cas B — Les octets NetFlow sont très inférieurs au compteur d’interface

**Faits :** le compteur d’interface augmente fortement ; NetFlow indique un volume réduit.

**Analyse :** le sampling est-il activé ? Tous les champs et toutes les directions sont-ils exportés ? Le monitor observe-t-il le bon trafic ? Les compteurs de l’interface et du flux couvrent-ils le même périmètre et la même période ? Les unités et les politiques d’agrégation sont-elles identiques ? La différence de couche mesurée peut contribuer à l’écart mais doit être démontrée, pas supposée.

**Correction :** aligner la fenêtre et le point de mesure, documenter le sampling et vérifier la configuration du monitor avant toute extrapolation.

### Cas C — IP SLA indique un délai élevé alors que NetFlow ne montre pas de pic

**Faits :** la latence augmente ; les volumes vus par le collecteur semblent stables.

**Analyse :** les flux sont-ils correctement collectés sur le chemin réel de la sonde ? Le problème peut se trouver dans un chemin différent, dans une file QoS, dans les erreurs de lien, dans le traitement distant ou dans une cible qui répond lentement. Une absence de pic NetFlow n’exclut pas la congestion si les records sont échantillonnés ou agrégés.

**Correction :** corréler l’horodatage, lire les compteurs d’interface et de file, vérifier le routage et lancer une mesure indépendante. Ne pas déclarer que NetFlow « contredit » IP SLA avant d’avoir aligné les points observés.

### Cas D — La collecte devient lente après l’ajout de nouveaux champs

**Faits :** les dashboards ont davantage de dimensions ; le nombre d’entrées et la charge de stockage augmentent.

**Analyse :** les nouvelles clés ont-elles augmenté la cardinalité ? Les champs auraient-ils pu rester non-key ? Le volume de records/s et la taille du schéma ont-ils été mesurés ?

**Correction :** séparer les usages, tester les nouveaux records sur un périmètre pilote, comparer le débit et la cardinalité, réduire les champs inutiles et ajuster la rétention. Il faut mesurer le gain analytique obtenu par rapport au coût.

### Cas E — Après bascule de collecteur, les enregistrements sont mal interprétés

**Faits :** des messages sont reçus par le second collecteur, mais les valeurs semblent incohérentes après la bascule.

**Analyse :** le collecteur a-t-il restauré un template provenant d’une session distincte ? L’Observation Domain ID et les identifiants de templates ont-ils été interprétés dans le bon contexte ? L’exportateur a-t-il redémarré ou réinitialisé ses templates ?

**Correction :** suivre les recommandations du protocole et du collecteur, rétablir un état de template valide, inspecter les logs de décodage et tester le scénario à nouveau. Ne pas réutiliser aveuglément des templates mis en cache sans tenir compte des règles de session du protocole.


## 15. Quiz expert avec corrigé

### Questions

1. Pourquoi un record qui ajoute l’interface à la clé peut-il augmenter fortement la cardinalité ?
2. Pourquoi l’absence de flux dans le collecteur ne prouve-t-elle pas l’absence de trafic ?
3. Quel est le rôle d’un template en IPFIX ou NetFlow v9 ?
4. Pourquoi la perte d’un template peut-elle empêcher le décodage de données pourtant reçues ?
5. Le Sequence Number IPFIX est-il un compteur de paquets utilisateurs ?
6. Dans quelles circonstances deux points d’observation peuvent-ils compter le même trafic ?
7. Pourquoi une fraction de sampling doit-elle être conservée comme métadonnée ?
8. Que faut-il aligner pour corréler IP SLA et NetFlow ?
9. Quelle est la différence entre timeout d’IP SLA et état de reachability ?
10. Pourquoi un grand volume sortant ne prouve-t-il pas une exfiltration ?
11. Quelles données faut-il regarder si les datagrammes arrivent mais que les records décodés sont nuls ?
12. Pourquoi faut-il tester un record détaillé sur une interface pilote ?
13. Que doit mesurer un test de résilience de collecteur ?
14. Donne deux causes possibles d’écart entre compteurs interface et NetFlow.
15. Quel intérêt a un record spécifique à la sécurité plutôt qu’un record universel ?

### Corrigé

1. L’interface devient une dimension supplémentaire de la clé ; des paquets autrement agrégés dans un seul flux peuvent appartenir à plusieurs entrées.
2. Le problème peut se trouver dans l’observation, le cache, l’expiration, l’export, le transport, le template, le parsing ou l’ingestion.
3. Il décrit les champs et leurs longueurs dans les records exportés afin que le collecteur sache décoder les Data Sets.
4. Sans un template valide dans le contexte attendu, la séquence d’octets ne peut pas être interprétée de manière fiable comme les champs attendus.
5. Non. Dans IPFIX, il compte les Data Records envoyés dans le domaine d’observation pertinent au sein de la session, selon la spécification.
6. Si l’entrée et la sortie d’un routeur mesurent le même paquet, ou si des chemins alternatifs sont additionnés sans identifier la population représentée.
7. Pour expliquer les biais, les estimations et les changements de méthode, et pour éviter de comparer des données produites selon des fractions différentes sans correction.
8. Les horodatages, le point d’observation, la direction, la cible, le chemin logique, la VRF et la fenêtre d’agrégation.
9. Le timeout limite l’attente d’une opération ; l’état de reachability reflète sa réussite/joignabilité selon les règles de la plateforme.
10. Il peut s’agir d’une sauvegarde ou d’une activité légitime. Le volume est un signal à contextualiser avec des sources complémentaires.
11. Les templates, le format/version, le contexte d’observation, les erreurs de décodage, les rejets et la compatibilité des éléments d’information.
12. Pour mesurer la cardinalité, l’usage des ressources, les débits de records et l’effet sur le forwarding avant de déployer largement.
13. Le comportement pendant panne/reprise, l’état des templates, les files, le délai de décodage, la perte et la continuité des données.
14. Sampling, observation à des points différents, direction, double comptage, périmètre de couche, agrégation, perte d’export ou mauvaise interprétation du champ.
15. Il adapte les clés et champs à un usage précis, limite les coûts inutiles et permet de définir une durée/politique de collecte adaptée.


## 16. Checklist de mise en production

### Conception

- [ ] Le cas d’usage et les questions auxquelles la mesure doit répondre sont écrits.
- [ ] Le point d’observation et la direction sont documentés.
- [ ] Les clés et champs collectés sont justifiés par un cas d’usage.
- [ ] La cardinalité attendue est estimée et vérifiée sur une charge représentative.
- [ ] Les effets du NAT, des VRF, de l’ECMP et des chemins asymétriques sont compris.

### Export et décodage

- [ ] Format et version supportés sont documentés.
- [ ] Le transport, la destination, la source et les ACL sont testés.
- [ ] Templates, sessions, observation domains et compteurs sont surveillés.
- [ ] Les redémarrages et bascules ont été testés.
- [ ] Le système distingue messages reçus, records décodés, records rejetés et records analysés.

### IP SLA

- [ ] Le type de sonde mesure réellement le chemin ou service voulu.
- [ ] Source, cible, fréquence, timeout et seuil sont documentés.
- [ ] Le tracking a des temporisations de transition justifiées.
- [ ] Les cas de faux positifs et les conditions de rétablissement sont testés.

### Capacité, sécurité et exploitation

- [ ] Débit de pointe, taille moyenne, stockage brut et stockage indexé ont été mesurés.
- [ ] La rétention et l’accès suivent les règles de gouvernance.
- [ ] Le sampling est explicitement documenté lorsqu’il est utilisé.
- [ ] Une procédure de dépannage couvre observation, cache, export, template et collecteur.
- [ ] Une procédure de désactivation et de retour arrière a été testée.
- [ ] Les exemples de configuration sont adaptés à la version et à la gamme réelles.


## 17. Références techniques

Les liens ci-dessous sont des références de protocole ou de configuration. Ils doivent être consultés en parallèle avec la documentation de la version et du modèle d’équipement réellement déployé.

1. **IETF RFC 7011 — Specification of the IP Flow Information Export (IPFIX) Protocol** : https://www.rfc-editor.org/rfc/rfc7011.html
2. **IETF RFC 5475 — Sampling and Filtering Techniques for IP Packet Selection** : https://www.rfc-editor.org/rfc/rfc5475.html
3. **Cisco IOS XE 17.x — Flexible NetFlow Overview** : https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ntw-servs/b-network-services/m_fnf-fnetflow.html
4. **Cisco IOS XE 17.x — Flexible NetFlow Output Features on Data Export** : https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ntw-servs/b-network-services/m_fnf-output-features.html
5. **Cisco IOS XE — Enhanced Object Tracking** : https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-addressing/ip-addressing/m_iap-eot-xe.html


## Conclusion

À un niveau expert, la qualité de la télémétrie vient moins du nombre de champs exportés que de la précision du contrat de mesure et de la validation de toute la chaîne. Un record doit être compréhensible, le cache dimensionné, l’export décodable, la collecte observable, l’analyse contextualisée et les alertes testées. IP SLA indique ce qu’une opération de mesure a constaté ; NetFlow décrit les flux selon les champs et le point d’observation ; les compteurs d’interface, les logs et les tests indépendants permettent de transformer ces signaux en hypothèse vérifiable.

**Principe final : ne conclure qu’à partir des limites connues de chaque mesure et d’au moins une vérification indépendante quand l’impact opérationnel est important.**
