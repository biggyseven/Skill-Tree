# Segment Routing — Niveau Débutant

> **Objectif général :** comprendre le principe du Segment Routing, distinguer SR-MPLS et SRv6, reconnaître les principaux SID, et suivre un paquet dans une petite topologie avant d’aborder l’ingénierie de trafic avancée.

## 1. Objectifs pédagogiques et prérequis

À la fin de ce cours, tu dois pouvoir expliquer le source routing, différencier le plan de contrôle du plan de données, comprendre le rôle de l’IGP, lire les notions de Prefix-SID/Node-SID et Adj-SID, décrire une SR Policy et dépanner les premières étapes d’un domaine SR-MPLS. Tu connaîtras également SRv6 à un niveau conceptuel.

**Prérequis :** adressage IPv4, routes, notions d’OSPF ou IS-IS, bases d’MPLS (labels, push/swap/pop) et lecture simple de topologie. Ce cours reste pédagogique : les commandes exactes dépendent de la plateforme et de la version logicielle.

## 2. Pourquoi le Segment Routing ?

Le **Segment Routing (SR)** est une architecture de transfert fondée sur une liste d’instructions, appelées *segments*, que le réseau exécute pour acheminer un paquet. Chaque instruction est identifiée par un **Segment Identifier (SID)**. Le point d’entrée du domaine peut sélectionner une séquence de segments pour exprimer le trajet ou un service à appliquer.

Dans un routage IP classique, chaque routeur prend une décision à partir de la destination et de sa table locale. Avec SR, le headend peut ajouter une séquence d’instructions : certains segments signifient « atteindre ce nœud selon l’IGP », d’autres « utiliser cette adjacence », ou encore « entrer dans cette politique ». Les routeurs traversés continuent néanmoins à utiliser leurs tables de transfert et à exécuter les comportements définis par les segments. Ce n’est donc pas une source route arbitraire sans contrôle : SR s’appuie sur la topologie, les politiques et les capacités du domaine.

### Bénéfices attendus

- **Moins de signalisation par chemin** : en SR-MPLS, les chemins peuvent être représentés par des stacks de labels sans devoir établir un LSP RSVP-TE distinct pour chaque tunnel. SR peut coexister avec LDP ou RSVP-TE selon la migration.
- **Contrôle du chemin** : une SR Policy peut exprimer des contraintes ou objectifs, par exemple éviter un lien, préférer un chemin ou respecter une affinité.
- **Protection** : des mécanismes comme TI-LFA peuvent préparer des réparations locales rapides lorsque la topologie et l’implémentation le permettent.
- **Automatisation** : un contrôleur ou un calculateur PCE peut aider à calculer ou programmer des politiques, sans que l’architecture SR impose un unique modèle de contrôle.

### Limites et responsabilités

SR ne remplace pas l’IGP, la conception de l’adressage, la supervision ou les tests de changement. Une liste de segments trop longue peut dépasser les capacités de la plateforme ; des SIDs incohérents ou un plan d’adressage ambigu rendent le dépannage difficile. Les fonctionnalités disponibles dépendent des ASIC, des versions et de la famille de systèmes.

### Schéma 1 — Routage IP et Segment Routing

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Comparaison entre chemin choisi saut par saut et liste de segments"><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Routage IP classique et Segment Routing</text><rect x="35" y="115" width="180" height="88" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="125.0" y="142" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Routage IP</text><text x="125.0" y="163" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Destination finale</text><rect x="390" y="115" width="180" height="88" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="480.0" y="142" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Routeur ingress</text><text x="480.0" y="163" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Choisit une politique</text><rect x="745" y="115" width="180" height="88" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="835.0" y="142" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Destination</text><text x="835.0" y="163" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Termine le trajet</text><line x1="215" y1="160" x2="390" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="390,160 380.0,155.0 380.0,165.0" fill="#6dd3ce"/><text x="302.5" y="151.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">paquet IP</text><line x1="570" y1="160" x2="745" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="745,160 735.0,155.0 735.0,165.0" fill="#6dd3ce"/><text x="657.5" y="151.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">liste de segments</text><text x="480" y="245" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Le réseau transporte le paquet selon l’état de routage</text><text x="480" y="268" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">SR permet à l’entrée de décrire une séquence</text><text x="480" y="291" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">d’instructions topologiques ou de service.</text></svg>


### Schéma complémentaire — Exemple de topologie SR-MPLS

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="410" viewBox="0 0 960 410" role="img" aria-label="Routeurs R1 R2 R3 R4 et chemin logique"><rect x="1" y="1" width="958" height="408" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Exemple de topologie SR-MPLS</text><rect x="60" y="135" width="150" height="78" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="135.0" y="162" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R1</text><text x="135.0" y="183" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Ingress / Headend</text><rect x="300" y="75" width="150" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="375.0" y="102" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R2</text><text x="375.0" y="123" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Transit</text><rect x="300" y="215" width="150" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="375.0" y="242" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R3</text><text x="375.0" y="263" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Transit</text><rect x="560" y="135" width="150" height="78" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="635.0" y="162" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R4</text><text x="635.0" y="183" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Egress / cible</text><rect x="785" y="135" width="130" height="78" rx="12" fill="#44351b" stroke="#f0b75e" stroke-width="2"/><text x="850.0" y="162" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Service</text><text x="850.0" y="183" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">LAN cible</text><line x1="210" y1="155" x2="300" y2="115" stroke="#6dd3ce" stroke-width="3"/><polygon points="300,115 288.8,114.5 292.9,123.6" fill="#6dd3ce"/><text x="255.0" y="126.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">10</text><line x1="210" y1="190" x2="300" y2="250" stroke="#6dd3ce" stroke-width="3"/><polygon points="300,250 294.5,240.3 288.9,248.6" fill="#6dd3ce"/><text x="255.0" y="211.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">20</text><line x1="450" y1="115" x2="560" y2="155" stroke="#6dd3ce" stroke-width="3"/><polygon points="560,155 552.3,146.9 548.9,156.3" fill="#6dd3ce"/><text x="505.0" y="126.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">10</text><line x1="450" y1="250" x2="560" y2="190" stroke="#6dd3ce" stroke-width="3"/><polygon points="560,190 548.8,190.4 553.6,199.2" fill="#6dd3ce"/><text x="505.0" y="211.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">10</text><line x1="710" y1="174" x2="785" y2="174" stroke="#6dd3ce" stroke-width="3"/><polygon points="785,174 775.0,169.0 775.0,179.0" fill="#6dd3ce"/><text x="747.5" y="165.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">IP</text><text x="480" y="345" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="400" fill="#c8d7e8">Le chemin final dépend de la topologie IGP et des segments imposés.</text></svg>


## 3. SR-MPLS et SRv6 : deux instanciations

Le terme Segment Routing décrit l’architecture, pas un seul format de paquet. Les deux familles essentielles sont :

| Sujet | SR-MPLS | SRv6 |
|---|---|---|
| Données de segment | Label MPLS | Adresse SID IPv6 |
| Encodage de la politique | Pile de labels | SR Header (SRH) IPv6 contenant une liste de segments |
| Réseau de transport | Domaine qui commute MPLS | Domaine IPv6 qui prend en charge SRv6 |
| Pré-requis de déploiement | MPLS et matériel/logiciel SR-MPLS | IPv6 et prise en charge SRv6 sur les chemins concernés |
| Points de vigilance | SRGB, profondeur de pile, comportement des labels | format du SID, SRH, MTU, fonctions SRv6 et capacités matériel |

Dans SR-MPLS, un segment est représenté par un label MPLS (ou un index qui correspond à un label dans le cadre du SRGB). Dans SRv6, un SID est une adresse IPv6 associée à un comportement, et l’entête SRH peut transporter la liste ordonnée des segments. Les deux modèles partagent le principe d’instructions, mais on ne transpose pas directement leurs paramètres ou leur configuration.

### Schéma 2 — Comparaison des plans de données

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Comparaison entre labels MPLS et segments IPv6"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Deux plans de données : SR-MPLS et SRv6</text><rect x="55" y="90" width="390" height="100" rx="12" fill="#15334a" stroke="#5a82b1" stroke-width="2"/><text x="250.0" y="117" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">SR-MPLS</text><text x="250.0" y="138" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">SID encodé comme label MPLS</text><rect x="515" y="90" width="390" height="100" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="710.0" y="117" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">SRv6</text><text x="710.0" y="138" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">SID encodé comme adresse IPv6</text><rect x="85" y="225" width="330" height="80" rx="12" fill="#1b3c52" stroke="#39a7a1" stroke-width="2"/><text x="250.0" y="252" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Pile de labels</text><text x="250.0" y="273" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Le label actif est au sommet</text><rect x="545" y="225" width="330" height="80" rx="12" fill="#392b54" stroke="#a78bfa" stroke-width="2"/><text x="710.0" y="252" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">IPv6 + SRH</text><text x="710.0" y="273" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Segments list + Segments Left</text><text x="480" y="345" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Les objectifs SR sont communs, mais l’encapsulation,</text><text x="480" y="365" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">les capacités et les contraintes du matériel diffèrent.</text></svg>


## 4. Vocabulaire minimal

- **Domaine SR** : ensemble de nœuds qui participent au domaine SR et comprennent les informations de segments utiles à leur rôle.
- **Headend** : nœud qui classe le trafic et l’insère dans une SR Policy.
- **Segment / SID** : instruction et identifiant qui lui est associé. Le terme « SID » est couramment utilisé pour désigner le segment, même si l’architecture distingue l’instruction et son identifiant.
- **SR Policy** : politique de routage représentée par une liste ordonnée de segments et portée par un headend.
- **Control plane** : mécanismes qui annoncent les préfixes, la topologie, les SIDs et/ou les politiques.
- **Data plane** : mécanismes qui traitent les paquets réels en fonction des labels ou des headers.
- **IGP** : OSPF ou IS-IS peuvent annoncer les informations de segments adaptées à leur protocole.

## 5. Les principaux SID

### 5.1 Prefix-SID et Node-SID
Un **Prefix-SID** identifie un préfixe annoncé par un IGP SR-capable. Un **Node-SID** est le cas d’usage courant où le préfixe désigne l’adresse de loopback d’un routeur. En SR-MPLS, l’index de SID est mappé dans le SRGB local du routeur. Le comportement visé correspond typiquement à un chemin shortest-path IGP vers ce préfixe, avec ECMP si plusieurs chemins sont équivalents selon l’algorithme.

### 5.2 Adjacency-SID
Un **Adjacency-SID** identifie une adjacence annoncée par un nœud. Par défaut, un Adj-SID est généralement local au nœud qui l’annonce, sauf mécanisme de publicité ou usage spécifique. Il sert lorsqu’une politique doit suivre une liaison déterminée plutôt que laisser le choix entièrement au calcul SPF. Il faut tenir compte de la portée et du sens de l’adjacence.

### 5.3 Binding SID
Un **Binding SID (BSID)** est associé à une SR Policy. Quand le headend reçoit un paquet dont le segment actif correspond au BSID local, il peut le diriger dans la policy associée. Cela permet d’abstraire une liste de segments sous une instruction, utile pour composer les politiques et limiter la complexité présentée en amont.

### 5.4 Anycast-SID
Un SID de préfixe anycast peut être annoncé par plusieurs routeurs partageant une destination logique. Le comportement et le plan d’allocation doivent être conçus attentivement, en particulier pour le mapping des SIDs globaux et la cohérence du SRGB.

### Schéma 3 — Familles de SID

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="420" viewBox="0 0 960 420" role="img" aria-label="Node Prefix Adjacency et Binding SID"><rect x="1" y="1" width="958" height="418" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Familles de SID à connaître</text><rect x="40" y="105" width="205" height="100" rx="12" fill="#15334a" stroke="#5a82b1" stroke-width="2"/><text x="142.5" y="132" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Prefix-SID / Node-SID</text><text x="142.5" y="153" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Vers un préfixe / routeur</text><rect x="270" y="105" width="205" height="100" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="372.5" y="132" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Adjacency-SID</text><text x="372.5" y="153" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Utiliser une liaison précise</text><rect x="500" y="105" width="205" height="100" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="602.5" y="132" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Binding SID (BSID)</text><text x="602.5" y="153" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Entrer dans une politique</text><rect x="730" y="105" width="190" height="100" rx="12" fill="#44351b" stroke="#f0b75e" stroke-width="2"/><text x="825.0" y="132" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Anycast-SID</text><text x="825.0" y="153" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Vers un groupe de nœuds</text><text x="480" y="260" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="400" fill="#c8d7e8">Un SID identifie une instruction : il ne faut pas confondre</text><text x="480" y="284" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="400" fill="#c8d7e8">le type de SID, sa portée (locale/globale), et son encodage.</text><text x="480" y="340" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#9fb4cc">Prefix-SID : chemin IGP shortest-path (souvent ECMP)</text><text x="480" y="361" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#9fb4cc">Adj-SID : voisinage / lien local par défaut</text><text x="480" y="382" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#9fb4cc">BSID : abstraction d’une SR Policy au headend</text></svg>


## 6. SRGB, SRLB et mapping des labels

En SR-MPLS, le **Segment Routing Global Block (SRGB)** est une plage de labels réservée au mapping des segments globaux. Le **Segment Routing Local Block (SRLB)** est une plage distincte destinée aux labels de segments locaux, selon l’implémentation. Le mapping d’un Prefix-SID par index dépend de la SRGB configurée sur un nœud.

Par exemple, si un index Prefix-SID vaut 10 et qu’un routeur utilise un SRGB commençant à 16000, son label peut être 16010 selon la plage et les règles d’allocation. Cet exemple illustre un calcul de base ; on doit vérifier les bornes et les informations réellement annoncées par les équipements.

Il est fortement recommandé de planifier les plages, d’éviter les recouvrements non voulus et de documenter les écarts entre nœuds. Une SRGB identique sur tous les routeurs d’un domaine simplifie l’exploitation, mais le modèle exact d’indexation et les exigences de cohérence doivent suivre la conception choisie. Un label n’est pas une adresse globale IP : il est interprété selon la table de labels et le contexte SR.

### Schéma 4 — Exemple de SRGB

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="SRGB commun recommandé et local label values"><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">SRGB : comprendre les labels globaux</text><rect x="55" y="110" width="250" height="105" rx="12" fill="#15334a" stroke="#5a82b1" stroke-width="2"/><text x="180.0" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Routeur A</text><text x="180.0" y="158" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">SRGB 16000–23999</text><rect x="355" y="110" width="250" height="105" rx="12" fill="#15334a" stroke="#5a82b1" stroke-width="2"/><text x="480.0" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Routeur B</text><text x="480.0" y="158" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">SRGB 16000–23999</text><rect x="655" y="110" width="250" height="105" rx="12" fill="#15334a" stroke="#5a82b1" stroke-width="2"/><text x="780.0" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Routeur C</text><text x="780.0" y="158" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">SRGB 16000–23999</text><line x1="305" y1="160" x2="355" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="355,160 345.0,155.0 345.0,165.0" fill="#6dd3ce"/><line x1="605" y1="160" x2="655" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="655,160 645.0,155.0 645.0,165.0" fill="#6dd3ce"/><text x="480" y="265" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Prefix-SID index  index 10  →  label 16010 (dans cet exemple)</text><text x="480" y="289" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Même index global + SRGB identique : label cohérent sur les nœuds</text><text x="480" y="313" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Vérifier la plage SRGB réellement configurée et annoncée.</text></svg>


## 7. Comment SR utilise OSPF ou IS-IS

Un IGP à état de liens calcule déjà la topologie et les chemins les plus courts. Les extensions SR ajoutent à la publicité des informations liées aux segments, par exemple les Prefix-SID et les Adj-SID. Les routeurs peuvent ainsi construire une représentation de la topologie enrichie, calculer le SPF et installer dans leur plan de transfert les entrées nécessaires.

Les extensions IGP ne rendent pas tous les routeurs du réseau automatiquement capables de traiter SR. Il faut vérifier le support des extensions, les fonctionnalités activées, l’allocation des SIDs, la cohérence des algorithmes IGP et la programmation du plan de données. Dans un déploiement progressif, les interactions avec les nœuds non-SR doivent être conçues et testées.

### Schéma 5 — Plan de contrôle SR

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Extensions OSPF ou IS-IS diffusant SIDs dans la LSDB"><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Plan de contrôle : IGP annonce les segments</text><rect x="45" y="120" width="180" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="135.0" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">IGP</text><text x="135.0" y="168" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">OSPF / IS-IS</text><rect x="290" y="85" width="175" height="80" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="377.5" y="112" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">LSDB</text><text x="377.5" y="133" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Préfixes + adjacences</text><rect x="530" y="120" width="180" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="620.0" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Calcul SPF</text><text x="620.0" y="168" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">FIB et next-hop</text><rect x="760" y="120" width="155" height="80" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="837.5" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">SIDs</text><text x="837.5" y="168" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Mapping / labels</text><line x1="225" y1="160" x2="290" y2="125" stroke="#6dd3ce" stroke-width="3"/><polygon points="290,125 278.8,125.3 283.6,134.1" fill="#6dd3ce"/><text x="257.5" y="133.5" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">TLV/LSA</text><line x1="465" y1="125" x2="530" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="530,160 523.6,150.9 518.8,159.7" fill="#6dd3ce"/><text x="497.5" y="133.5" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">topology</text><line x1="710" y1="160" x2="760" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="760,160 750.0,155.0 750.0,165.0" fill="#6dd3ce"/><text x="735.0" y="151.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">install</text><text x="480" y="270" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Le contrôle distribué apporte reachability et informations de segments.</text><text x="480" y="292" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Il ne signifie pas qu’un contrôleur central est obligatoire.</text></svg>


## 8. De la politique au paquet : comment un flux est transporté

Dans un modèle pédagogique SR-MPLS, le headend identifie le trafic concerné, sélectionne une SR Policy et insère la pile de labels qui représente sa liste de segments. Les routeurs utilisent le label actif et les informations locales de transfert. Lorsqu’un segment est terminé, le label correspondant est retiré et le prochain segment devient actif. Le détail des opérations de pile, du PHP et des labels explicites dépend de la politique, du comportement des segments et de la plateforme.

Une liste de segments peut combiner des Node-SIDs pour exprimer des sous-chemins et des Adj-SIDs pour fixer certaines liaisons. L’objectif n’est pas d’énumérer nécessairement chaque routeur du trajet : les segments peuvent décrire des sous-chemins compacts, ce qui réduit la taille de la liste.

### Schéma 6 — Pile de labels

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Pile illustrant labels pour des segments ordonnés"><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Pile SR-MPLS : séquence d’instructions</text><rect x="100" y="90" width="210" height="70" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="205.0" y="117" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Label 16010</text><text x="205.0" y="138" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">SID actif / premier segment</text><rect x="100" y="170" width="210" height="70" rx="12" fill="#15334a" stroke="#5a82b1" stroke-width="2"/><text x="205.0" y="197" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Label 16030</text><text x="205.0" y="218" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Segment suivant</text><rect x="100" y="250" width="210" height="70" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="205.0" y="277" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Paquet IP</text><text x="205.0" y="298" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Charge utile</text><rect x="455" y="120" width="430" height="95" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="670.0" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Traitement du segment actif</text><text x="670.0" y="168" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Chaque nœud exécute l’instruction associée.</text><line x1="310" y1="125" x2="455" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="455,160 446.5,152.8 444.1,162.5" fill="#6dd3ce"/><text x="382.5" y="133.5" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">top of stack</text><line x1="310" y1="205" x2="455" y2="175" stroke="#6dd3ce" stroke-width="3"/><polygon points="455,175 444.2,172.1 446.2,181.9" fill="#6dd3ce"/><text x="382.5" y="181.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">next</text><line x1="310" y1="285" x2="455" y2="195" stroke="#6dd3ce" stroke-width="3"/><polygon points="455,195 443.9,196.0 449.1,204.5" fill="#6dd3ce"/><text x="382.5" y="231.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">payload</text><text x="480" y="350" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">L’ordre de pile réel doit être validé sur la plateforme et les commandes de policy.</text></svg>


## 9. Node-SID contre Adj-SID : choisir le bon niveau de contrainte

Utilise un Node-SID lorsque le besoin est d’atteindre un routeur ou préfixe selon l’algorithme IGP. Le chemin exact peut changer après une modification de topologie. Utilise un Adj-SID lorsqu’une politique doit passer par une adjacence particulière. Dans ce second cas, la politique est plus contrainte et peut être sensible à la disparition du lien : il faut concevoir la protection, le recalcul ou le chemin de secours.

### Schéma 7 — Shortest-path et adjacency

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Différence entre shortest path et lien imposé"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Node-SID et Adj-SID ne promettent pas la même chose</text><rect x="45" y="115" width="130" height="78" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="110.0" y="142" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">A</text><text x="110.0" y="163" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Headend</text><rect x="275" y="70" width="130" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="340.0" y="97" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">B</text><text x="340.0" y="118" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Chemin court</text><rect x="275" y="225" width="130" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="340.0" y="252" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">C</text><text x="340.0" y="273" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Autre chemin</text><rect x="510" y="115" width="130" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="575.0" y="142" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">D</text><text x="575.0" y="163" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Point ciblé</text><rect x="750" y="115" width="155" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="827.5" y="142" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">E</text><text x="827.5" y="163" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Destination</text><line x1="175" y1="145" x2="275" y2="105" stroke="#6dd3ce" stroke-width="3"/><polygon points="275,105 263.9,104.1 267.6,113.4" fill="#6dd3ce"/><line x1="175" y1="165" x2="275" y2="255" stroke="#6dd3ce" stroke-width="3"/><polygon points="275,255 270.9,244.6 264.2,252.0" fill="#6dd3ce"/><line x1="405" y1="105" x2="510" y2="145" stroke="#6dd3ce" stroke-width="3"/><polygon points="510,145 502.4,136.8 498.9,146.1" fill="#6dd3ce"/><line x1="405" y1="255" x2="510" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="510,165 499.2,167.7 505.7,175.3" fill="#6dd3ce"/><line x1="640" y1="155" x2="750" y2="155" stroke="#6dd3ce" stroke-width="3"/><polygon points="750,155 740.0,150.0 740.0,160.0" fill="#6dd3ce"/><text x="475" y="340" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Node-SID vers D : suit le plus court chemin IGP vers D.</text><text x="475" y="362" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Adj-SID annoncé par B : peut forcer B à emprunter B–D.</text></svg>


## 10. Premiers pas vers les SR Policies

Une **SR Policy** s’exprime du point de vue du headend. Selon l’architecture, elle peut être configurée explicitement, calculée localement ou calculée par un contrôleur/PCE. Ses objectifs peuvent être un chemin imposé, une préférence, une contrainte d’affinité, une contrainte de latence ou la protection contre certains risques partagés (SRLG). Les possibilités réelles de calcul et d’installation varient selon le routeur et le contrôleur.

Une politique n’est pas effective uniquement parce qu’elle est configurée : il faut vérifier qu’une liste de segments valide existe, que les SIDs sont résolus, que les contraintes sont satisfaites, que le trafic est bien classé/steeré sur la policy et que l’état de forwarding correspond à l’intention.

### Schéma 8 — Headend et Segment List

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="410" viewBox="0 0 960 410" role="img" aria-label="Entrée de trafic et policy explicite ou calculée"><rect x="1" y="1" width="958" height="408" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">SR Policy : le headend applique une liste de segments</text><rect x="40" y="130" width="150" height="84" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="115.0" y="157" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Trafic entrant</text><text x="115.0" y="178" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">classe / destination</text><rect x="250" y="105" width="190" height="120" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="345.0" y="132" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Headend PE/R1</text><text x="345.0" y="153" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Steering vers la policy</text><rect x="500" y="80" width="180" height="82" rx="12" fill="#15334a" stroke="#5a82b1" stroke-width="2"/><text x="590.0" y="107" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Segment List A</text><text x="590.0" y="128" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">R2 → R4 → R7</text><rect x="500" y="205" width="180" height="82" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="590.0" y="232" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Segment List B</text><text x="590.0" y="253" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Chemin de secours</text><rect x="745" y="130" width="170" height="84" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="830.0" y="157" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Egress / service</text><text x="830.0" y="178" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Destination</text><line x1="190" y1="170" x2="250" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="250,165 239.6,160.8 240.4,170.8" fill="#6dd3ce"/><line x1="440" y1="145" x2="500" y2="120" stroke="#6dd3ce" stroke-width="3"/><polygon points="500,120 488.8,119.2 492.7,128.5" fill="#6dd3ce"/><text x="470.0" y="123.5" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">active</text><line x1="440" y1="185" x2="500" y2="245" stroke="#6dd3ce" stroke-width="3"/><polygon points="500,245 496.5,234.4 489.4,241.5" fill="#6dd3ce"/><text x="470.0" y="206.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">backup</text><line x1="680" y1="120" x2="745" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="745,160 739.1,150.5 733.9,159.0" fill="#6dd3ce"/><line x1="680" y1="245" x2="745" y2="185" stroke="#6dd3ce" stroke-width="3"/><polygon points="745,185 734.3,188.1 741.0,195.5" fill="#6dd3ce"/><text x="480" y="345" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Une policy peut être explicite ou calculée sous contraintes : coût, latence, affinité.</text></svg>


## 11. Protection et convergence : introduction à TI-LFA

La convergence IGP et la reconstruction des entrées de forwarding peuvent prendre du temps après une panne. Les mécanismes Fast Reroute visent à fournir une réparation locale immédiatement exploitable lorsqu’un lien ou un nœud devient indisponible. **TI-LFA** (Topology Independent Loop-Free Alternate) calcule un chemin de réparation qui couvre un ensemble plus large de scénarios que les LFA classiques, sous réserve que la topologie et la configuration le permettent.

Il ne faut pas supposer que TI-LFA est actif sur tous les nœuds, toutes les familles d’interfaces ou toutes les versions. Valide le support, les protections annoncées et les résultats de tests de panne. La protection locale n’élimine pas la nécessité de vérifier la convergence globale ni la stabilité après le rétablissement.

### Schéma 9 — Réparation locale

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="410" viewBox="0 0 960 410" role="img" aria-label="Chemin primaire et détour local vers un point sûr"><rect x="1" y="1" width="958" height="408" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">TI-LFA : protéger localement une panne</text><rect x="45" y="130" width="130" height="78" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="110.0" y="157" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R1</text><text x="110.0" y="178" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Point défaillant</text><rect x="270" y="60" width="130" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="335.0" y="87" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R2</text><text x="335.0" y="108" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Transit primaire</text><rect x="510" y="60" width="130" height="78" rx="12" fill="#4b232b" stroke="#e16a78" stroke-width="2"/><text x="575.0" y="87" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R3</text><text x="575.0" y="108" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Panne sur lien</text><rect x="510" y="225" width="130" height="78" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="575.0" y="252" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R4</text><text x="575.0" y="273" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Chemin alternatif</text><rect x="770" y="130" width="140" height="78" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="840.0" y="157" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R5</text><text x="840.0" y="178" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Destination</text><line x1="175" y1="145" x2="270" y2="100" stroke="#6dd3ce" stroke-width="3"/><polygon points="270,100 258.8,99.8 263.1,108.8" fill="#6dd3ce"/><text x="222.5" y="113.5" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">primaire</text><line x1="400" y1="100" x2="510" y2="100" stroke="#6dd3ce" stroke-width="3"/><polygon points="510,100 500.0,95.0 500.0,105.0" fill="#6dd3ce"/><line x1="640" y1="100" x2="770" y2="145" stroke="#6dd3ce" stroke-width="3"/><polygon points="770,145 762.2,137.0 758.9,146.5" fill="#6dd3ce"/><line x1="175" y1="185" x2="510" y2="265" stroke="#6dd3ce" stroke-width="3"/><polygon points="510,265 501.4,257.8 499.1,267.5" fill="#6dd3ce"/><text x="342.5" y="216.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">repair</text><line x1="640" y1="265" x2="770" y2="185" stroke="#6dd3ce" stroke-width="3"/><polygon points="770,185 758.9,186.0 764.1,194.5" fill="#6dd3ce"/><text x="480" y="350" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">TI-LFA prépare un détour sans attendre la convergence complète.</text><text x="480" y="370" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">La faisabilité dépend de la topologie, des métriques et du support plateforme.</text></svg>


## 12. SRv6 en aperçu

SRv6 applique le concept SR au plan de données IPv6. Un SID SRv6 est une adresse IPv6 associée à un comportement. Le SR Header (SRH) peut contenir une liste ordonnée de segments ; le champ *Segments Left* contribue à indiquer le segment actif dans le cycle de traitement. Certains comportements SRv6 peuvent représenter le transit, l’application d’une fonction ou un service.

SRv6 demande une conception IPv6 cohérente, le support de l’SRH sur les chemins et le matériel, une analyse du MTU/surcharge, et une attention aux politiques de sécurité sur les en-têtes d’extension. Les adresses IPv6 ordinaires ne deviennent pas automatiquement des SIDs SRv6 : le comportement doit être instancié suivant le modèle retenu.

### Schéma 10 — SRv6 en bref

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="SRv6 ajoute un SRH IPv6 qui porte les segments"><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">SRv6 : SID IPv6 et Segment Routing Header</text><rect x="45" y="125" width="180" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="135.0" y="152" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">IPv6 header</text><text x="135.0" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Destination Address = SID actif</text><rect x="270" y="125" width="200" height="90" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="370.0" y="152" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">SRH</text><text x="370.0" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Segments Left + liste SID</text><rect x="515" y="125" width="180" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="605.0" y="152" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Segment actif</text><text x="605.0" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Comportement local</text><rect x="740" y="125" width="175" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="827.5" y="152" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Payload</text><text x="827.5" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Paquet transporté</text><line x1="225" y1="170" x2="270" y2="170" stroke="#6dd3ce" stroke-width="3"/><polygon points="270,170 260.0,165.0 260.0,175.0" fill="#6dd3ce"/><line x1="470" y1="170" x2="515" y2="170" stroke="#6dd3ce" stroke-width="3"/><polygon points="515,170 505.0,165.0 505.0,175.0" fill="#6dd3ce"/><line x1="695" y1="170" x2="740" y2="170" stroke="#6dd3ce" stroke-width="3"/><polygon points="740,170 730.0,165.0 730.0,175.0" fill="#6dd3ce"/><text x="480" y="275" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">SRv6 est une instanciation distincte : les SIDs sont IPv6 addresses.</text><text x="480" y="299" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Ne pas confondre avec SR-MPLS, qui utilise des labels MPLS.</text></svg>


## 13. Configuration : ce qu’il faut retenir avant de toucher à un routeur

Le but de ce cours est de rendre le modèle compréhensible avant la pratique. La configuration réelle dépend de la plate-forme, de la version, du protocole IGP, de la plage SRGB, du mode SR-MPLS/SRv6 et des fonctionnalités de protection activées. Les commandes montrées ici sont donc un **plan de vérification conceptuel** et non un bloc universel à coller en production.

### Séquence de mise en place

1. Stabiliser l’adressage et les loopbacks.
2. Valider l’IGP sur tous les liens du domaine et vérifier l’absence de partitions.
3. Activer les extensions SR supportées dans le bon processus OSPF/IS-IS.
4. Planifier/configurer SRGB et les SIDs sans conflit.
5. Contrôler les SIDs annoncés et leur mapping dans chaque routeur.
6. Vérifier l’installation dans la FIB/LFIB et la résolution des next-hops.
7. Établir une SR Policy, puis confirmer son état et son steering.
8. Tester une panne contrôlée, mesurer la convergence et valider le retour à l’état nominal.

### Schéma 11 — Migration progressive

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="410" viewBox="0 0 960 410" role="img" aria-label="Coexistence, validation et rollback"><rect x="1" y="1" width="958" height="408" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Migration prudente vers Segment Routing</text><rect x="40" y="120" width="180" height="88" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="130.0" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">État initial</text><text x="130.0" y="168" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">IGP + LDP/RSVP</text><rect x="270" y="120" width="180" height="88" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="360.0" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Pilote SR</text><text x="360.0" y="168" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Un domaine / une zone</text><rect x="500" y="120" width="180" height="88" rx="12" fill="#15334a" stroke="#5a82b1" stroke-width="2"/><text x="590.0" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Validation</text><text x="590.0" y="168" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Reachability, labels, FRR</text><rect x="740" y="120" width="180" height="88" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="830.0" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Extension</text><text x="830.0" y="168" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Déploiement progressif</text><line x1="220" y1="165" x2="270" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="270,165 260.0,160.0 260.0,170.0" fill="#6dd3ce"/><line x1="450" y1="165" x2="500" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="500,165 490.0,160.0 490.0,170.0" fill="#6dd3ce"/><line x1="680" y1="165" x2="740" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="740,165 730.0,160.0 730.0,170.0" fill="#6dd3ce"/><text x="480" y="270" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Prévoir le rollback, les fenêtres de changement et des preuves mesurables.</text><text x="480" y="294" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">La coexistence SR et LDP/RSVP dépend de la conception et de la plateforme.</text></svg>


## 14. Vérifications et dépannage débutant

Adopte une approche en couches. Si le ping de loopback échoue, ne commence pas par la SR Policy : résous d’abord le problème de base. Si les loopbacks sont joignables mais que les SIDs n’apparaissent pas, regarde les extensions IGP et l’allocation. Si les SIDs sont annoncés mais que le forwarding échoue, vérifie le mapping, les labels, les next-hops, les capacités de pile, la MTU, et la configuration de steering.

### Checklist de vérification

- Les loopbacks de tous les routeurs sont joignables.
- Les adjacences OSPF/IS-IS sont stables.
- La LSDB contient les informations SR prévues.
- La SRGB et le mapping des Prefix-SIDs sont compris et cohérents avec la conception.
- Les SIDs locaux (Adj-SID/BSID) ont une portée connue.
- La FIB/LFIB montre le comportement et le next-hop attendus.
- La SR Policy est active, valide et bien utilisée par le trafic visé.
- Les compteurs, traces et tests de panne confirment la performance observée.

### Schéma 12 — Ordre du dépannage

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="430" viewBox="0 0 960 430" role="img" aria-label="Checklist de troubleshooting en couches"><rect x="1" y="1" width="958" height="428" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Dépannage SR : séparer contrôle et transfert</text><rect x="115" y="65" width="730" height="55" rx="12" fill="#15334a" stroke="#5a82b1" stroke-width="2"/><text x="480.0" y="92" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">1. Reachability IGP</text><text x="480.0" y="113" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">Vois-tu les loopbacks et la topologie ?</text><line x1="480" y1="120" x2="480" y2="135" stroke="#6dd3ce" stroke-width="2"/><polygon points="480,135 485.0,125.0 475.0,125.0" fill="#6dd3ce"/><rect x="115" y="135" width="730" height="55" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="480.0" y="162" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">2. SIDs annoncés</text><text x="480.0" y="183" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">Prefix-SID / Adj-SID attendus ?</text><line x1="480" y1="190" x2="480" y2="205" stroke="#6dd3ce" stroke-width="2"/><polygon points="480,205 485.0,195.0 475.0,195.0" fill="#6dd3ce"/><rect x="115" y="205" width="730" height="55" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="480.0" y="232" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">3. FIB / LFIB</text><text x="480.0" y="253" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">Mapping label et next-hop corrects ?</text><line x1="480" y1="260" x2="480" y2="275" stroke="#6dd3ce" stroke-width="2"/><polygon points="480,275 485.0,265.0 475.0,265.0" fill="#6dd3ce"/><rect x="115" y="275" width="730" height="55" rx="12" fill="#44351b" stroke="#f0b75e" stroke-width="2"/><text x="480.0" y="302" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">4. Policy / steering</text><text x="480.0" y="323" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">Le trafic entre-t-il dans la policy ?</text><line x1="480" y1="330" x2="480" y2="345" stroke="#6dd3ce" stroke-width="2"/><polygon points="480,345 485.0,335.0 475.0,335.0" fill="#6dd3ce"/><rect x="115" y="345" width="730" height="55" rx="12" fill="#17304a" stroke="#5a82b1" stroke-width="2"/><text x="480.0" y="372" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">5. Data plane</text><text x="480.0" y="393" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">MTU, compteurs, ECMP et captures ?</text></svg>


## 15. Laboratoire guidé : 4 routeurs en SR-MPLS

### Objectifs
Construire une topologie linéaire à quatre routeurs, activer un IGP compatible, annoncer les loopbacks, mettre en place SR-MPLS, contrôler les Node-SIDs, puis tester l’atteignabilité de bout en bout.

### Topologie de laboratoire

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Topologie de lab avec IGP, Node SIDs et tests de chemin"><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1424" stroke="#28415f" stroke-width="2"/><text x="480.0" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Laboratoire débutant : quatre routeurs SR-MPLS</text><rect x="50" y="125" width="155" height="82" rx="12" fill="#163b36" stroke="#46b99f" stroke-width="2"/><text x="127.5" y="152" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R1</text><text x="127.5" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">10.0.0.1 /32</text><rect x="280" y="125" width="155" height="82" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="357.5" y="152" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R2</text><text x="357.5" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">10.0.0.2 /32</text><rect x="510" y="125" width="155" height="82" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="587.5" y="152" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R3</text><text x="587.5" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">10.0.0.3 /32</text><rect x="740" y="125" width="155" height="82" rx="12" fill="#30274b" stroke="#a78bfa" stroke-width="2"/><text x="817.5" y="152" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">R4</text><text x="817.5" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">10.0.0.4 /32</text><line x1="205" y1="165" x2="280" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="280,165 270.0,160.0 270.0,170.0" fill="#6dd3ce"/><text x="242.5" y="156.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">10</text><line x1="435" y1="165" x2="510" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="510,165 500.0,160.0 500.0,170.0" fill="#6dd3ce"/><text x="472.5" y="156.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">20</text><line x1="665" y1="165" x2="740" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="740,165 730.0,160.0 730.0,170.0" fill="#6dd3ce"/><text x="702.5" y="156.0" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="600" fill="#e2e8f0">10</text><text x="480" y="270" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">Tests : adjacency IGP, SID annonce, table MPLS, traceroute MPLS/SR,</text><text x="480" y="294" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#c8d7e8">retrait temporaire d’un lien et observation de la reconvergence.</text></svg>

### Plan d’adressage proposé

| Routeur | Loopback0 | Lien vers le voisin gauche | Lien vers le voisin droit |
|---|---|---|---|
| R1 | 10.0.0.1/32 | — | 10.1.12.1/30 |
| R2 | 10.0.0.2/32 | 10.1.12.2/30 | 10.1.23.1/30 |
| R3 | 10.0.0.3/32 | 10.1.23.2/30 | 10.1.34.1/30 |
| R4 | 10.0.0.4/32 | 10.1.34.2/30 | — |

Choisis soit IS-IS soit OSPF pour ce premier essai, selon le support de ton environnement virtuel. Ne tente pas de copier un jeu de commandes récupéré pour une autre version sans vérifier sa syntaxe. Configure les loopbacks, valide l’IGP, active les extensions SR et attribue les Prefix-SIDs d’après une convention documentée.

### Tests

1. Vérifier les voisins IGP et le calcul des routes.
2. Vérifier que les loopbacks sont présentes dans la table de routage.
3. Vérifier les annonces de SIDs dans les informations d’état de liens.
4. Vérifier le mapping des SIDs et les entrées MPLS/FIB.
5. Tracer le chemin de R1 à R4 et expliquer quels SIDs gouvernent les étapes.
6. Couper temporairement un lien en laboratoire et observer le résultat de convergence.
7. Restaurer le lien, observer la stabilisation et documenter les résultats.

### Critères d’acceptation

- Les adjacences restent stables après convergence.
- Les loopbacks sont joignables dans les deux sens.
- Les Prefix-SIDs sont correctement annoncés et résolus.
- Le trafic de test traverse le domaine sans perte persistante.
- Toute fonctionnalité de protection est confirmée par une commande d’état et un test, jamais uniquement par une ligne de configuration.

## 16. Exercices corrigés

### Exercice 1 — Le SID n’est pas annoncé
**Situation :** R1 atteint la loopback de R2, mais ne voit pas son Prefix-SID.

**Réponse attendue :** l’underlay peut être fonctionnel sans que les extensions SR soient actives. Vérifier les capacités de l’IGP, la configuration d’activation SR, l’annonce du SID sur la bonne famille d’adresses, et la compatibilité logicielle.

### Exercice 2 — Le label calculé n’est pas celui attendu
**Situation :** le même index est observé, mais les labels calculés diffèrent entre deux équipements.

**Réponse attendue :** vérifier la SRGB, la convention d’indexation, la plage réservée et la portée du SID. Ne pas traiter un label comme une valeur globale indépendante de la SRGB locale. Les écarts doivent être compris et documentés.

### Exercice 3 — La policy est installée, mais aucun trafic ne l’utilise
**Réponse attendue :** vérifier l’état de la policy, les listes de segments candidates, le classement/steering du trafic, la résolution des segments, le next-hop, l’admissibilité de la policy et les compteurs correspondants. Une policy valide n’implique pas automatiquement que tout le trafic vers sa destination est orienté dessus.

### Exercice 4 — Un chemin explicite casse après la panne d’un lien
**Réponse attendue :** une séquence comportant un Adj-SID local peut être dépendante d’une adjacence donnée. Vérifier la protection FRR, la réparabilité topologique, la stratégie de recalcul et la politique de secours. Il ne faut pas supposer que le Node-SID et l’Adj-SID réagissent de la même façon.

## 17. Quiz final

1. Que signifie SID ?
2. Quelle différence conceptuelle existe entre SR-MPLS et SRv6 ?
3. Quel est le comportement typique attendu d’un Node-SID ?
4. Pourquoi un Adj-SID peut-il rendre un chemin plus contraint ?
5. À quoi sert le SRGB ?
6. Quel rôle l’IGP joue-t-il dans un domaine SR distribué ?
7. Que représente une SR Policy ?
8. Pourquoi faut-il contrôler le steering des flux et pas seulement la présence de la policy ?
9. Que vise TI-LFA ?
10. Quelles étapes de base suivre pour dépanner un flux SR ?

### Corrigé

1. Segment Identifier, identifiant d’une instruction de segment.
2. SR-MPLS utilise des labels MPLS ; SRv6 utilise des SIDs IPv6 et peut employer un SRH.
3. Acheminer selon l’algorithme IGP vers le préfixe/nœud associé, souvent via ECMP si applicable.
4. Il référence une adjacence particulière plutôt qu’un simple shortest-path vers une destination.
5. Définir la plage de labels utilisée pour le mapping de segments globaux en SR-MPLS.
6. Diffuser la topologie et les extensions annonçant les segments, puis permettre le calcul des chemins.
7. Une liste ordonnée de segments qui guide le trafic depuis un headend selon une intention.
8. Parce qu’une policy configurée ou valide n’est pas forcément utilisée par le trafic visé.
9. Fournir une réparation locale rapide lors de certaines pannes, suivant la topologie et le support.
10. Vérifier underlay/IGP, SIDs annoncés, SRGB/mapping, FIB/LFIB, policy/steering, puis le plan de données et les compteurs.

## 18. Glossaire

- **Adj-SID** : SID attaché à une adjacence.
- **BSID** : Binding SID associé à une SR Policy.
- **ECMP** : partage du trafic sur des chemins de coût équivalent.
- **FIB/LFIB** : bases de forwarding IP et MPLS.
- **Headend** : nœud qui applique une SR Policy aux paquets.
- **IGP** : protocole interne de routage, par exemple OSPF ou IS-IS.
- **Node-SID** : Prefix-SID qui identifie couramment un routeur par sa loopback.
- **Prefix-SID** : SID associé à un préfixe IGP.
- **SRGB** : bloc global de labels SR-MPLS.
- **SRLB** : bloc local réservé aux labels SR locaux.
- **SRH** : Segment Routing Header de SRv6.
- **SR Policy** : politique matérialisée par une liste de segments ordonnée.
- **TI-LFA** : mécanisme de protection rapide basé sur un calcul de réparation indépendant de nombreuses contraintes classiques de LFA.

## 19. Checklist de révision

- [ ] Je sais expliquer la différence entre routage IP classique et source routing SR.
- [ ] Je sais distinguer SR-MPLS et SRv6.
- [ ] Je comprends Node-SID, Prefix-SID, Adj-SID et BSID.
- [ ] Je sais expliquer SRGB et le mapping d’un index.
- [ ] Je comprends l’annonce des SIDs via l’IGP.
- [ ] Je sais tracer le chemin d’un paquet et expliquer sa pile de labels en SR-MPLS.
- [ ] Je sais expliquer le rôle d’une SR Policy et vérifier que le trafic l’utilise.
- [ ] Je sais expliquer l’objectif général de TI-LFA.
- [ ] Je peux dépanner en séparant control plane et data plane.
- [ ] Je vérifie les commandes selon la plateforme et la version avant toute utilisation.

## 20. Passer d’un besoin métier à une SR Policy

La conception d’une SR Policy doit partir d’un besoin observable plutôt que d’une liste de SIDs choisie au hasard. Par exemple, une application temps réel peut exiger une latence maximale, un service de réplication peut privilégier la capacité disponible, et un trafic de sauvegarde peut être orienté vers un chemin moins coûteux. Segment Routing fournit un vocabulaire pour exprimer un chemin, mais ne garantit pas à lui seul les objectifs de performance. Les mesures et la politique de contrôle doivent être conçues ensemble.

**Étape 1 — caractériser le trafic.** Identifier la source, la destination, le type de trafic et le point de classification. Une SR Policy ne se substitue pas à une politique QoS : il faut distinguer quel trafic est sélectionné, quel chemin lui est proposé et quel traitement de file d’attente lui est appliqué.

**Étape 2 — définir les contraintes.** Préciser ce qui est obligatoire (par exemple traverser un point de service) et ce qui constitue une préférence (par exemple éviter un lien saturé). Les affinités, les contraintes de latence, les SRLG ou les objectifs de coût ne sont disponibles que si la topologie expose les informations nécessaires et si le contrôleur/routeur sait les traiter.

**Étape 3 — choisir le niveau d’abstraction.** Un Node-SID est compact et suit le plus court chemin IGP vers un préfixe. Une liste composée de plusieurs Node-SIDs peut contraindre des segments du trajet. Un Adj-SID peut imposer une adjacence précise, mais rend la policy plus dépendante de la liaison. Un BSID peut masquer une politique derrière un identifiant unique.

**Étape 4 — vérifier le résultat calculé.** Examiner la candidate path, sa validité, la disponibilité des segments, les contraintes satisfaites et le chemin effectivement programmé dans le plan de données. Une policy peut exister dans la configuration mais être inactive, non résolue ou ne recevoir aucun trafic.

**Étape 5 — mesurer et réviser.** Effectuer des tests en charge représentatifs. Mesurer latence, pertes, gigue, utilisation, profondeur de pile et comportement à la panne. Les objectifs doivent être formulés sous forme de critères de validation (par exemple : aucune perte persistante après basculement, temps de convergence mesuré et retour à l’état stable), et non seulement en termes de configuration présente.

## 21. Plan d’adressage, allocation des SID et conventions d’exploitation

Une bonne architecture SR commence par un plan stable des identifiants et des responsabilités. La loopback d’un routeur sert souvent d’identifiant stable pour le routage IGP ; les Prefix-SIDs doivent être attribués selon une convention écrite, maîtrisée par l’équipe réseau et alignée sur la SRGB. Le but est de limiter les conflits, de rendre les traces interprétables et de simplifier les changements.

| Élément | Décision de conception | Contrôle opérationnel |
|---|---|---|
| Loopbacks | Plan IPv4/IPv6 stable, annonces IGP explicites | Reachability depuis tous les nœuds du domaine |
| SRGB | Plage de labels documentée, cohérente avec la plateforme | Valeurs configurées, annoncées et effectivement mappées |
| Prefix-SID / Node-SID | Index par nœud selon une convention | Correspondance préfixe ↔ index ↔ label observée |
| Adj-SID | Portée et besoin de lien explicite documentés | SID local/global, direction et comportement confirmés |
| BSID | Allocation et ownership définis au headend | Policy liée, validité et compteurs associés |
| Algorithme IGP | Algorithme standard ou spécifique choisi en connaissance de cause | Compatibilité des nœuds et absence de blackhole pour les algorithmes non supportés |

Pour un domaine de laboratoire, on peut réserver une plage de tests distincte, consigner le routeur, le préfixe, l’index SID et le label résultant. En production, éviter les changements d’index sans analyser leurs effets. Un changement qui semble purement administratif peut modifier la signification d’une liste de labels, créer une incohérence temporaire ou perturber des politiques explicites.

Il faut également distinguer l’index d’un Prefix-SID du label MPLS observé sur un routeur. L’index est une valeur d’identification du segment global ; le label est obtenu via le mapping prévu par la plage de labels locale. Une observation incomplète de la SRGB peut conduire à croire à tort qu’un SID est incohérent. Les commandes de vérification et leur affichage diffèrent selon IOS XE, IOS XR et les autres implémentations.

## 22. Coexistence et migration depuis LDP ou RSVP-TE

Une migration vers SR ne se résume pas à activer un seul paramètre global. Les réseaux peuvent exploiter LDP, RSVP-TE et SR sur une période de transition. Cette coexistence exige une politique claire de préférence, une vérification de la continuité des chemins et un plan de retour arrière. Certaines plateformes proposent des mécanismes de synchronisation IGP/LDP ou des fonctions d’interopérabilité ; leur disponibilité et leur syntaxe ne sont pas universelles.

### Approche progressive

1. **Inventorier** les routeurs, versions, cartes, familles d’interfaces et fonctionnalités MPLS déjà utilisées. Identifier les tunnels RSVP-TE, sessions LDP, services L3VPN et besoins de protection existants.
2. **Construire un pilote** sur une zone contrôlée, avec une SRGB documentée et un protocole IGP supporté. Conserver des mesures de référence avant le changement.
3. **Activer et observer** les extensions SR sur les routeurs pilotes. Contrôler l’adjacence, les annonces de SID, la LFIB et la résolution de chaque next-hop. Ne pas introduire une policy de production tant que le transport de base n’est pas confirmé.
4. **Tester les scénarios de panne** : perte d’un lien, perte d’un nœud, retrait de SID, indisponibilité du contrôleur si présent, restauration du service. Documenter le temps de convergence et tout paquet perdu.
5. **Étendre par étapes** en gardant des critères d’arrêt explicites. Une extension n’est validée qu’après vérification des services et de la supervision.
6. **Prévoir le rollback** : commandes de désactivation testées, sauvegarde de configuration, fenêtre de retour, point de décision et responsable du changement.

Les routeurs non SR, les frontières de domaine et les services qui dépendent de LDP/RSVP doivent être traités comme des cas de conception. Ne pas supposer qu’un label ou une policy traverse automatiquement toute frontière. La compatibilité doit être évaluée pour chaque service, chaque protocole de distribution et chaque chemin de transport.

## 23. Sécurité, gouvernance et validation avant production

Segment Routing donne davantage de possibilités pour exprimer des chemins, ce qui rend la gouvernance des politiques importante. Limiter qui peut créer ou modifier des SR Policies, protéger les canaux de gestion et de programmation, journaliser les changements et contrôler l’accès aux interfaces d’administration. Lorsqu’un contrôleur/PCE est utilisé, traiter son accès, son authentification, sa disponibilité et la cohérence de ses données de topologie comme des éléments critiques.

Une SR Policy doit être évaluée en fonction du trafic qu’elle peut influencer. Un chemin non attendu peut contourner un point de contrôle, modifier le point d’application de la QoS, ou concentrer la charge sur un lien. Les contraintes de sécurité doivent donc être exprimées explicitement dans le design : points de filtrage, limites de domaine, chemins autorisés, traitement des SIDs et validation des paquets entrant dans le domaine SR. Ne considère pas Segment Routing comme un mécanisme de chiffrement ou de contrôle d’accès à lui seul.

### Modèle minimal de revue de changement

- **Avant** : sauvegarder les configurations ; collecter l’état IGP, la reachability des loopbacks, le mapping des SIDs, les compteurs et une mesure de latence/perte de référence.
- **Pendant** : appliquer une étape à la fois ; confirmer les annonces attendues ; ne pas continuer si un SID ou un next-hop est absent ou incohérent.
- **Validation fonctionnelle** : tester plusieurs classes de trafic, les chemins aller et retour, la QoS, les MTU, les services VPN éventuels et le comportement d’ECMP.
- **Validation de résilience** : provoquer les pannes prévues uniquement dans le laboratoire ou la fenêtre approuvée ; mesurer convergence et pertes.
- **Après** : comparer aux critères d’acceptation, surveiller les compteurs, archiver la configuration et consigner les écarts.
- **Rollback** : déclencher le retour arrière si les seuils convenus sont dépassés ou si un comportement inattendu reste inexpliqué.

L’objectif d’une checklist n’est pas de remplacer l’analyse, mais d’éviter qu’une configuration apparemment correcte soit considérée comme réussie sans preuve dans le plan de données.

## 24. Références techniques

- [RFC 8402 — Segment Routing Architecture](https://www.rfc-editor.org/rfc/rfc8402.html) : architecture SR, SIDs, SRGB/SRLB, SR Policy et SR-MPLS/SRv6.
- [RFC 8665 — OSPF Extensions for Segment Routing](https://www.rfc-editor.org/rfc/rfc8665.html) : extensions SR pour OSPFv2.
- [RFC 8667 — IS-IS Extensions for Segment Routing](https://www.rfc-editor.org/rfc/rfc8667.html) : extensions SR pour IS-IS avec plan de données MPLS.
- [RFC 9256 — Segment Routing Policy Architecture](https://www.rfc-editor.org/rfc/rfc9256.html) : modèle de SR Policy.
- [Cisco Segment Routing Configuration Guide for IOS XE](https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/segment-routing/segment-routing-guide.html) : prise en charge et configuration selon les versions IOS XE.

**Note de compatibilité :** la syntaxe, les commandes de vérification, les capacités TI-LFA, la profondeur maximale de pile et le support des SR Policies varient selon l’équipement et la version logicielle. Utilise les guides correspondant à la plateforme réelle et réalise les essais dans un laboratoire avant une mise en production.
