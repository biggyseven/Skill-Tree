# Architecture Spine/Leaf — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Prérequis :** bases Ethernet, adressage IPv4, sous-réseaux, routage IP et notions de VLAN.  
**Objectif :** concevoir, dimensionner, configurer conceptuellement et dépanner une fabric Spine/Leaf routée en comprenant le rôle du underlay, d’ECMP, du routage dynamique, de la redondance et des overlays.

> **Périmètre.** Ce cours est orienté conception et exploitation. Les extraits de configuration sont volontairement génériques ou illustratifs : la syntaxe exacte varie selon le constructeur, le système d’exploitation réseau et la version. Valide toujours les commandes sur la documentation de la plateforme utilisée avant de les appliquer en production.

## 1. Ce qui change au niveau intermédiaire

Au niveau débutant, l’objectif est de reconnaître les Leaf, les Spine et les liens entre eux, puis de comprendre qu’un paquet entre deux Leaf traverse normalement un Spine. Au niveau intermédiaire, cette image physique ne suffit plus. Il faut répondre à des questions opérationnelles :

- Comment les Leaf et les Spine apprennent-ils les routes nécessaires ?
- Comment plusieurs chemins de coût égal sont-ils installés et utilisés ?
- Que se passe-t-il après la panne d’un lien, d’un port ou d’un Spine ?
- Comment mesurer la capacité, le surabonnement, la perte de paquets et la latence ?
- Comment transporter plusieurs réseaux logiques au-dessus d’un réseau IP ?
- Comment faire évoluer la fabric sans introduire de panne globale ?

Une topologie Spine/Leaf n’impose pas à elle seule un protocole de routage, un plan d’adressage ni un modèle d’overlay. On peut utiliser OSPF ou IS-IS comme IGP, ou BGP dans une fabric routée. Une fabric peut fonctionner sans VXLAN, tandis qu’une architecture avec VXLAN utilise généralement un réseau IP sous-jacent pour relier les points de terminaison des tunnels. Le choix doit suivre les exigences et les compétences d’exploitation, pas une mode technologique.

## 2. Anatomie d’une fabric routée

### 2.1 Séparer les rôles physiques et logiques

Les **Leaf** raccordent les serveurs, les hyperviseurs, le stockage et les appliances. Ils exécutent généralement les passerelles des réseaux de serveurs dans une architecture routée de couche 3. Les **Spine** acheminent le trafic entre Leaf et évitent de devenir des switches d’accès aux serveurs. Le **underlay** est le réseau IP qui assure la connectivité entre les équipements de la fabric. Si un overlay est présent, il s’appuie sur ce underlay.

La fabric routée emploie habituellement des liens point-à-point de couche 3 entre chaque Leaf et chaque Spine. Chaque lien possède son propre sous-réseau, souvent très petit, par exemple un /31 en IPv4 lorsque les équipements le prennent en charge. Les adresses de loopback servent souvent d’identifiants stables pour le routage et les sessions de contrôle, notamment BGP.

### 2.2 Exemple d’architecture et de chemin de contrôle

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 440" role="img" aria-label="Fabric routée avec deux Spine et trois Leaf ; chaque liaison Leaf-Spine est un lien IP point à point" width="100%" height="auto"><defs><marker id="si1Arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#66d9ff"/></marker></defs><style>.si1box{stroke-width:2;rx:11}.si1t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.si1s{font:12px system-ui,sans-serif;fill:#b6c4d7;text-anchor:middle}.si1link{fill:none;stroke:#66d9ff;stroke-width:2.7;stroke-dasharray:7 6;marker-end:url(#si1Arrow);animation:si1dash 2.5s linear infinite}@keyframes si1dash{to{stroke-dashoffset:-26}}@media(prefers-reduced-motion:reduce){.si1link{animation:none}}</style><rect x="32" y="18" width="836" height="150" rx="16" fill="#101b2a" stroke="#344d69" stroke-dasharray="5 5"/><text x="450" y="40" class="si1s">Plan de transit — adresses de liens et routes underlay</text><rect class="si1box" x="205" y="61" width="180" height="68" fill="#173c5b" stroke="#66d9ff"/><text x="295" y="88" class="si1t">SPINE 1</text><text x="295" y="108" class="si1s">Loopback S1</text><rect class="si1box" x="515" y="61" width="180" height="68" fill="#173c5b" stroke="#66d9ff"/><text x="605" y="88" class="si1t">SPINE 2</text><text x="605" y="108" class="si1s">Loopback S2</text><rect x="32" y="190" width="836" height="122" rx="16" fill="#101e1a" stroke="#2c684b" stroke-dasharray="5 5"/><g class="si1link"><path d="M295 129 L120 212" marker-end="url(#si1Arrow)"/><path d="M295 129 L410 212" marker-end="url(#si1Arrow)"/><path d="M295 129 L720 212" marker-end="url(#si1Arrow)"/><path d="M605 129 L180 212" marker-end="url(#si1Arrow)"/><path d="M605 129 L490 212" marker-end="url(#si1Arrow)"/><path d="M605 129 L780 212" marker-end="url(#si1Arrow)"/></g><g><rect class="si1box" x="75" y="225" width="150" height="59" fill="#183b2c" stroke="#80e3ac"/><text x="150" y="250" class="si1t">LEAF 1</text><text x="150" y="269" class="si1s">Lo1 · GW A</text><rect class="si1box" x="375" y="225" width="150" height="59" fill="#183b2c" stroke="#80e3ac"/><text x="450" y="250" class="si1t">LEAF 2</text><text x="450" y="269" class="si1s">Lo2 · GW B</text><rect class="si1box" x="675" y="225" width="150" height="59" fill="#183b2c" stroke="#80e3ac"/><text x="750" y="250" class="si1t">LEAF 3</text><text x="750" y="269" class="si1s">Lo3 · GW C</text></g><g stroke="#80e3ac" fill="none" stroke-width="2.2"><path d="M150 284 V340"/><path d="M450 284 V340"/><path d="M750 284 V340"/></g><g fill="#202b3b" stroke="#80e3ac" stroke-width="1.5"><rect x="82" y="340" width="136" height="42" rx="7"/><rect x="382" y="340" width="136" height="42" rx="7"/><rect x="682" y="340" width="136" height="42" rx="7"/></g><g class="si1t"><text x="150" y="366">SERVEURS A</text><text x="450" y="366">SERVEURS B</text><text x="750" y="366">SERVEURS C</text></g><text x="450" y="410" class="si1s">Les liens Leaf–Spine sont des adjacences IP distinctes ; les chemins sont calculés par le plan de contrôle.</text></svg></div>

Ce modèle illustre six liaisons point-à-point. Les sous-réseaux de ces liaisons ne doivent pas être confondus avec les réseaux de serveurs. Le sous-réseau serveur peut être directement connecté à un Leaf, tandis que le réseau de transit relie les routeurs de la fabric.

### 2.3 Pourquoi favoriser des liens routés ?

Des liens de couche 3 entre Leaf et Spine limitent la propagation des domaines de couche 2 et rendent le comportement des chemins plus explicite. Le protocole de routage construit une table de routes, puis le plan de données utilise la table de transfert pour acheminer les paquets. Une panne de lien peut conduire au retrait d’une adjacence ou d’une route et à l’utilisation d’un autre chemin.

Cela ne signifie pas que la couche 2 disparaît partout. Les ports des serveurs peuvent être des ports d’accès VLAN, des trunks vers des hyperviseurs ou des interfaces routées, selon les besoins. L’idée est de garder une frontière claire entre la connectivité des workloads et le transit de la fabric.

## 3. Concevoir l’underlay

### 3.1 Objectifs de l’underlay

Le underlay doit fournir une connectivité IP stable entre tous les équipements nécessaires au transport. Ses objectifs comprennent :

1. annoncer uniquement les routes nécessaires au fonctionnement de la fabric ;
2. offrir plusieurs chemins valides vers chaque destination pertinente ;
3. converger de façon prévisible après un événement ;
4. permettre l’observabilité et le diagnostic ;
5. rester suffisamment simple pour être automatisé et testé.

Un underlay propre ne doit pas transporter toute la complexité des applications. Les réseaux des workloads, les identifiants de tenants et les politiques peuvent relever de l’overlay ou de la configuration côté Leaf. Un underlay trop complexe rend le dépannage et les changements plus risqués.

### 3.2 Adressage des liens point-à-point

Les préfixes très petits réduisent le gaspillage d’adresses sur les liaisons de transit. En IPv4, on utilise souvent /31 pour une liaison point-à-point selon la prise en charge des équipements ; /30 est une autre possibilité. En IPv6, les conventions et recommandations de déploiement peuvent différer, même si /127 est couramment utilisé pour certains liens point-à-point. Il faut documenter ce choix et vérifier le comportement des équipements.

Exemple conceptuel, à ne pas recopier sans adaptation :

| Lien | Préfixe de transit | Adresse Leaf | Adresse Spine |
|---|---|---|---|
| Leaf-01 ↔ Spine-01 | `10.0.0.0/31` | `10.0.0.0` | `10.0.0.1` |
| Leaf-01 ↔ Spine-02 | `10.0.0.2/31` | `10.0.0.2` | `10.0.0.3` |
| Leaf-02 ↔ Spine-01 | `10.0.0.4/31` | `10.0.0.4` | `10.0.0.5` |
| Leaf-02 ↔ Spine-02 | `10.0.0.6/31` | `10.0.0.6` | `10.0.0.7` |

La table d’adressage doit mentionner le nom des ports, le préfixe, l’adresse locale, le voisin, la vitesse, le type de transceiver, le MTU et l’usage. Une adresse seule, sans correspondance de câblage, ne suffit pas pour exploiter la fabric.

### 3.3 Loopbacks

Une loopback est une interface logique qui reste généralement opérationnelle tant que le système et son logiciel réseau fonctionnent, indépendamment d’un port physique unique. Elle sert souvent d’identifiant stable pour les sessions BGP, le routage ou les terminaisons VXLAN. La route vers une loopback doit être annoncée et atteignable par les chemins de l’underlay.

Une loopback n’est pas un chemin physique de secours à elle seule. Si toutes les routes permettant de joindre cette adresse disparaissent, la loopback peut demeurer « up » localement tout en étant inaccessible depuis le reste de la fabric. Le diagnostic doit distinguer l’état de l’interface logique de l’accessibilité IP de bout en bout.

### 3.4 Plan d’adressage exemple

Un plan évolutif réserve des blocs différents par fonction :

- un bloc pour les liens Leaf–Spine ;
- un bloc pour les loopbacks des Leaf ;
- un bloc pour les loopbacks des Spine ;
- des préfixes séparés pour les interfaces de gestion hors bande ;
- des préfixes dédiés aux workloads ou aux passerelles, gérés selon le modèle choisi.

Éviter d’utiliser le même préfixe sur plusieurs segments distincts. Prévoir suffisamment d’espace pour ajouter des Leaf et des Spine sans renuméroter l’ensemble de la fabric. Les plages de gestion hors bande méritent une séparation physique ou logique et des contrôles d’accès distincts.

## 4. Choisir le protocole de routage

Il n’existe pas une réponse universelle à la question « OSPF ou BGP ? ». Les deux approches peuvent construire une fabric fonctionnelle. Le bon choix dépend de l’échelle, de l’expérience de l’équipe, du support constructeur, des exigences de filtrage des routes et des objectifs d’exploitation.

### 4.1 OSPF ou IS-IS comme IGP

Un IGP (*Interior Gateway Protocol*) comme OSPF ou IS-IS échange les informations de routage à l’intérieur d’un domaine administratif. Il peut calculer plusieurs chemins de coût égal et construire la base des routes underlay.

**Atouts possibles :**
- modèle opérationnel connu par de nombreuses équipes ;
- découverte des voisins et calcul des routes via une base de topologie ;
- intégration avec des pratiques classiques de réseau IP.

**Points d’attention :**
- concevoir les zones et les frontières avec cohérence ;
- contrôler le type de routes annoncées ;
- maîtriser le coût des liens et la convergence ;
- ne pas supposer que toutes les implémentations réagissent de façon identique.

Dans un domaine aussi régulier qu’une fabric, un modèle très simple est souvent plus facile à exploiter qu’une hiérarchie de zones inutilement complexe. Toutefois, la bonne conception dépend du nombre d’équipements, des contraintes de plateforme et des procédures d’exploitation.

### 4.2 BGP comme underlay

BGP est un protocole de routage fondé sur des sessions entre voisins et des attributs de routes. Dans les fabrics de data center, un design fréquemment rencontré utilise eBGP entre les Leaf et les Spine, avec des numéros d’AS choisis selon une convention planifiée. D’autres designs emploient iBGP ou un IGP pour l’underlay. Le guide IETF RFC 7938 décrit l’usage de BGP dans les grands centres de données.

**Atouts possibles :**
- politiques et filtres d’annonces explicites ;
- modèle adapté à des topologies où l’on veut éviter de diffuser une base de topologie IGP complète ;
- relation naturelle entre voisins sur des liens routés ;
- mécanismes utiles pour contrôler les routes et les préférences.

**Points d’attention :**
- planification cohérente des AS et des sessions ;
- filtrage strict des préfixes autorisés ;
- compréhension des règles de sélection, des attributs et des routes de secours ;
- conception correcte de l’ECMP, des loopbacks et éventuellement de BFD ;
- surveillance de l’état des sessions et du nombre de routes.

BGP n’est pas automatiquement plus simple, ni automatiquement plus lent ou plus rapide qu’un IGP dans tous les scénarios. Il faut mesurer le comportement réel et vérifier les fonctions supportées par la plateforme.

### 4.3 Comparaison pratique

| Question | IGP (ex. OSPF/IS-IS) | BGP (ex. eBGP dans la fabric) |
|---|---|---|
| Échange de routes | Base de topologie et calcul SPF selon le protocole | Sessions entre voisins, sélection par attributs et politiques |
| Modèle d’exploitation | Familier aux équipes IGP ; attention aux zones et à la diffusion | Filtrage et politiques détaillés ; attention aux sessions et attributs |
| Chemins multiples | ECMP possible si les routes et coûts sont compatibles | ECMP possible selon les attributs et la configuration |
| Contrôle des annonces | Filtres et politiques selon l’implémentation | Route-maps/policies et filtres de préfixes selon l’implémentation |
| Choix conseillé | Si l’équipe et les outils sont optimisés pour un IGP | Si la fabric est conçue et opérée autour de BGP |

### 4.4 Principes de configuration, pas copier-coller

Pour chaque lien, la configuration conceptuelle devrait comporter :

1. l’interface activée, avec l’adresse de transit et le MTU attendu ;
2. un voisinage de routage vers l’équipement situé à l’autre extrémité ;
3. un identifiant de routeur ou une loopback si requis ;
4. des annonces limitées aux préfixes justifiés ;
5. une politique ECMP cohérente ;
6. une supervision de l’adjacence et des compteurs d’erreur.

Un exemple purement logique d’intention BGP pourrait se lire ainsi :

```text
interface Leaf01-to-Spine01
  address 10.0.0.0/31
  mtu 9216                 # exemple : valeur à adapter et à vérifier

routing-protocol BGP
  local-as 65101
  neighbor 10.0.0.1 remote-as 65001
  advertise-prefixes [loopback-Leaf01]
  import-policy ALLOW-EXPECTED-FROM-SPINE01
  maximum-paths 4          # dépend du matériel et du logiciel
```

Ce pseudo-code ne constitue pas une configuration utilisable telle quelle sur Cisco NX-OS, Arista EOS, Juniper Junos, FRRouting ou une autre plateforme. Il explicite les objets à configurer. Une configuration production nécessite la syntaxe réelle, les préfixes exacts, les garde-fous et une validation hors production.

## 5. ECMP : chemins multiples en pratique

### 5.1 Où se trouvent les chemins ?

Dans une fabric à deux niveaux avec deux Spine, Leaf-A peut disposer de deux chemins de coût égal vers la loopback ou les réseaux rattachés à Leaf-B : l’un via Spine-1 et l’autre via Spine-2. Pour que les deux chemins soient installés, le protocole, ses attributs et les règles du système doivent autoriser le multipath. La seule présence physique de deux câbles ne garantit pas qu’ECMP fonctionne.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 370" role="img" aria-label="Deux chemins ECMP entre deux Leaf, le premier via Spine 1 et le second via Spine 2" width="100%" height="auto"><defs><marker id="si2Arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#7ce5ad"/></marker></defs><style>.si2b{rx:10;stroke-width:2}.si2t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.si2s{font:12px system-ui,sans-serif;fill:#b7c5d8;text-anchor:middle}.si2path{fill:none;stroke:#7ce5ad;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#si2Arrow);animation:si2dash 2.3s linear infinite}@keyframes si2dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.si2path{animation:none}}</style><rect class="si2b" x="55" y="145" width="170" height="72" fill="#183b2b" stroke="#7ce5ad"/><text x="140" y="174" class="si2t">LEAF A</text><text x="140" y="195" class="si2s">Destination distante</text><rect class="si2b" x="675" y="145" width="170" height="72" fill="#183b2b" stroke="#7ce5ad"/><text x="760" y="174" class="si2t">LEAF B</text><text x="760" y="195" class="si2s">Préfixe cible</text><rect class="si2b" x="340" y="34" width="220" height="72" fill="#173b59" stroke="#67d9ff"/><text x="450" y="63" class="si2t">SPINE 1</text><text x="450" y="84" class="si2s">Chemin A</text><rect class="si2b" x="340" y="255" width="220" height="72" fill="#173b59" stroke="#67d9ff"/><text x="450" y="284" class="si2t">SPINE 2</text><text x="450" y="305" class="si2s">Chemin B</text><g class="si2path"><path d="M225 158 L340 88" marker-end="url(#si2Arrow)"/><path d="M560 88 L675 158" marker-end="url(#si2Arrow)"/><path d="M225 203 L340 273" marker-end="url(#si2Arrow)"/><path d="M560 273 L675 203" marker-end="url(#si2Arrow)"/></g><text x="450" y="132" class="si2s">Deux routes de coût égal</text><text x="450" y="352" class="si2s">Le hachage répartit généralement les flux ; ce ne sont pas des copies de chaque paquet.</text></svg></div>

### 5.2 Hachage des flux

Les équipements utilisent souvent certains champs d’en-tête — par exemple adresses IP et ports TCP/UDP — pour choisir un membre ECMP. Plusieurs flux peuvent alors emprunter différents chemins, tandis qu’un même flux conserve généralement une sélection cohérente afin de limiter le réordonnancement.

Le hachage ne garantit pas une distribution parfaitement égale. Si un seul flux très volumineux domine le trafic, il peut saturer un chemin alors que les autres sont moins chargés. Il faut observer les compteurs par interface et les statistiques de flux, pas uniquement le débit agrégé de la fabric.

### 5.3 Déséquilibre et polarisation

Des problèmes peuvent apparaître lorsque plusieurs couches de hachage produisent des choix corrélés, lorsque le nombre de flux est faible ou lorsque les champs disponibles ne distinguent pas suffisamment les conversations. Le résultat peut être une utilisation inégale des liens.

Démarche de diagnostic :

1. comparer le débit par lien Leaf–Spine et non seulement par équipement ;
2. vérifier les erreurs physiques, pertes, files et drops ;
3. comparer plusieurs périodes pour distinguer une pointe normale d’une anomalie persistante ;
4. vérifier les champs utilisés par le hachage si la plateforme l’expose ;
5. examiner les flux volumineux et les destinations les plus sollicitées ;
6. ne modifier le hachage qu’après avoir formulé une hypothèse et prévu un retour arrière.

Ne pas confondre ECMP avec LACP. ECMP sélectionne entre des chemins de couche 3 selon les routes installées ; LACP négocie l’appartenance de liens physiques à un agrégat Ethernet. Les deux mécanismes peuvent coexister, mais ils n’opèrent pas au même niveau.

## 6. Convergence et détection de panne

### 6.1 Les étapes d’une panne

Lorsqu’un lien tombe, l’équipement doit détecter l’événement, en informer le plan de contrôle, retirer ou invalider la route affectée et utiliser les chemins encore valides. Le temps observé par l’application dépend de plusieurs composants : la détection physique ou logique, le protocole de routage, l’installation des routes dans le plan de données, les files réseau et le comportement des applications.

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 250" role="img" aria-label="Séquence logique de convergence après la panne d’un lien de fabric" width="100%" height="auto"><defs><marker id="si3Arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#f6c36a"/></marker></defs><style>.si3b{rx:10;stroke-width:2}.si3t{font:600 14px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.si3s{font:12px system-ui,sans-serif;fill:#bcc9da;text-anchor:middle}.si3p{fill:none;stroke:#f6c36a;stroke-width:2.7;marker-end:url(#si3Arrow);stroke-dasharray:6 5;animation:si3dash 2.4s linear infinite}@keyframes si3dash{to{stroke-dashoffset:-22}}@media(prefers-reduced-motion:reduce){.si3p{animation:none}}</style><rect class="si3b" x="20" y="70" width="160" height="92" fill="#3b2922" stroke="#f6c36a"/><text x="100" y="104" class="si3t">1. Détecter</text><text x="100" y="126" class="si3s">LOS, protocole, BFD</text><text x="100" y="144" class="si3s">selon le scénario</text><rect class="si3b" x="205" y="70" width="160" height="92" fill="#25304a" stroke="#90b4ff"/><text x="285" y="104" class="si3t">2. Signaler</text><text x="285" y="126" class="si3s">État d’interface</text><text x="285" y="144" class="si3s">ou voisinage Down</text><rect class="si3b" x="390" y="70" width="160" height="92" fill="#25304a" stroke="#90b4ff"/><text x="470" y="104" class="si3t">3. Recalculer</text><text x="470" y="126" class="si3s">Retirer la route</text><text x="470" y="144" class="si3s">ou le next-hop</text><rect class="si3b" x="575" y="70" width="160" height="92" fill="#183b2c" stroke="#7ce5ad"/><text x="655" y="104" class="si3t">4. Installer</text><text x="655" y="126" class="si3s">Chemin survivant</text><text x="655" y="144" class="si3s">dans le forwarding</text><rect class="si3b" x="760" y="70" width="140" height="92" fill="#183b2c" stroke="#7ce5ad"/><text x="830" y="104" class="si3t">5. Vérifier</text><text x="830" y="126" class="si3s">Flux rétabli ?</text><text x="830" y="144" class="si3s">Pertes résiduelles ?</text><g class="si3p"><path d="M180 116 H205" marker-end="url(#si3Arrow)"/><path d="M365 116 H390" marker-end="url(#si3Arrow)"/><path d="M550 116 H575" marker-end="url(#si3Arrow)"/><path d="M735 116 H760" marker-end="url(#si3Arrow)"/></g><text x="460" y="202" class="si3s">Le temps de convergence total dépend du matériel, des protocoles, des timers et de la politique.</text><text x="460" y="224" class="si3s">Une détection plus rapide ne corrige pas une mauvaise capacité ou une route absente.</text></svg></div>

### 6.2 BFD : rôle et limites

BFD (*Bidirectional Forwarding Detection*) est un mécanisme destiné à détecter rapidement la défaillance d’un chemin bidirectionnel entre systèmes de transfert. Il peut fonctionner avec différents protocoles et médias, mais doit être pris en charge et configuré aux deux extrémités selon le scénario visé. La détection BFD ne remplace pas le protocole de routage : elle peut lui signaler rapidement une perte de voisinage ou de chemin afin que des actions appropriées soient prises.

Un réglage très agressif des intervalles n’est pas automatiquement meilleur. Une grande quantité de sessions BFD, des timers trop courts ou une charge CPU peuvent augmenter la pression sur les équipements et provoquer de faux positifs. Les paramètres doivent être validés avec le matériel, le logiciel et les objectifs de disponibilité.

### 6.3 Fast convergence et risques

La convergence se mesure dans des conditions explicites. Une annonce constructeur comme « convergence en X millisecondes » doit être lue avec son contexte : taille de la table, type de panne, nombre de routes, configuration des timers, charge, version logicielle et méthode de mesure. Il faut établir un objectif de service réaliste et le mesurer dans son propre environnement.

Une séquence de tests doit distinguer au moins :

- perte optique d’un seul lien ;
- arrêt administratif d’une interface ;
- redémarrage d’un Spine ;
- disparition d’une session de routage sans perte physique évidente ;
- perte d’accès au next-hop ou à une loopback ;
- épuisement ou surcharge d’un chemin survivant.

Chaque test doit enregistrer l’événement déclenché, la détection, l’évolution de la table de routage, les compteurs, le nombre de paquets perdus et l’impact applicatif.

## 7. MTU, Ethernet et VXLAN

### 7.1 Pourquoi la MTU est importante

La MTU définit la taille maximale d’un paquet de couche 3 transporté sans fragmentation sur une interface, selon le protocole et la plateforme. Le fonctionnement exact dépend des conventions d’interface et du traitement des en-têtes. Dans un chemin de bout en bout, la plus petite MTU compatible peut limiter la taille des paquets.

Un overlay ajoute des en-têtes au paquet d’origine. VXLAN encapsule une trame Ethernet dans UDP/IP, ce qui augmente la taille totale sur le réseau physique. Si la MTU underlay est trop petite par rapport aux paquets encapsulés, des paquets peuvent être fragmentés, rejetés ou subir des problèmes de performance selon les versions IP, les drapeaux et la configuration.

### 7.2 Vérifier de bout en bout

Ne règle pas seulement les interfaces des Spine. Vérifie les MTU :

- sur les ports des serveurs et hyperviseurs ;
- sur les Leaf et les liens montants ;
- sur tous les liens du underlay ;
- sur les interfaces et tunnels overlay ;
- vers les passerelles et services externes, lorsque les flux passent par eux.

Une configuration cohérente doit documenter si la MTU affichée correspond à la trame Ethernet, au paquet IP ou à une convention propre au constructeur. Deux valeurs portant le même nombre peuvent ne pas désigner la même couche selon les systèmes. Utilise des tests adaptés au chemin et à la taille souhaitée, sans se contenter d’un ping de petite taille.

### 7.3 VXLAN : ce qu’il ajoute

VXLAN est un mécanisme d’encapsulation d’overlay permettant de transporter des trames Ethernet à travers un réseau IP. Les points de terminaison VXLAN (VTEP) encapsulent et décapsulent les paquets. Dans de nombreuses conceptions de data center, les Leaf jouent ce rôle de VTEP, tandis que le underlay assure l’acheminement IP entre leurs adresses de terminaison.

Le VNI (*VXLAN Network Identifier*) identifie un segment VXLAN. Il ne faut pas confondre VLAN et VNI : le VLAN appartient à l’identification Ethernet locale et le VNI identifie le segment overlay. La correspondance entre VLAN, segment logique, VNI et passerelle doit être documentée. Les détails exacts dépendent du modèle d’overlay.

### 7.4 Underlay et overlay

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 410" role="img" aria-label="Schéma de séparation entre overlay VXLAN et underlay IP dans une fabric Spine Leaf" width="100%" height="auto"><defs><marker id="si4Arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#67d9ff"/></marker></defs><style>.si4b{rx:10;stroke-width:2}.si4t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.si4s{font:12px system-ui,sans-serif;fill:#bdcadd;text-anchor:middle}.si4p{fill:none;stroke:#67d9ff;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#si4Arrow);animation:si4dash 2.5s linear infinite}@keyframes si4dash{to{stroke-dashoffset:-28}}@media(prefers-reduced-motion:reduce){.si4p{animation:none}}</style><rect x="25" y="20" width="850" height="155" rx="16" fill="#11202e" stroke="#344f6a" stroke-dasharray="5 5"/><text x="450" y="43" class="si4t">UNDERLAY — transport IP entre VTEP</text><rect class="si4b" x="80" y="66" width="140" height="64" fill="#173b59" stroke="#67d9ff"/><text x="150" y="92" class="si4t">LEAF A</text><text x="150" y="112" class="si4s">VTEP A</text><rect class="si4b" x="380" y="66" width="140" height="64" fill="#173b59" stroke="#67d9ff"/><text x="450" y="92" class="si4t">SPINE</text><text x="450" y="112" class="si4s">Route IP</text><rect class="si4b" x="680" y="66" width="140" height="64" fill="#173b59" stroke="#67d9ff"/><text x="750" y="92" class="si4t">LEAF B</text><text x="750" y="112" class="si4s">VTEP B</text><g class="si4p"><path d="M220 98 H380" marker-end="url(#si4Arrow)"/><path d="M520 98 H680" marker-end="url(#si4Arrow)"/></g><rect x="25" y="205" width="850" height="170" rx="16" fill="#171b30" stroke="#7269ba" stroke-dasharray="5 5"/><text x="450" y="230" class="si4t">OVERLAY — réseau logique transporté par encapsulation</text><rect class="si4b" x="80" y="255" width="190" height="68" fill="#303052" stroke="#a59cff"/><text x="175" y="283" class="si4t">VNI 10100</text><text x="175" y="303" class="si4s">Segment applicatif</text><rect class="si4b" x="630" y="255" width="190" height="68" fill="#303052" stroke="#a59cff"/><text x="725" y="283" class="si4t">VNI 10100</text><text x="725" y="303" class="si4s">Même segment logique</text><path d="M270 289 C370 250 530 250 630 289" fill="none" stroke="#a59cff" stroke-width="3" stroke-dasharray="7 6" marker-end="url(#si4Arrow)"/><text x="450" y="350" class="si4s">Le tunnel est logique ; les paquets encapsulés sont acheminés par les routes IP du underlay.</text></svg></div>

Le underlay n’a pas nécessairement besoin de connaître toutes les adresses des machines virtuelles. Il doit surtout rendre joignables les VTEP et fournir une connectivité fiable. L’overlay transporte les segments logiques, tandis que son plan de contrôle ou ses mécanismes d’apprentissage distribuent les informations nécessaires à la livraison des trames.

### 7.5 EVPN en introduction

BGP EVPN est une famille de mécanismes de plan de contrôle souvent associée à VXLAN. Elle peut distribuer des informations d’accessibilité de couche 2 et de couche 3, plutôt que de dépendre uniquement de l’apprentissage par diffusion inconnue ou de mécanismes propres à une plateforme. L’implémentation doit être conçue selon les fonctions réellement supportées.

Le modèle mental à retenir :

- le underlay transporte les paquets IP entre les adresses des VTEP ;
- l’encapsulation VXLAN identifie le segment overlay ;
- EVPN peut signaler les informations d’accessibilité et certains rôles de passerelle ;
- la politique de sécurité reste à concevoir explicitement : la présence de VXLAN ou EVPN n’autorise pas automatiquement tous les flux.

Il n’est pas recommandé de mélanger des paramètres d’overlay copiés depuis deux plateformes différentes. Le choix du mode de passerelle, de l’annonce des préfixes, du multihoming et de la suppression de trafic de diffusion doit rester cohérent.

## 8. LAG, MLAG et multihoming

### 8.1 LACP et port-channel

LACP permet à deux systèmes directement reliés de négocier un agrégat de liens Ethernet, souvent appelé port-channel ou LAG (*Link Aggregation Group*). L’agrégat peut augmenter la capacité disponible pour un ensemble de flux et protéger contre la panne d’un membre. Il ne garantit pas qu’un flux unique utilise simultanément tous les liens : la distribution s’effectue généralement par hachage.

LACP concerne un agrégat entre deux terminaux d’une liaison. Il ne remplace pas le routage ECMP entre plusieurs Spine. En fonction de la plateforme, un même Leaf peut employer un LAG vers un serveur et des liens routés indépendants vers les Spine.

### 8.2 MLAG et limites

MLAG (*Multi-Chassis Link Aggregation*) permet, sur les plateformes qui le prennent en charge, de présenter un agrégat raccordé à deux switches physiques. Les deux switches doivent coordonner l’état et le comportement de l’agrégat au moyen d’un mécanisme spécifique au constructeur. Les détails ne sont pas uniformes d’un fournisseur à l’autre.

Les points à concevoir comprennent le lien de peer, le keepalive, le traitement du split-brain, les conséquences de la perte d’un peer et les politiques de configuration. Un lien serveur à deux Leaf sans technologie de multihoming compatible peut créer des boucles, des problèmes de MAC ou des comportements asymétriques.

### 8.3 Comparer les mécanismes

| Mécanisme | Rôle principal | À retenir |
|---|---|---|
| ECMP | Choisir parmi plusieurs next-hops IP de coût égal | Plusieurs chemins de couche 3 ; hachage des flux possible |
| LACP/LAG | Agréger des liens Ethernet entre deux systèmes | Négociation des membres et capacité de l’agrégat |
| MLAG | Étendre un agrégat vers deux switches selon une solution constructeur | Coordination inter-switchs et scénarios de split-brain à tester |
| EVPN multihoming | Modèle de multihoming standardisé pour certains overlays | Dépend du support et de l’architecture choisie |

Le choix ne se fait pas uniquement en fonction du nombre de câbles. Il doit prendre en compte la topologie, la manière dont les MAC et les routes sont annoncées, le plan de contrôle et les scénarios de panne.

## 9. Dimensionnement de la fabric

### 9.1 Ports disponibles

Pour estimer la capacité de ports, compter les liaisons de chaque Leaf vers les Spine. Si chaque Leaf se relie à chacun de quatre Spine par une liaison, chaque Leaf consomme quatre ports montants et chaque Spine consomme un port par Leaf. Pour 12 Leaf et 4 Spine, cela représente 48 liaisons Leaf–Spine et 12 ports de fabric utilisés sur chaque Spine, sous l’hypothèse d’une liaison par paire.

Le calcul ne prend pas en compte les ports de gestion, les liens inter-équipements additionnels, les liens de supervision, les modules, ni les ports inutilisables à cause des choix de vitesse ou de transceiver. L’inventaire des ports doit être fait modèle par modèle.

### 9.2 Surabonnement

Le ratio de surabonnement peut être estimé en divisant la capacité agrégée théorique des ports downlink par la capacité agrégée des uplinks. Il s’agit d’une approximation : le débit réel dépend des directions, du nombre de flux, des destinations, de la capacité de commutation, des files et des pertes éventuelles.

**Exemple :** un Leaf possède 48 ports downlink à 25 Gbit/s et quatre liens montants à 100 Gbit/s :

- capacité downlink théorique : `48 × 25 = 1 200 Gbit/s` ;
- capacité uplink théorique : `4 × 100 = 400 Gbit/s` ;
- ratio nominal : `1 200 / 400 = 3:1`.

Pour interpréter ce ratio, ne présume pas que tous les ports émettent en permanence à pleine vitesse vers des destinations situées ailleurs dans la fabric. De même, un ratio de 1:1 n’assure pas à lui seul une latence basse, une absence de congestion ou une capacité intégralement disponible après panne.

### 9.3 Capacité après défaillance

Une fabric doit également être évaluée en mode dégradé. Avec quatre Spine et quatre uplinks de 100 Gbit/s par Leaf, la capacité montante nominale du Leaf est de 400 Gbit/s. Si un seul chemin est indisponible, la capacité nominale restante vers les trois Spine restants est de 300 Gbit/s, sous réserve que l’ECMP et les autres conditions de service restent fonctionnels.

Ce calcul peut être trop optimiste si le problème est un Spine complet qui retire de nombreux chemins à la fois, si d’autres liens partagent un même chemin physique, ou si le fabric impose des limites internes. Le dimensionnement doit donc examiner les pannes simples attendues et, pour les services critiques, les domaines de panne qui peuvent être corrélés.

### 9.4 Facteurs de capacité autres que le débit

- **Paquets par seconde :** les petits paquets peuvent atteindre la limite de traitement avant d’atteindre le débit en bits.
- **Latence :** dépend du matériel, des files, du chemin et de la charge ; compter des sauts ne suffit pas.
- **Buffers :** leur comportement sous microbursts varie selon les équipements.
- **Transceivers et fibres :** vérifier vitesse, distance, type de fibre et compatibilité.
- **Alimentation et refroidissement :** une conception redondante de câbles n’aide pas si les deux équipements partagent un même point de panne électrique.
- **Croissance :** conserver une marge pour les ports, la bande passante, les routes, les VNI, les sessions et la télémétrie.

## 10. QoS et congestion

### 10.1 Les causes de congestion

Une fabric peut avoir des liens rapides tout en subissant de la congestion. Les causes fréquentes incluent un flux volumineux, une concentration de destinations, des microbursts, des buffers insuffisants pour le profil de trafic, un oversubscription élevé ou une défaillance qui réduit la capacité disponible. Une interface à 20 % d’utilisation moyenne peut tout de même subir de brèves pointes qui remplissent une file.

### 10.2 Politique QoS cohérente

La QoS (*Quality of Service*) classe les paquets et définit leur traitement en période de concurrence : files, priorités, pondération, marquage et éventuellement contrôle de débit. Les valeurs DSCP et CoS doivent être traitées selon une politique de bout en bout. Marquer un paquet comme prioritaire sans configurer de façon cohérente les équipements successifs ne garantit pas un traitement privilégié.

Un plan QoS devrait répondre aux questions suivantes : quelles applications ont des exigences de latence ou de perte ? Où le marquage est-il défini ? Quels équipements le conservent, le réécrivent ou le suppriment ? Quels trafics peuvent consommer une file dédiée ? Comment les drops de chaque file sont-ils mesurés ?

### 10.3 PFC et Ethernet sans perte : prudence

Certains réseaux de stockage ou de calcul à haut débit utilisent des mécanismes de contrôle de flux spécifiques, par exemple Priority Flow Control (PFC) dans des environnements Ethernet adaptés. PFC n’est pas une solution universelle à la congestion : une configuration inappropriée peut propager la pause et créer des problèmes de blocage ou de latence. Les besoins des applications, les fonctions du matériel et l’architecture entière doivent être validés avant activation.

## 11. Exploitation et observabilité

### 11.1 Les quatre plans d’observation

1. **Physique :** état des ports, lumière optique, erreurs, CRC, pertes, puissance TX/RX et températures selon le matériel.
2. **Adjacences :** état des voisins de routage, sessions BGP/OSPF, BFD si utilisé, MTU et compteurs de keepalive.
3. **Routage et forwarding :** routes connues, next-hops installés, nombre de chemins ECMP, FIB, drops et compteurs par port.
4. **Application :** disponibilité, latence, pertes, retransmissions, tests synthétiques et logs des services.

Un ping réussi vers une loopback ne prouve pas que l’application fonctionne ; une session BGP active ne prouve pas que les bonnes routes sont installées dans la FIB. Le diagnostic doit vérifier chaque couche.

### 11.2 Mesures recommandées

Collecter au minimum :

- état et transitions de chaque interface ;
- erreurs physiques et taux de drops ;
- utilisation en entrée et sortie par lien ;
- état et durée des sessions de routage ;
- nombre de routes reçues, acceptées et rejetées ;
- nombre de next-hops ECMP installés ;
- événements d’alimentation, de température et de redémarrage ;
- latence et perte de tests synthétiques entre points représentatifs ;
- métriques applicatives fournies par les équipes systèmes.

Une moyenne sur cinq minutes masque parfois les microbursts. Utiliser des fréquences et histogrammes adaptés aux phénomènes recherchés, sans générer trop de télémétrie pour les équipements ou la plateforme de collecte.

### 11.3 Baseline et alertes

Établir une baseline lors d’une période représentative. Une alerte doit être actionnable et donner le contexte : équipement, port, sens, période, seuil, valeur actuelle et corrélation possible avec un événement. Trop d’alertes de faible qualité conduisent à leur ignorance.

Il est souvent préférable de combiner un seuil absolu (par exemple un lien qui reste au-dessus d’un niveau d’utilisation) avec une condition de durée, une évolution du taux de drops et la connaissance du rôle du port. Les seuils doivent refléter le service, pas simplement une valeur copiée depuis un exemple générique.

## 12. Sécurité d’une fabric Spine/Leaf

### 12.1 Séparer gestion et production

L’administration des switches doit être protégée par un réseau de gestion, des identités individuelles, une authentification adaptée, des rôles à privilèges minimaux et des journaux centralisés. Limiter les services d’administration aux sources autorisées. Le contrôle d’accès hors bande doit lui-même être supervisé et sécurisé.

### 12.2 Filtrer les annonces de routage

N’annonce que les préfixes attendus par chaque voisin. Les politiques d’import et d’export permettent de réduire les risques de routes inattendues ou de fuite de préfixes. Utiliser des mécanismes de protection de session et de limitation du nombre de routes lorsque la plateforme le permet, avec des valeurs cohérentes avec le design et des procédures de réaction en cas de seuil atteint.

Les filtres ne doivent pas bloquer par erreur les routes de loopback ou les préfixes indispensables à la convergence. Vérifie chaque politique avec une liste positive de routes attendues, des compteurs de rejet et des tests de panne.

### 12.3 Plan de contrôle et services d’infrastructure

Protéger les interfaces de gestion, le plan de contrôle, les services de découverte, les API et les accès aux consoles. Ne pas exposer directement les interfaces d’administration à des réseaux utilisateurs ou à Internet. Maintenir une version logicielle supportée et surveiller les vulnérabilités pertinentes pour le matériel et les fonctions activées.

La microsegmentation des workloads relève de politiques complémentaires — ACL, pare-feu distribué, contrats ou contrôles de plateforme — et non de la seule topologie physique. Un réseau Spine/Leaf bien construit n’implique pas que deux serveurs puissent ou ne puissent pas communiquer : c’est la configuration de routage et de sécurité qui détermine les flux permis.

## 13. Méthode de dépannage par couches

### 13.1 Symptôme : un serveur ne joint pas un serveur derrière un autre Leaf

Procéder dans cet ordre :

1. confirmer l’adresse IP, le masque et la passerelle du serveur source et de la destination ;
2. vérifier le lien serveur–Leaf, le VLAN/port, les erreurs et l’apprentissage MAC si la couche 2 locale est concernée ;
3. vérifier que la passerelle et le routage côté Leaf sont opérationnels ;
4. vérifier l’adjacence et les routes vers le préfixe distant ;
5. vérifier que le next-hop est présent dans la RIB puis dans la FIB ;
6. vérifier les chemins ECMP et leurs interfaces de sortie ;
7. inspecter filtres, ACL, pare-feu et politiques de sécurité ;
8. confirmer le retour de trafic et les éventuelles routes asymétriques ;
9. regarder MTU, drops et compteurs si les petits paquets passent mais pas les grands.

### 13.2 Symptôme : un chemin est saturé, les autres non

Vérifier d’abord les valeurs par lien et par sens. Confirmer que les routes sont réellement multipath et que les next-hops souhaités sont installés. Analyser les gros flux, les ports utilisés dans le hachage et les effets d’un LAG en aval. Examiner également les drops de queue et les microbursts : la charge moyenne n’est pas toujours représentative.

### 13.3 Symptôme : un tunnel overlay échoue

Un tunnel VXLAN nécessite de la connectivité IP entre les adresses VTEP et une configuration cohérente des identifiants et des paramètres d’encapsulation. Vérifier :

- reachabilité IP entre les loopbacks VTEP ;
- routes et next-hops dans le underlay ;
- MTU sur tout le chemin ;
- VNI et correspondance avec les réseaux logiques ;
- informations d’accessibilité annoncées par le plan de contrôle overlay ;
- passerelle, ARP/ND et règles de sécurité ;
- compteurs de drops et captures sur les points où elles sont autorisées.

### 13.4 Matrice de diagnostic

| Observation | Cause possible | Contrôle suivant |
|---|---|---|
| Interface down / pertes optiques | Fibre, transceiver, port distant ou équipement | Vérifier alarmes optiques, câblage et logs des deux côtés |
| Session de routage down, lien up | Paramètres de voisinage, ACL, adressage ou processus | Vérifier IPs, AS, timers, authentification et journaux |
| Route présente en RIB, absent du forwarding | Next-hop non résolu, limites ou politique | Inspecter la FIB, la résolution récursive et les raisons de rejet |
| Ping petit fonctionne, gros échoue | MTU ou filtrage lié à la taille | Tester progressivement la taille et le bit DF si applicable |
| Un seul flux lent | Hachage, congestion localisée ou endpoint | Comparer plusieurs flux et les compteurs des liens |
| Aller fonctionne, retour échoue | Route retour ou filtrage asymétrique | Tracer les deux directions et vérifier les politiques stateful |
| Un VNI est injoignable, les autres fonctionnent | Mapping VLAN/VNI, control-plane overlay ou policy | Comparer une entrée qui fonctionne à une qui échoue |

### 13.5 Outils de validation

Selon la plateforme, utiliser l’équivalent de :

- `show interfaces` et compteurs d’erreurs ;
- `show ip route` / `show route` ;
- commandes de voisinage et de résumé BGP/OSPF ;
- consultation de la FIB et des next-hops installés ;
- état BFD si ce mécanisme est déployé ;
- compteurs de files et télémétrie ;
- `ping`, `traceroute`/`tracert` et tests de MTU ;
- captures de paquets ciblées lorsque l’accès, la sécurité et l’impact le permettent.

Les noms de commandes diffèrent. Toujours identifier la plateforme et sa version avant d’utiliser un guide de dépannage.

## 14. Automatisation et gestion des changements

### 14.1 Pourquoi automatiser ?

Une fabric comporte de nombreux ports et des configurations répétitives. L’automatisation peut réduire les erreurs de frappe, normaliser l’adressage, générer les politiques, vérifier la cohérence et conserver l’historique. Mais automatiser une erreur la répète rapidement : la validation du modèle est aussi importante que le générateur.

### 14.2 Source de vérité

Maintenir un inventaire avec :

- noms et rôles des équipements ;
- rack, position, modèle et version ;
- ports, voisins, câbles et vitesses ;
- adresses de liens, loopbacks et numéros d’AS ;
- réseaux des workloads, passerelles, VLAN/VNI ;
- profils de MTU, QoS et sécurité ;
- relations et dépendances de changement.

Le fichier d’inventaire doit être assez précis pour reconstruire la topologie et générer les configurations, mais aussi facile à réviser et à comparer.

### 14.3 Idempotence et contrôle de dérive

Une opération idempotente peut être appliquée plusieurs fois sans créer des doublons ni modifier le résultat attendu après la première application. Les outils d’automatisation devraient comparer l’état désiré à l’état observé, appliquer uniquement les différences et signaler les écarts non prévus.

Avant le déploiement, valider la syntaxe, les adresses en doublon, l’existence des voisins, la cohérence des MTU, les limites de ports et les filtres de routes. Après le déploiement, comparer l’état réel à l’état attendu et tester la connectivité des chemins critiques.

### 14.4 Pipeline de changement recommandé

<div class="diagram-wrap"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 290" role="img" aria-label="Cycle de changement automatisé : inventaire, génération, validation, déploiement progressif et vérification" width="100%" height="auto"><defs><marker id="si5Arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#a99cff"/></marker></defs><style>.si5b{rx:10;stroke-width:2}.si5t{font:600 14px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.si5s{font:12px system-ui,sans-serif;fill:#bdcadd;text-anchor:middle}.si5p{fill:none;stroke:#a99cff;stroke-width:2.6;stroke-dasharray:7 6;marker-end:url(#si5Arrow);animation:si5dash 2.3s linear infinite}@keyframes si5dash{to{stroke-dashoffset:-24}}@media(prefers-reduced-motion:reduce){.si5p{animation:none}}</style><rect class="si5b" x="20" y="58" width="155" height="78" fill="#252a45" stroke="#a99cff"/><text x="97" y="88" class="si5t">1. Inventaire</text><text x="97" y="109" class="si5s">Source de vérité</text><rect class="si5b" x="198" y="58" width="155" height="78" fill="#252a45" stroke="#a99cff"/><text x="275" y="88" class="si5t">2. Générer</text><text x="275" y="109" class="si5s">Configuration attendue</text><rect class="si5b" x="376" y="58" width="155" height="78" fill="#3b2d20" stroke="#f6c36a"/><text x="453" y="88" class="si5t">3. Valider</text><text x="453" y="109" class="si5s">Syntaxe + préconditions</text><rect class="si5b" x="554" y="58" width="155" height="78" fill="#173b59" stroke="#67d9ff"/><text x="631" y="88" class="si5t">4. Déployer</text><text x="631" y="109" class="si5s">Petit lot contrôlé</text><rect class="si5b" x="732" y="58" width="148" height="78" fill="#183b2c" stroke="#7ce5ad"/><text x="806" y="88" class="si5t">5. Vérifier</text><text x="806" y="109" class="si5s">Santé et flux</text><g class="si5p"><path d="M175 97 H198" marker-end="url(#si5Arrow)"/><path d="M353 97 H376" marker-end="url(#si5Arrow)"/><path d="M531 97 H554" marker-end="url(#si5Arrow)"/><path d="M709 97 H732" marker-end="url(#si5Arrow)"/></g><path d="M806 136 V200 H453 V136" fill="none" stroke="#f6c36a" stroke-width="2.4" stroke-dasharray="6 6" marker-end="url(#si5Arrow)"/><text x="625" y="190" class="si5s">Échec : rollback ou correction</text><text x="450" y="246" class="si5s">Conserver le diff, l’approbation, les tests, l’heure et le résultat de chaque changement.</text></svg></div>

### 14.5 Plan de retour arrière

Avant tout changement touchant l’underlay, le protocole de routage, le MTU ou les politiques globales, préciser les symptômes qui déclenchent le rollback, la configuration précédente, les accès de secours, les métriques à observer et la personne responsable de la décision. Une sauvegarde de configuration n’est utile que si elle peut être restaurée par une procédure connue et testée.

Les opérations sur un seul équipement à la fois réduisent souvent le risque, mais ne constituent pas une règle absolue : un changement peut nécessiter une séquence coordonnée. Le plan doit définir les dépendances et le domaine d’impact, plutôt que d’appliquer aveuglément une stratégie unique.

## 15. Atelier pratique : construire un design intermédiaire

### 15.1 Scénario

On doit raccorder 6 racks de serveurs. On prévoit 6 Leaf et 3 Spine. Chaque Leaf dispose d’un lien routé vers chaque Spine. Les serveurs de chaque rack utilisent un réseau dédié ; deux workloads doivent échanger des données à travers des Leaf différents. Une augmentation de capacité est prévue l’année suivante.

**Contraintes de départ :**
- garder les rôles physiques séparés ;
- choisir un modèle de routage sous-jacent et le documenter ;
- prévoir des loopbacks stables ;
- calculer les liaisons et la consommation de ports ;
- tester une panne d’uplink et une panne de Spine ;
- définir comment un overlay serait ajouté sans confondre le VNI et l’underlay.

### 15.2 Topologie physique et calcul

Nombre de liaisons Leaf–Spine : `6 × 3 = 18`. Chaque Leaf consomme trois ports montants pour la fabric. Chaque Spine consomme six ports destinés aux Leaf, à condition d’utiliser un lien par paire et de ne pas ajouter de liens supplémentaires.

Si chaque Leaf reçoit 48 ports serveur de 25 Gbit/s et utilise trois uplinks de 100 Gbit/s, sa capacité théorique côté serveur est de `1 200 Gbit/s` et sa capacité montante nominale de `300 Gbit/s`. Le ratio agrégé théorique est donc `4:1`. Après la perte d’un seul Spine, la capacité montante nominale tombe à `200 Gbit/s` par Leaf : le ratio effectif devient `6:1`, sans même compter d’autres limites potentielles.

Ce résultat ne détermine pas à lui seul si le design est acceptable. Il faut connaitre les profils de trafic, les objectifs de service, les vitesses réelles des ports, les taux de simultanéité et les flux pendant les opérations de maintenance.

### 15.3 Concevoir l’underlay

Choisir soit un IGP, soit une architecture BGP de fabric, puis documenter :

- le bloc de transit et la convention /31 ou autre ;
- les loopbacks des six Leaf et des trois Spine ;
- les adjacences attendues ;
- les routes que chaque classe d’équipement doit annoncer ;
- la politique multipath ;
- la protection des sessions et le dispositif de détection de panne ;
- les valeurs de MTU et les règles de filtrage.

Vérifier que toutes les loopbacks qui doivent communiquer sont atteignables, que les routes ont plusieurs next-hops si le design l’exige et que les préfixes inattendus sont rejetés. L’état « voisin établi » est nécessaire mais pas suffisant : la table de routage et la FIB doivent également correspondre à l’intention.

### 15.4 Valider les workloads

Créer une matrice de flux simple :

| Source | Destination | Résultat attendu | Pourquoi |
|---|---|---|---|
| Serveur A | Passerelle locale | Autorisé | Connectivité de base |
| Serveur A | Serveur B autorisé | Autorisé | Flux applicatif déclaré |
| Serveur A | Réseau d’administration non autorisé | Bloqué selon la politique | Réduction de la surface d’attaque |
| Serveur A | Réseau externe requis | Autorisé via le chemin prévu | Dépendance explicitement documentée |
| Serveur isolé | Service interdit | Bloqué | Vérification négative de la segmentation |

Répéter les tests dans les deux sens lorsque la politique et les protocoles le demandent. Enregistrer les résultats et les captures utiles. Ne jamais considérer qu’un test négatif est concluant uniquement parce que le ping échoue : une application peut utiliser un autre protocole ou un autre port.

### 15.5 Tester les pannes

Pour chaque test, définir une fenêtre, un déclencheur, les systèmes observés, les métriques et la méthode de restauration. Exemples :

1. couper un lien Leaf–Spine de test ; vérifier que les routes et le trafic utilisent les chemins restants ;
2. arrêter un Spine pendant un test contrôlé ; vérifier la convergence et la capacité résiduelle ;
3. restaurer le Spine ; observer la réintégration des chemins et l’état des sessions ;
4. tester une taille de paquet proche de la MTU prévue ; rechercher fragmentation, perte et erreurs ;
5. comparer la latence et le taux de perte avant, pendant et après chaque événement.

Le résultat doit être mesuré et comparé à un seuil de réussite décidé avant le test. Une phrase telle que « le réseau a l’air stable » n’est pas un critère de validation.

## 16. Erreurs fréquentes de conception

### 16.1 Se fier à la présence des câbles

Un câblage complet ne garantit ni le routage multipath, ni les annonces correctes, ni l’absence de congestion. Vérifier chaque couche indépendamment : physique, adressage, voisinage, RIB, FIB, overlay et application.

### 16.2 Configurer ECMP sans analyser la capacité de panne

Avec plusieurs Spine, ECMP peut répartir les flux sur plusieurs chemins. Si un Spine tombe, les autres absorbent le trafic restant. Si la fabric était déjà proche de la saturation, la tolérance au défaut peut ne pas répondre aux besoins du service. Dimensionner le réseau en mode dégradé.

### 16.3 Mélanger les fonctions de chaque couche

Ne pas confondre l’adresse de management, les loopbacks, les réseaux de transit, les passerelles workloads et les identifiants VXLAN. Les séparer simplifie les politiques de routage, l’automatisation et la résolution de problèmes.

### 16.4 Changer plusieurs variables simultanément

Modifier à la fois l’IGP/BGP, les MTU, les politiques ECMP et le mapping overlay rend le diagnostic très difficile. Découper le changement en étapes, associer chaque étape à des critères et conserver un plan de retour arrière.

### 16.5 Traiter la QoS comme une solution magique

Une priorité élevée ne crée pas de capacité. La QoS distribue la ressource en cas de concurrence ; le dimensionnement, la visibilité et la correction d’une congestion persistante restent indispensables.

### 16.6 Copier des timers « ultra-rapides » sans validation

Des timers plus courts peuvent détecter plus vite certaines pannes mais augmenter la charge, déclencher des basculements intempestifs ou interagir mal avec le logiciel. Définir un objectif, mesurer et tester plutôt que choisir une valeur extrême par principe.

## 17. Quiz de validation

**1.** Pourquoi la présence d’un lien vers chaque Spine ne garantit-elle pas à elle seule ECMP ?  
**2.** Quelle est la différence fondamentale entre la RIB et la FIB ?  
**3.** Pourquoi une loopback peut-elle être « up » tout en restant inaccessible depuis un autre Leaf ?  
**4.** Dans une fabric avec 8 Leaf et 4 Spine, combien de liens Leaf–Spine existe-t-il avec une liaison par paire ?  
**5.** Quelle est la fonction principale de BFD ?  
**6.** Pourquoi VXLAN impose-t-il de vérifier la MTU de bout en bout ?  
**7.** En quoi ECMP diffère-t-il de LACP ?  
**8.** Pourquoi faut-il mesurer les liens individuellement lorsqu’un chemin semble saturé ?  
**9.** Quel rôle peut jouer BGP EVPN dans un overlay VXLAN ?  
**10.** Pourquoi un test de ping réussi ne suffit-il pas pour déclarer une application fonctionnelle ?

### Corrigé

1. Le plan de contrôle doit installer plusieurs next-hops de coût égal et le forwarding doit les accepter ; plusieurs câbles peuvent coexister sans multipath effectif.  
2. La RIB contient l’information de routage connue et sélectionnée ; la FIB est la structure utilisée par le plan de données pour transférer les paquets. Les détails d’implémentation varient.  
3. La loopback est logique ; elle peut être active localement alors que les routes permettant de la joindre sont absentes ou incorrectes.  
4. `8 × 4 = 32` liens.  
5. Détecter l’état d’un chemin bidirectionnel entre systèmes, avec un mécanisme de détection pouvant être plus rapide que certains timers de protocole ; BFD ne remplace pas le routage.  
6. L’encapsulation ajoute des en-têtes et peut faire dépasser la taille autorisée sur un des liens du chemin.  
7. ECMP choisit entre plusieurs next-hops IP de coût égal ; LACP négocie des membres d’un agrégat Ethernet entre deux systèmes.  
8. Le hachage peut répartir les flux de façon inégale ; l’agrégat masque les liens qui portent réellement la charge ou les drops.  
9. Distribuer des informations de contrôle d’accessibilité pour certains overlays, notamment VXLAN, selon les fonctions déployées.  
10. Le ping ne vérifie ni tous les ports/protocoles applicatifs, ni les dépendances, ni nécessairement le chemin aller-retour, la MTU et les politiques de sécurité.

## 18. Checklist de conception et d’exploitation

Avant la mise en service :

- [ ] topologie physique complète et ports réservés ;
- [ ] plan d’adressage séparant transit, loopbacks, gestion et workloads ;
- [ ] protocole de routage choisi et documenté ;
- [ ] politique de routes entrantes et sortantes ;
- [ ] ECMP vérifié sur la RIB et la FIB ;
- [ ] MTU validée de bout en bout, y compris encapsulation si overlay ;
- [ ] capacité calculée en fonctionnement normal et après panne ;
- [ ] supervision physique, routage, forwarding et application ;
- [ ] procédures de changement et de rollback testées ;
- [ ] tests de panne et tests positifs/négatifs enregistrés ;
- [ ] administration protégée et accès privilégiés limités ;
- [ ] inventaire et schéma mis à jour après chaque changement.

## 19. Glossaire intermédiaire

- **Underlay :** réseau IP de transport entre les équipements de la fabric.
- **Overlay :** réseau logique construit au-dessus d’un réseau de transport, souvent grâce à l’encapsulation.
- **ECMP :** utilisation de plusieurs chemins IP de coût égal.
- **RIB :** base des informations de routage.
- **FIB :** structure de transfert utilisée pour acheminer les paquets.
- **Loopback :** interface logique souvent utilisée comme adresse stable d’identification ou de session.
- **IGP :** protocole de routage interne, comme OSPF ou IS-IS.
- **BGP :** protocole de routage par sessions et politiques ; eBGP est souvent utilisé entre Leaf et Spine dans certaines fabric.
- **BFD :** mécanisme de détection de défaillance d’un chemin bidirectionnel.
- **MTU :** taille maximale transportée selon la convention de l’interface et du protocole.
- **VXLAN :** encapsulation de trames Ethernet dans UDP/IP pour des réseaux overlay.
- **VTEP :** point de terminaison d’un tunnel VXLAN.
- **VNI :** identifiant de segment VXLAN.
- **EVPN :** famille de mécanismes de plan de contrôle BGP pour des services Ethernet VPN, employée notamment avec certains overlays.
- **LAG/LACP :** agrégation et négociation de liens Ethernet.
- **MLAG :** mécanisme constructeur de port-channel multi-équipement, avec un comportement dépendant de l’implémentation.
- **Microburst :** pointe de trafic très brève pouvant remplir une file sans apparaître dans une moyenne à long intervalle.
- **Convergence :** transition vers un état de routage et de transfert cohérent après un changement de topologie.

## 20. Références pour approfondir

- IETF, [RFC 7938 — Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938) : principes d’utilisation de BGP dans les data centers de grande échelle.
- IETF, [RFC 7348 — Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348) : format et principes de l’encapsulation VXLAN.
- IETF, [RFC 5880 — Bidirectional Forwarding Detection (BFD)](https://www.rfc-editor.org/rfc/rfc5880) : mécanisme de détection de panne de chemin.
- Cisco, [Data Center Infrastructure Design](https://www.cisco.com/c/en/us/td/docs/solutions/Enterprise/Data_Center/DC_Infra2_5/DCInfra_1.html) : éléments de conception d’infrastructure de centre de données. Vérifier la documentation correspondant à la plateforme et à la version déployées.

Les références expliquent des principes, pas une configuration universelle. Pour une implémentation précise, utiliser le guide de conception validé et les guides de configuration de la version logicielle retenue.

## 21. Résumé à retenir

Une fabric Spine/Leaf intermédiaire doit être conçue comme un système de transport et d’exploitation, pas comme un simple dessin de switches. Le underlay fournit une reachabilité IP prévisible ; le protocole de routage et la configuration déterminent les chemins disponibles ; ECMP répartit des flux entre certains chemins installés ; la convergence détermine le comportement face aux pannes ; le MTU, les files et la capacité affectent le trafic réel ; VXLAN/EVPN peuvent ajouter une couche logique, mais ne remplacent pas la nécessité d’un underlay sain.

La méthode professionnelle consiste à documenter l’intention, calculer les ports et la capacité, filtrer les routes, valider les tables de routage et de transfert, mesurer les flux, tester les pannes et conserver un retour arrière. Une fabric est réellement prête lorsqu’elle reste observable, testable et exploitable en condition normale comme en mode dégradé.
