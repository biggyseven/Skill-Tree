# IS-IS — Niveau Débutant

## Objectif du cours

Ce cours introduit **IS-IS (Intermediate System to Intermediate System)**, un protocole de routage dynamique à état de liens utilisé dans les réseaux IP, notamment dans les infrastructures d'opérateurs et les réseaux de grande taille. L’objectif n’est pas encore de maîtriser les optimisations avancées : il s’agit de comprendre son rôle, son vocabulaire, son fonctionnement, sa hiérarchie, son adressage propre et la manière de le mettre en place dans un petit laboratoire.

À la fin du cours, vous devez pouvoir :

- expliquer ce qu’est un protocole de routage dynamique et pourquoi IS-IS est un protocole à état de liens ;
- distinguer une aire de niveau 1 d’un domaine de niveau 2 ;
- lire les trois parties d’un NET et choisir un System ID unique ;
- décrire le rôle des messages Hello, LSP, CSNP et PSNP ;
- comprendre comment les routeurs construisent leur base d’état de liens et calculent les meilleurs chemins ;
- reconnaître le rôle du DIS sur un réseau multi-accès ;
- configurer une topologie simple sous Cisco IOS/IOS XE, puis vérifier les voisins et les routes ;
- diagnostiquer les causes habituelles d’une adjacency qui ne se forme pas.

## 1. Prérequis et vocabulaire essentiel

Il est utile de connaître les bases suivantes : adresse IPv4, masque ou préfixe CIDR, interface réseau, passerelle, table de routage et commandes de configuration d’un routeur. Le cours reste accessible si ces notions sont encore récentes : elles seront réutilisées dans les exemples.

| Terme | Signification simple |
|---|---|
| Routage dynamique | Des routeurs échangent des informations pour apprendre automatiquement les réseaux accessibles. |
| Routeur / IS | Dans le vocabulaire IS-IS, un routeur est un **Intermediate System (IS)**. |
| État de liens | Description des liens d’un routeur : voisins, interfaces ou segments et informations de coût. |
| Adjacency | Relation de voisinage établie entre deux routeurs IS-IS sur un lien. |
| LSP | Link State PDU/Packet : message qui décrit la connectivité annoncée par un routeur. Il ne faut pas le confondre avec le protocole de transport TCP. |
| LSDB | Link-State Database : base qui rassemble les informations d’état de liens reçues. |
| SPF | Shortest Path First : calcul des chemins à partir de la topologie connue. Il s’appuie sur l’algorithme de Dijkstra. |
| Aire (area) | Ensemble logique de routeurs qui partagent une zone d’adressage IS-IS pour le routage de niveau 1. |
| NET | Network Entity Title : identifiant configuré pour une instance IS-IS, qui contient l’adresse d’aire, le System ID et le sélecteur NSEL. |
| Metric / métrique | Coût associé à un lien ou chemin ; IS-IS utilise ces coûts pour choisir un itinéraire. |

## 2. Qu’est-ce qu’IS-IS ?

IS-IS est un protocole de routage **interne** (IGP, Interior Gateway Protocol). Il permet aux routeurs d’un même domaine administratif de découvrir leurs voisins, de partager des informations de topologie et de calculer des routes vers les réseaux annoncés.

Historiquement, IS-IS vient du monde OSI. La version dite **Integrated IS-IS** permet aussi d’acheminer des préfixes IP, notamment IPv4 et IPv6 selon les extensions et la plateforme. Le protocole n’est donc pas limité aux réseaux OSI historiques.

IS-IS appartient à la famille des protocoles **à état de liens**, comme OSPF. Chaque routeur décrit les liens qu’il connaît au moyen de LSP. Les routeurs d’un même niveau diffusent ces informations, construisent une base topologique et effectuent un calcul SPF pour déterminer les meilleurs chemins.

### 2.1 Pourquoi utiliser un protocole de routage dynamique ?

Prenons un réseau de trois routeurs. Si le réseau derrière le troisième routeur doit être joint depuis le premier, il est possible de configurer une route statique. Mais si plusieurs liens et plusieurs réseaux sont présents, maintenir toutes les routes à la main devient difficile. Avec IS-IS, les routeurs peuvent apprendre les réseaux annoncés par les autres routeurs et recalculer leurs chemins lorsque la topologie change.

Le protocole ne remplace pas les adresses IP ni le plan d’adressage. Il permet aux routeurs d’échanger et de calculer des informations de routage. Les interfaces doivent quand même être adressées et opérationnelles.

### 2.2 IS-IS en quelques étapes

1. Les interfaces sont activées et correctement adressées.
2. IS-IS envoie des messages Hello pour découvrir les routeurs accessibles sur les liens configurés.
3. Les routeurs compatibles établissent une adjacency.
4. Ils échangent les informations d’état de liens décrites dans les LSP.
5. Chaque routeur synchronise sa base d’état de liens avec ses voisins du niveau concerné.
6. L’algorithme SPF calcule les meilleurs chemins vers les destinations connues.
7. Les routes retenues sont installées dans la table de routage, sous réserve des règles de préférence de la plateforme.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 300" role="img" aria-labelledby="isis-flow-title isis-flow-desc">
  <title id="isis-flow-title">Fonctionnement général d’IS-IS</title>
  <desc id="isis-flow-desc">Sept étapes, de l’activation de l’interface jusqu’à l’installation des routes dans la table de routage.</desc>
  <defs>
    <marker id="isis-flow-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#4f8bd6"/></marker>
  </defs>
  <rect width="960" height="300" rx="18" fill="#0b1220"/>
  <text x="480" y="34" text-anchor="middle" fill="#f8fafc" font-size="21" font-weight="700">Le cycle IS-IS</text>
  <g font-family="Arial, sans-serif" font-size="14" text-anchor="middle">
    <g><rect x="30" y="68" width="205" height="67" rx="10" fill="#16243a" stroke="#4f8bd6"/><text x="132" y="94" fill="#93c5fd" font-weight="700">1. Interfaces</text><text x="132" y="115" fill="#e2e8f0">Adressées et actives</text></g>
    <g><rect x="265" y="68" width="205" height="67" rx="10" fill="#16243a" stroke="#4f8bd6"/><text x="367" y="94" fill="#93c5fd" font-weight="700">2. Hello</text><text x="367" y="115" fill="#e2e8f0">Découverte des voisins</text></g>
    <g><rect x="500" y="68" width="205" height="67" rx="10" fill="#16243a" stroke="#4f8bd6"/><text x="602" y="94" fill="#93c5fd" font-weight="700">3. Adjacency</text><text x="602" y="115" fill="#e2e8f0">Voisinage établi</text></g>
    <g><rect x="735" y="68" width="195" height="67" rx="10" fill="#16243a" stroke="#4f8bd6"/><text x="832" y="94" fill="#93c5fd" font-weight="700">4. LSP</text><text x="832" y="115" fill="#e2e8f0">Infos de topologie</text></g>
    <path d="M235 101 H260 M470 101 H495 M705 101 H730" stroke="#4f8bd6" stroke-width="2.5" fill="none" marker-end="url(#isis-flow-arrow)"/>
    <g><rect x="145" y="190" width="205" height="67" rx="10" fill="#18352e" stroke="#34d399"/><text x="247" y="216" fill="#6ee7b7" font-weight="700">5. Base LSDB</text><text x="247" y="237" fill="#e2e8f0">Topologie synchronisée</text></g>
    <g><rect x="390" y="190" width="205" height="67" rx="10" fill="#18352e" stroke="#34d399"/><text x="492" y="216" fill="#6ee7b7" font-weight="700">6. Calcul SPF</text><text x="492" y="237" fill="#e2e8f0">Meilleurs chemins</text></g>
    <g><rect x="635" y="190" width="205" height="67" rx="10" fill="#18352e" stroke="#34d399"/><text x="737" y="216" fill="#6ee7b7" font-weight="700">7. Routes</text><text x="737" y="237" fill="#e2e8f0">Installées si retenues</text></g>
    <path d="M832 135 V165 H247 V185 M350 223 H385 M595 223 H630" stroke="#34d399" stroke-width="2.5" fill="none" marker-end="url(#isis-flow-arrow)"/>
  </g>
</svg>

## 3. La hiérarchie IS-IS : niveau 1 et niveau 2

La hiérarchie est l’une des idées les plus importantes d’IS-IS. Elle permet de limiter la quantité de détails topologiques que certains routeurs doivent connaître.

### 3.1 Niveau 1 (L1)

Un routeur **L1** échange les informations de niveau 1 avec les autres routeurs L1 de **sa propre aire**. Il connaît la topologie de cette aire, mais n’a pas besoin de connaître chaque détail interne de toutes les autres aires.

Pour joindre une destination située en dehors de son aire, un routeur L1 utilise normalement un routeur capable de router au niveau 2. Le choix du routeur de sortie peut dépendre de la route de niveau 1, de la route par défaut injectée, des métriques et de l’implémentation.

### 3.2 Niveau 2 (L2)

Le niveau **L2** forme l’ossature inter-aires du domaine IS-IS. Les routeurs L2 échangent des informations de niveau 2 et calculent les chemins entre aires. Pour que les différentes aires puissent communiquer normalement, l’ensemble des routeurs et liens de niveau 2 doit former une topologie connectée.

L2 ne signifie pas « couche 2 Ethernet ». Ici, **Level 2** est un niveau de routage IS-IS. Il ne faut pas le confondre avec la couche 2 du modèle OSI.

### 3.3 Routeur L1/L2

Un routeur **L1/L2** participe aux deux niveaux : il apprend la topologie de son aire en L1 et participe à l’ossature L2. Il peut donc aider à faire communiquer une aire avec une autre.

Les plateformes peuvent utiliser des règles précises pour annoncer les préfixes entre niveaux. Au début, retenez surtout le rôle général : L1 = topologie de l’aire ; L2 = topologie inter-aires.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 400" role="img" aria-labelledby="isis-level-title isis-level-desc">
  <title id="isis-level-title">Exemple d’architecture IS-IS à deux aires</title>
  <desc id="isis-level-desc">L’aire 49.0001 contient R1 et R2, l’aire 49.0002 contient R3 et R4. Le lien R2-R3 participe au niveau 2. R2 et R3 sont des routeurs L1/L2.</desc>
  <defs><marker id="isis-level-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#64748b"/></marker></defs>
  <rect width="960" height="400" rx="18" fill="#0b1220"/>
  <text x="480" y="34" text-anchor="middle" font-size="21" fill="#f8fafc" font-weight="700">Les niveaux IS-IS</text>
  <rect x="35" y="65" width="390" height="275" rx="20" fill="#10243a" stroke="#60a5fa" stroke-width="2"/>
  <rect x="535" y="65" width="390" height="275" rx="20" fill="#123027" stroke="#34d399" stroke-width="2"/>
  <text x="230" y="94" text-anchor="middle" font-size="17" fill="#93c5fd" font-weight="700">Aire 49.0001</text>
  <text x="730" y="94" text-anchor="middle" font-size="17" fill="#6ee7b7" font-weight="700">Aire 49.0002</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <g><rect x="75" y="145" width="105" height="65" rx="10" fill="#1d3553" stroke="#93c5fd"/><text x="127" y="171" fill="#f8fafc" font-size="17" font-weight="700">R1</text><text x="127" y="193" fill="#bfdbfe" font-size="12">L1</text></g>
    <g><rect x="280" y="145" width="105" height="65" rx="10" fill="#263b3c" stroke="#6ee7b7"/><text x="332" y="171" fill="#f8fafc" font-size="17" font-weight="700">R2</text><text x="332" y="193" fill="#a7f3d0" font-size="12">L1/L2</text></g>
    <g><rect x="575" y="145" width="105" height="65" rx="10" fill="#263b3c" stroke="#6ee7b7"/><text x="627" y="171" fill="#f8fafc" font-size="17" font-weight="700">R3</text><text x="627" y="193" fill="#a7f3d0" font-size="12">L1/L2</text></g>
    <g><rect x="780" y="145" width="105" height="65" rx="10" fill="#1d3553" stroke="#93c5fd"/><text x="832" y="171" fill="#f8fafc" font-size="17" font-weight="700">R4</text><text x="832" y="193" fill="#bfdbfe" font-size="12">L1</text></g>
    <path d="M180 177 H275 M385 177 H570 M680 177 H775" stroke="#cbd5e1" stroke-width="3" fill="none"/>
    <text x="230" y="164" fill="#e2e8f0" font-size="12">L1 + L2</text>
    <text x="477" y="164" fill="#e2e8f0" font-size="12">L2 seulement</text>
    <text x="730" y="164" fill="#e2e8f0" font-size="12">L1 + L2</text>
    <rect x="78" y="250" width="305" height="54" rx="9" fill="#0b1728" stroke="#315274"/><text x="230" y="273" fill="#dbeafe" font-size="13">R1 et R2 partagent l’aire L1</text><text x="230" y="291" fill="#94a3b8" font-size="12">Ils échangent les détails L1 de l’aire</text>
    <rect x="578" y="250" width="305" height="54" rx="9" fill="#0b1d18" stroke="#27634e"/><text x="730" y="273" fill="#d1fae5" font-size="13">R3 et R4 partagent l’aire L1</text><text x="730" y="291" fill="#94a3b8" font-size="12">Ils échangent les détails L1 de l’aire</text>
    <text x="480" y="370" fill="#cbd5e1" font-size="13">Le lien inter-aires doit rester dans une ossature L2 connectée.</text>
  </g>
</svg>

**À retenir :** un routeur peut être L1, L2 ou L1/L2. Deux voisins peuvent former une adjacency L2 même si leurs adresses d’aire diffèrent, mais une adjacency L1 exige une compatibilité d’aire conformément aux règles IS-IS. Les possibilités exactes dépendent des niveaux activés sur chaque interface et sur chaque routeur.

### 3.4 Comparaison rapide

| Type de routeur | Informations L1 | Informations L2 | Rôle typique |
|---|---|---|---|
| L1 | Oui, pour son aire | Non | Route à l’intérieur d’une aire |
| L2 | Non, sauf configuration/implémentation particulière | Oui, pour l’ossature | Route entre aires |
| L1/L2 | Oui, pour son aire | Oui | Relie une aire à l’ossature inter-aires |

## 4. Le NET et le System ID

IS-IS n’identifie pas ses routeurs uniquement à partir d’une adresse IPv4 d’interface. Chaque instance IS-IS reçoit un **NET (Network Entity Title)**. Le NET reprend le format d’une adresse NSAP et se termine par le sélecteur **NSEL = 00** pour une adresse d’entité de réseau IS-IS.

Un NET usuel est composé de trois parties :

1. **Adresse d’aire** : identifie l’aire pour le fonctionnement L1.
2. **System ID** : identifiant de 6 octets utilisé pour identifier le routeur dans la topologie IS-IS.
3. **NSEL** : sélecteur d’entité, fixé à `00` dans un NET IS-IS courant.

### 4.1 Lire un NET

Exemple :

```text
49.0001.0000.0000.0001.00
```

On peut le découper ainsi :

```text
49.0001       . 0000.0000.0001 . 00
Adresse d’aire   System ID        NSEL
```

Dans cet exemple, l’adresse d’aire est `49.0001`, le System ID est `0000.0000.0001` et le NSEL est `00`.

Le préfixe `49` est très couramment utilisé dans les laboratoires et les réseaux privés pour les adresses d’aire IS-IS. Il ne s’agit pas d’une adresse IPv4 ni d’un sous-réseau IP. Les points sont des séparateurs de présentation utilisés pour rendre les groupes d’octets plus lisibles.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 275" role="img" aria-labelledby="isis-net-title isis-net-desc">
  <title id="isis-net-title">Décomposition d’un NET IS-IS</title>
  <desc id="isis-net-desc">Le NET 49.0001.0000.0000.0001.00 est divisé en adresse d’aire 49.0001, System ID 0000.0000.0001 et NSEL 00.</desc>
  <rect width="960" height="275" rx="18" fill="#0b1220"/>
  <text x="480" y="36" text-anchor="middle" font-size="21" font-family="Arial,sans-serif" fill="#f8fafc" font-weight="700">Comprendre le NET</text>
  <rect x="90" y="65" width="780" height="58" rx="10" fill="#16243a" stroke="#334155"/>
  <text x="480" y="101" text-anchor="middle" font-size="25" font-family="monospace" fill="#f8fafc">49.0001.0000.0000.0001.00</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <path d="M110 130 V151 H260 V130" stroke="#60a5fa" stroke-width="2.5" fill="none"/><path d="M270 130 V151 H710 V130" stroke="#34d399" stroke-width="2.5" fill="none"/><path d="M720 130 V151 H850 V130" stroke="#fbbf24" stroke-width="2.5" fill="none"/>
    <rect x="70" y="164" width="230" height="72" rx="10" fill="#142d4b" stroke="#60a5fa"/><text x="185" y="190" fill="#93c5fd" font-size="15" font-weight="700">Adresse d’aire</text><text x="185" y="216" fill="#f8fafc" font-size="19" font-family="monospace">49.0001</text>
    <rect x="365" y="164" width="250" height="72" rx="10" fill="#15372e" stroke="#34d399"/><text x="490" y="190" fill="#6ee7b7" font-size="15" font-weight="700">System ID (6 octets)</text><text x="490" y="216" fill="#f8fafc" font-size="19" font-family="monospace">0000.0000.0001</text>
    <rect x="680" y="164" width="210" height="72" rx="10" fill="#3b2c12" stroke="#fbbf24"/><text x="785" y="190" fill="#fcd34d" font-size="15" font-weight="700">NSEL</text><text x="785" y="216" fill="#f8fafc" font-size="19" font-family="monospace">00</text>
  </g>
</svg>

### 4.2 Règles pratiques de choix

- Le **System ID doit être unique** parmi les routeurs qui partagent le domaine/niveau pertinent. En pratique, attribuez un System ID unique à chaque routeur IS-IS dans tout le domaine pour éviter les collisions.
- Tous les routeurs d’une même aire L1 doivent avoir des adresses d’aire compatibles afin de former les adjacencies L1.
- Le NET n’est pas l’adresse IP d’une interface. Il s’agit de l’identifiant de l’instance IS-IS.
- Le NET doit respecter le format accepté par la plateforme. La notation et les limites exactes sont décrites dans la documentation du constructeur.
- Une erreur de System ID peut perturber la base de topologie et entraîner des conflits difficiles à diagnostiquer. Ne recopiez pas le NET d’un routeur sur un autre sans changer le System ID.

## 5. Comment IS-IS découvre les voisins

IS-IS utilise des messages appelés **IIH (IS-IS Hello)** pour découvrir les routeurs voisins sur une interface activée pour le protocole. Les paquets Hello servent aussi à maintenir le voisinage vivant. Ils ne transportent pas à eux seuls toute la topologie réseau.

Les conditions exactes pour former une adjacency varient selon le type de réseau et la plateforme, mais vérifiez en premier lieu :

- interface physiquement et administrativement opérationnelle ;
- IS-IS activé sur la bonne interface ;
- niveau commun activé sur le lien ;
- compatibilité d’aire pour un voisinage L1 ;
- paramètres Hello, authentification et MTU cohérents lorsque ces paramètres sont configurés ;
- prise en charge et configuration du type de réseau utilisé.

Les adresses IP des interfaces sont essentielles au trafic IP et au routage des préfixes, mais l’établissement du voisinage IS-IS n’est pas un échange TCP/UDP classique. IS-IS fonctionne directement au-dessus de la couche liaison avec ses propres unités de données de protocole. Cette conception est une différence importante avec des protocoles qui s’appuient sur des paquets IP.

### 5.1 Adjacency, table de voisins et routes : trois choses différentes

Il faut distinguer :

- **Voisin découvert** : un message Hello reçu peut montrer qu’un autre routeur est présent.
- **Adjacency établie** : les conditions sont remplies pour former le voisinage au niveau concerné.
- **Route apprise et installée** : après l’échange de la topologie et le calcul SPF, le routeur dispose d’un chemin vers un préfixe ; ce chemin doit encore être retenu et installé dans la table de routage.

Voir un voisin ne garantit donc pas que toutes les routes attendues sont présentes. De la même façon, une adjacency en état correct n’assure pas que toutes les interfaces et annonces de préfixes ont été configurées comme prévu.

## 6. Les principaux messages IS-IS

Pour comprendre le protocole, apprenez les quatre types de messages de base. Les noms complets et la façon dont les commandes d’affichage les présentent peuvent varier selon le constructeur.

| Message | Nom complet | Fonction de base |
|---|---|---|
| IIH | IS-IS Hello | Découvre les voisins et maintient l’adjacency. |
| LSP | Link State PDU | Annonce les liens et les préfixes connus par un routeur. Les LSP sont diffusés dans le niveau concerné. |
| CSNP | Complete Sequence Numbers PDU | Résume les LSP présents dans la base d’un routeur, utile notamment pour comparer/synchroniser la base sur un réseau multi-accès. |
| PSNP | Partial Sequence Numbers PDU | Demande ou acquitte des informations LSP spécifiques, selon le contexte et le type de réseau. |

### 6.1 Rôle des LSP

Un LSP contient des informations qui permettent aux autres routeurs de reconstruire la topologie connue de son émetteur : identifiant du routeur, voisins ou segments joignables, métriques et préfixes annoncés, selon les extensions et options utilisées.

Les LSP ne sont pas des paquets de données utilisateur. Ils appartiennent au **plan de contrôle** : ils servent à apprendre la topologie et calculer les routes. Le trafic utilisateur est ensuite transféré par le plan de données selon la table de routage construite.

### 6.2 Pourquoi faut-il synchroniser la LSDB ?

Si deux routeurs d’un même niveau ont des vues incompatibles de la topologie, ils peuvent calculer des routes différentes et le réseau peut fonctionner de manière imprévisible. IS-IS inclut des mécanismes de numérotation, de durée de vie et de synchronisation des LSP pour faire converger les bases.

La LSDB est la base de départ du calcul SPF. Elle représente les informations d’état de liens connues du routeur dans le niveau concerné ; elle n’est pas simplement une copie de la table de routage.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="isis-pdu-title isis-pdu-desc">
  <title id="isis-pdu-title">Échange des messages IS-IS</title>
  <desc id="isis-pdu-desc">Les Hello établissent le voisinage, les LSP décrivent la topologie, puis les CSNP et PSNP contribuent à comparer et synchroniser la base d’état de liens.</desc>
  <defs><marker id="isis-pdu-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#94a3b8"/></marker></defs>
  <rect width="960" height="350" rx="18" fill="#0b1220"/>
  <text x="480" y="33" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21" font-weight="700">Les échanges entre deux routeurs</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="95" y="65" width="210" height="65" rx="12" fill="#142d4b" stroke="#60a5fa"/><text x="200" y="91" fill="#93c5fd" font-size="17" font-weight="700">Routeur A</text><text x="200" y="113" fill="#e2e8f0" font-size="13">Adjacency + LSDB</text>
    <rect x="655" y="65" width="210" height="65" rx="12" fill="#15372e" stroke="#34d399"/><text x="760" y="91" fill="#6ee7b7" font-size="17" font-weight="700">Routeur B</text><text x="760" y="113" fill="#e2e8f0" font-size="13">Adjacency + LSDB</text>
    <path d="M305 84 H650" stroke="#60a5fa" stroke-width="2" fill="none" marker-end="url(#isis-pdu-arrow)"/><text x="480" y="76" fill="#bfdbfe" font-size="14" font-weight="700">IIH / Hello</text><text x="480" y="99" fill="#94a3b8" font-size="12">Découverte et maintien du voisinage</text>
    <path d="M655 116 H310" stroke="#34d399" stroke-width="2" fill="none" marker-end="url(#isis-pdu-arrow)"/><text x="480" y="138" fill="#a7f3d0" font-size="14" font-weight="700">LSP</text>
    <rect x="125" y="178" width="710" height="51" rx="10" fill="#172335" stroke="#334155"/><text x="480" y="199" fill="#f8fafc" font-size="15" font-weight="700">Synchronisation de la base d’état de liens</text><text x="480" y="217" fill="#cbd5e1" font-size="12">CSNP : résumé de base  •  PSNP : demande / acquittement partiel</text>
    <path d="M200 130 V170 M760 130 V170" stroke="#64748b" stroke-width="1.7" stroke-dasharray="5 5"/>
    <rect x="180" y="260" width="250" height="58" rx="10" fill="#102e27" stroke="#34d399"/><text x="305" y="284" fill="#6ee7b7" font-size="15" font-weight="700">LSDB cohérente</text><text x="305" y="303" fill="#e2e8f0" font-size="12">Topologie du niveau</text>
    <rect x="530" y="260" width="250" height="58" rx="10" fill="#102e27" stroke="#34d399"/><text x="655" y="284" fill="#6ee7b7" font-size="15" font-weight="700">Calcul SPF</text><text x="655" y="303" fill="#e2e8f0" font-size="12">Routes candidates</text>
    <path d="M430 289 H525" stroke="#34d399" stroke-width="2.4" fill="none" marker-end="url(#isis-pdu-arrow)"/>
  </g>
</svg>

## 7. Du LSP à la table de routage : le calcul SPF

IS-IS est un protocole à état de liens : au lieu d’annoncer uniquement « voici le prochain saut pour chaque réseau », les routeurs partagent des informations de topologie. Chaque routeur construit sa représentation de la topologie et exécute le calcul SPF pour déterminer les chemins de coût minimal.

### 7.1 Le graphe de topologie

Pour raisonner simplement, représentez chaque routeur comme un nœud et chaque lien comme une arête portant une métrique. Le coût d’un chemin est généralement la somme des coûts des liens empruntés. SPF recherche les chemins de coût total le plus faible vers les destinations connues.

Un coût plus faible n’est pas nécessairement synonyme de lien physiquement plus rapide. Le rapport entre capacité du lien et métrique dépend de la politique de métrique et de la configuration. Ne supposez pas que chaque interface reçoit automatiquement une valeur correspondant exactement à sa bande passante sans vérifier la plateforme.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 325" role="img" aria-labelledby="isis-spf-title isis-spf-desc">
  <title id="isis-spf-title">Exemple de calcul SPF</title>
  <desc id="isis-spf-desc">De R1 à R4, le chemin via R2 a un coût total de 15 et le chemin via R3 un coût total de 30. Le choix illustré est le chemin R1-R2-R4.</desc>
  <rect width="960" height="325" rx="18" fill="#0b1220"/>
  <text x="480" y="33" text-anchor="middle" fill="#f8fafc" font-size="21" font-family="Arial,sans-serif" font-weight="700">SPF choisit le coût total le plus faible</text>
  <g stroke-linecap="round" fill="none" font-family="Arial,sans-serif">
    <path d="M145 160 L370 95" stroke="#34d399" stroke-width="4"/><path d="M370 95 L650 160" stroke="#34d399" stroke-width="4"/>
    <path d="M145 160 L370 245" stroke="#64748b" stroke-width="3"/><path d="M370 245 L650 160" stroke="#64748b" stroke-width="3"/>
    <path d="M650 160 L820 160" stroke="#64748b" stroke-width="3"/>
  </g>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <g><circle cx="145" cy="160" r="30" fill="#16243a" stroke="#60a5fa" stroke-width="2.5"/><text x="145" y="166" fill="#f8fafc" font-size="16" font-weight="700">R1</text></g>
    <g><circle cx="370" cy="95" r="30" fill="#15372e" stroke="#34d399" stroke-width="2.5"/><text x="370" y="101" fill="#f8fafc" font-size="16" font-weight="700">R2</text></g>
    <g><circle cx="370" cy="245" r="30" fill="#16243a" stroke="#64748b" stroke-width="2.5"/><text x="370" y="251" fill="#f8fafc" font-size="16" font-weight="700">R3</text></g>
    <g><circle cx="650" cy="160" r="30" fill="#16243a" stroke="#60a5fa" stroke-width="2.5"/><text x="650" y="166" fill="#f8fafc" font-size="16" font-weight="700">R4</text></g>
    <g><rect x="800" y="130" width="115" height="60" rx="10" fill="#172335" stroke="#334155"/><text x="857" y="154" fill="#e2e8f0" font-size="14" font-weight="700">Réseau</text><text x="857" y="173" fill="#cbd5e1" font-size="12">destination</text></g>
    <text x="255" y="112" fill="#6ee7b7" font-size="14" font-weight="700">Coût 5</text><text x="510" y="112" fill="#6ee7b7" font-size="14" font-weight="700">Coût 10</text>
    <text x="250" y="225" fill="#cbd5e1" font-size="14">Coût 20</text><text x="510" y="225" fill="#cbd5e1" font-size="14">Coût 10</text>
    <rect x="175" y="275" width="610" height="31" rx="8" fill="#102e27" stroke="#27634e"/><text x="480" y="295" fill="#a7f3d0" font-size="14">Via R2 : 5 + 10 = 15  →  préféré à via R3 : 20 + 10 = 30</text>
  </g>
</svg>

Dans cet exemple pédagogique, les coûts sont fictifs et choisis pour illustrer le calcul. Dans un vrai réseau, les métriques proviennent de la configuration et des règles de métrique IS-IS utilisées.

### 7.2 Pourquoi les routes peuvent différer de la LSDB

La LSDB décrit la topologie apprise au niveau concerné. La table de routage contient les routes finalement installées. Plusieurs raisons peuvent expliquer une différence :

- le préfixe n’est pas annoncé dans les LSP ;
- une route n’est pas atteignable à partir de la topologie ;
- une route d’un autre protocole a une préférence administrative ou une priorité supérieure sur la plateforme ;
- la métrique ne rend pas le chemin préférable ;
- une politique de routage filtre ou modifie l’annonce ;
- l’interface de sortie ou le prochain saut est indisponible.

Il faut donc inspecter séparément les voisins, la base IS-IS et la table de routage.

## 8. Les métriques IS-IS

Une **métrique** représente le coût associé à un lien. SPF additionne les métriques le long des chemins candidats. En règle générale, une route de métrique cumulée plus faible est préférée parmi les routes comparées par le même calcul IS-IS.

Historiquement, IS-IS a défini des métriques étroites avec un espace de valeurs limité. Les extensions de **métriques larges (wide metrics)** permettent des valeurs plus importantes et sont largement utilisées dans les déploiements modernes. La configuration précise dépend du constructeur et de la version ; certains équipements recommandent de vérifier que les routeurs du domaine utilisent un mode de métrique compatible.

Pour un cours débutant, retenez trois choses :

1. la métrique est un **coût**, pas une distance physique directe ;
2. SPF compare le coût total des chemins ;
3. les valeurs et leur mode de calcul doivent être configurés et interprétés selon la plateforme.

### 8.1 Égalité de coût

Si plusieurs chemins ont un coût total égal, un routeur peut installer plusieurs chemins de coût égal (ECMP, Equal-Cost Multi-Path) selon la configuration et les possibilités de l’équipement. Le trafic peut alors être réparti entre plusieurs prochains sauts. Le comportement précis de partage de charge dépend de la plateforme et de sa configuration.

## 9. Réseaux Ethernet multi-accès et DIS

Sur un réseau multi-accès comme un segment Ethernet partagé par plusieurs routeurs, IS-IS peut élire un **DIS (Designated Intermediate System)** pour ce segment. Le DIS joue un rôle dans la représentation du réseau partagé dans la topologie et dans les mécanismes de synchronisation LSP.

Le DIS n’est pas simplement le « chef » qui décide de toutes les routes. Il ne remplace pas SPF et ne devient pas forcément le prochain saut de tous les paquets. Son rôle porte notamment sur le segment multi-accès et sa représentation dans l’état de liens.

Le DIS est élu pour chaque niveau concerné sur un réseau multi-accès. Il n’y a pas de DIS nécessaire sur un simple lien point-à-point entre deux routeurs. Selon les règles IS-IS et la plateforme, l’élection du DIS et le traitement d’un segment diffèrent de ceux d’OSPF : ne transposez pas automatiquement les règles ou les minuteries OSPF à IS-IS.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 335" role="img" aria-labelledby="isis-dis-title isis-dis-desc">
  <title id="isis-dis-title">Rôle du DIS sur un réseau Ethernet partagé</title>
  <desc id="isis-dis-desc">Trois routeurs sont raccordés au même segment Ethernet. R2 est illustré comme DIS pour ce segment ; les adjacencies et les informations de topologie restent des mécanismes IS-IS.</desc>
  <rect width="960" height="335" rx="18" fill="#0b1220"/>
  <text x="480" y="34" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21" font-weight="700">DIS sur un segment multi-accès</text>
  <rect x="125" y="125" width="710" height="85" rx="16" fill="#172335" stroke="#64748b" stroke-width="2"/>
  <text x="480" y="173" text-anchor="middle" fill="#cbd5e1" font-size="17" font-family="Arial,sans-serif" font-weight="700">Segment Ethernet partagé</text>
  <g stroke="#94a3b8" stroke-width="3" fill="none"><path d="M245 100 V125"/><path d="M480 100 V125"/><path d="M715 100 V125"/></g>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="180" y="48" width="130" height="52" rx="10" fill="#16243a" stroke="#60a5fa" stroke-width="2"/><text x="245" y="70" fill="#f8fafc" font-size="15" font-weight="700">R1</text><text x="245" y="88" fill="#bfdbfe" font-size="12">Voisin IS-IS</text>
    <rect x="415" y="42" width="130" height="58" rx="10" fill="#3b2c12" stroke="#fbbf24" stroke-width="2.5"/><text x="480" y="67" fill="#fef3c7" font-size="15" font-weight="700">R2</text><text x="480" y="86" fill="#fcd34d" font-size="12">DIS du segment</text>
    <rect x="650" y="48" width="130" height="52" rx="10" fill="#16243a" stroke="#60a5fa" stroke-width="2"/><text x="715" y="70" fill="#f8fafc" font-size="15" font-weight="700">R3</text><text x="715" y="88" fill="#bfdbfe" font-size="12">Voisin IS-IS</text>
    <rect x="175" y="240" width="610" height="57" rx="10" fill="#10243a" stroke="#334155"/><text x="480" y="263" fill="#e2e8f0" font-size="14" font-weight="700">Le DIS aide à représenter le segment dans la topologie</text><text x="480" y="282" fill="#94a3b8" font-size="12">Il ne remplace ni la LSDB ni le calcul SPF de chaque routeur.</text>
  </g>
</svg>

## 10. Configuration de base : laboratoire à trois routeurs

Cette partie présente un exemple de syntaxe de type Cisco IOS/IOS XE. Les commandes peuvent varier selon la famille d’équipement, la version logicielle et le mode IS-IS pris en charge. L’objectif est d’apprendre la logique de configuration ; validez toujours la syntaxe exacte dans la documentation du matériel utilisé.

### 10.1 Topologie du laboratoire

Trois routeurs en chaîne : R1 — R2 — R3. Ils partagent tous l’aire IS-IS `49.0001`. Chaque routeur annonce une loopback de test ; les liens entre routeurs sont des réseaux /30.

| Lien ou interface | Adresse IPv4 | Fonction |
|---|---|---|
| R1 G0/0 | `10.0.12.1/30` | Lien vers R2 |
| R2 G0/0 | `10.0.12.2/30` | Lien vers R1 |
| R2 G0/1 | `10.0.23.1/30` | Lien vers R3 |
| R3 G0/0 | `10.0.23.2/30` | Lien vers R2 |
| R1 Loopback0 | `192.0.2.1/32` | Préfixe de test annoncé par R1 |
| R2 Loopback0 | `192.0.2.2/32` | Préfixe de test annoncé par R2 |
| R3 Loopback0 | `192.0.2.3/32` | Préfixe de test annoncé par R3 |

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 295" role="img" aria-labelledby="isis-lab-title isis-lab-desc">
  <title id="isis-lab-title">Topologie du laboratoire IS-IS</title>
  <desc id="isis-lab-desc">Trois routeurs R1, R2 et R3 forment une chaîne. Les liens utilisent les sous-réseaux 10.0.12.0/30 et 10.0.23.0/30. Chaque routeur annonce une loopback de documentation.</desc>
  <rect width="960" height="295" rx="18" fill="#0b1220"/>
  <text x="480" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" fill="#f8fafc" font-weight="700">Lab : un seul domaine IS-IS</text>
  <rect x="58" y="59" width="844" height="200" rx="18" fill="#10243a" stroke="#315274" stroke-width="1.5" stroke-dasharray="7 5"/>
  <text x="480" y="82" text-anchor="middle" fill="#93c5fd" font-family="Arial,sans-serif" font-size="14" font-weight="700">Aire 49.0001 • exemple L1/L2</text>
  <g stroke="#94a3b8" stroke-width="3" fill="none"><path d="M265 151 H420"/><path d="M540 151 H695"/></g>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="145" y="113" width="120" height="76" rx="12" fill="#16243a" stroke="#60a5fa" stroke-width="2"/><text x="205" y="139" fill="#f8fafc" font-size="18" font-weight="700">R1</text><text x="205" y="159" fill="#bfdbfe" font-size="12">10.0.12.1</text><text x="205" y="176" fill="#93c5fd" font-size="11">Lo0 .1/32</text>
    <rect x="420" y="113" width="120" height="76" rx="12" fill="#16243a" stroke="#60a5fa" stroke-width="2"/><text x="480" y="139" fill="#f8fafc" font-size="18" font-weight="700">R2</text><text x="480" y="159" fill="#bfdbfe" font-size="12">.12.2 / .23.1</text><text x="480" y="176" fill="#93c5fd" font-size="11">Lo0 .2/32</text>
    <rect x="695" y="113" width="120" height="76" rx="12" fill="#16243a" stroke="#60a5fa" stroke-width="2"/><text x="755" y="139" fill="#f8fafc" font-size="18" font-weight="700">R3</text><text x="755" y="159" fill="#bfdbfe" font-size="12">10.0.23.2</text><text x="755" y="176" fill="#93c5fd" font-size="11">Lo0 .3/32</text>
    <text x="342" y="137" fill="#e2e8f0" font-size="12">10.0.12.0/30</text><text x="617" y="137" fill="#e2e8f0" font-size="12">10.0.23.0/30</text>
    <text x="480" y="222" fill="#cbd5e1" font-size="13">NET : 49.0001.0000.0000.000X.00</text><text x="480" y="241" fill="#94a3b8" font-size="12">X est différent pour chaque routeur (System ID unique).</text>
  </g>
</svg>

### 10.2 Règles avant de configurer

1. Configurez d’abord le nom d’hôte et les adresses IP.
2. Vérifiez que les interfaces sont `up/up` et que les voisins directs répondent par IP quand c’est attendu.
3. Choisissez une aire commune pour ce laboratoire et un NET distinct par routeur.
4. Activez IS-IS globalement, puis sur les interfaces qui doivent participer au routage.
5. Contrôlez la table des voisins, la base IS-IS et les routes apprises.

### 10.3 Exemple de configuration pour R1

```text
hostname R1
!
interface GigabitEthernet0/0
 description Lien vers R2
 ip address 10.0.12.1 255.255.255.252
 ip router isis LAB
 no shutdown
!
interface Loopback0
 ip address 192.0.2.1 255.255.255.255
 ip router isis LAB
!
router isis LAB
 net 49.0001.0000.0000.0001.00
 is-type level-1-2
 metric-style wide
```

### 10.4 Exemple de configuration pour R2

```text
hostname R2
!
interface GigabitEthernet0/0
 description Lien vers R1
 ip address 10.0.12.2 255.255.255.252
 ip router isis LAB
 no shutdown
!
interface GigabitEthernet0/1
 description Lien vers R3
 ip address 10.0.23.1 255.255.255.252
 ip router isis LAB
 no shutdown
!
interface Loopback0
 ip address 192.0.2.2 255.255.255.255
 ip router isis LAB
!
router isis LAB
 net 49.0001.0000.0000.0002.00
 is-type level-1-2
 metric-style wide
```

### 10.5 Exemple de configuration pour R3

```text
hostname R3
!
interface GigabitEthernet0/0
 description Lien vers R2
 ip address 10.0.23.2 255.255.255.252
 ip router isis LAB
 no shutdown
!
interface Loopback0
 ip address 192.0.2.3 255.255.255.255
 ip router isis LAB
!
router isis LAB
 net 49.0001.0000.0000.0003.00
 is-type level-1-2
 metric-style wide
```

**Remarque de plateforme :** sur certaines images IOS/IOS XE, la commande globale `clns routing` peut être requise pour activer le traitement CLNS/IS-IS. Sur d’autres plateformes, l’activation et les commandes exactes sont différentes. Ajoutez-la uniquement si la documentation de votre équipement la demande. Les noms d’interface (`GigabitEthernet0/0`, `Gi0/0`, etc.) sont également à adapter.

Dans ce laboratoire, `metric-style wide` est affiché pour illustrer un mode de métriques couramment utilisé. Vérifiez les exigences de compatibilité de la version logicielle et du reste du domaine avant d’appliquer ce paramètre dans un environnement réel.

### 10.6 Que fait chaque commande ?

| Commande | Rôle |
|---|---|
| `router isis LAB` | Crée ou sélectionne le processus IS-IS nommé `LAB` sur cette plateforme. |
| `net ...` | Définit le NET de l’instance ; le System ID doit être propre au routeur. |
| `is-type level-1-2` | Demande au routeur de participer aux niveaux L1 et L2. Les valeurs exactes acceptées peuvent varier. |
| `metric-style wide` | Configure l’utilisation de métriques larges sur les plateformes qui proposent cette syntaxe. |
| `ip router isis LAB` | Active l’instance IS-IS sur l’interface dans cet exemple IOS/IOS XE. |
| `no shutdown` | Active administrativement l’interface. |

L’activation d’IS-IS sur une interface ne remplace pas la configuration d’adresse IP. Inversement, une interface qui a une adresse IP ne participe pas automatiquement au routage IS-IS si le protocole n’est pas activé sur celle-ci ou selon la méthode de configuration propre à la plateforme.

## 11. Vérification après configuration

Ne considérez pas la configuration terminée uniquement parce que les commandes ont été acceptées. Vérifiez le fonctionnement à plusieurs niveaux.

### 11.1 Contrôles à effectuer

Les commandes d’affichage suivantes sont courantes dans les environnements Cisco, mais leurs noms et leur sortie peuvent différer selon la version :

```text
show isis neighbors
show isis database
show isis route
show ip route isis
show ip interface brief
show running-config
```

- `show isis neighbors` : confirme que les voisins sont formés et affiche notamment leur état et leur niveau selon l’équipement.
- `show isis database` : inspecte la base de LSP connue par le routeur.
- `show isis route` : montre les routes calculées ou associées à IS-IS lorsque la plateforme propose cette commande.
- `show ip route isis` : vérifie les routes IS-IS présentes dans la table de routage IPv4.
- `show ip interface brief` : contrôle rapidement l’état et l’adressage des interfaces IPv4.
- `show running-config` : permet de vérifier le NET, les commandes de routage et l’activation d’IS-IS sur les interfaces.

### 11.2 Tests de connectivité

Depuis R1, testez les adresses directement connectées puis les loopbacks des routeurs éloignés :

```text
ping 10.0.12.2
ping 192.0.2.2
ping 192.0.2.3
```

Un ping vers une adresse directement connectée teste d’abord le lien et l’adressage. Un ping vers la loopback de R3 teste davantage de choses : adjacency, propagation des informations de routage, calcul du chemin et présence des routes de retour. Un échec de ping ne prouve donc pas automatiquement qu’IS-IS est mal configuré : l’adresse cible, les filtres ICMP et les routes de retour comptent aussi.

### 11.3 Résultat attendu

Dans un laboratoire fonctionnel, R1 devrait former un voisinage avec R2, R2 avec R1 et R3, et R3 avec R2. Les bases d’état de liens doivent contenir les informations des routeurs et les préfixes de test. R1 doit pouvoir apprendre la loopback de R3, et inversement, si l’annonce de loopback est activée et qu’aucune politique ne filtre les routes.

Les noms d’état et la présentation exacte sont spécifiques à la plateforme. Le bon résultat se vérifie par la présence du voisin, des LSP attendus, des préfixes appris et d’une connectivité de bout en bout.

## 12. Dépannage de base

Quand une route attendue manque, évitez de modifier toutes les commandes au hasard. Procédez de l’interface vers le protocole, puis vers la topologie et les routes.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 455" role="img" aria-labelledby="isis-trouble-title isis-trouble-desc">
  <title id="isis-trouble-title">Arbre de diagnostic IS-IS débutant</title>
  <desc id="isis-trouble-desc">Un parcours de diagnostic examine l’interface, le voisinage, la base de liens et les routes dans cet ordre.</desc>
  <defs><marker id="isis-trouble-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#64748b"/></marker></defs>
  <rect width="960" height="455" rx="18" fill="#0b1220"/>
  <text x="480" y="33" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="21" font-weight="700">Dépanner dans le bon ordre</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="320" y="60" width="320" height="52" rx="10" fill="#16243a" stroke="#60a5fa"/><text x="480" y="82" fill="#93c5fd" font-size="15" font-weight="700">1. Interface active ?</text><text x="480" y="100" fill="#e2e8f0" font-size="12">État, câble, VLAN, sous-réseau IP</text>
    <path d="M480 112 V137" stroke="#64748b" stroke-width="2" marker-end="url(#isis-trouble-arrow)"/>
    <rect x="320" y="143" width="320" height="52" rx="10" fill="#16243a" stroke="#60a5fa"/><text x="480" y="165" fill="#93c5fd" font-size="15" font-weight="700">2. Voisin IS-IS présent ?</text><text x="480" y="183" fill="#e2e8f0" font-size="12">Interface activée, niveau et aire compatibles</text>
    <path d="M480 195 V220" stroke="#64748b" stroke-width="2" marker-end="url(#isis-trouble-arrow)"/>
    <rect x="320" y="226" width="320" height="52" rx="10" fill="#16243a" stroke="#60a5fa"/><text x="480" y="248" fill="#93c5fd" font-size="15" font-weight="700">3. LSP attendus dans la LSDB ?</text><text x="480" y="266" fill="#e2e8f0" font-size="12">Annonce du routeur et des préfixes</text>
    <path d="M480 278 V303" stroke="#64748b" stroke-width="2" marker-end="url(#isis-trouble-arrow)"/>
    <rect x="320" y="309" width="320" height="52" rx="10" fill="#15372e" stroke="#34d399"/><text x="480" y="331" fill="#6ee7b7" font-size="15" font-weight="700">4. Route installée ?</text><text x="480" y="349" fill="#e2e8f0" font-size="12">SPF, métrique, politique, préférence</text>
    <path d="M320 169 H165 V194" stroke="#f87171" stroke-width="1.8" fill="none" stroke-dasharray="5 4"/><path d="M320 252 H165 V277" stroke="#f87171" stroke-width="1.8" fill="none" stroke-dasharray="5 4"/><path d="M320 335 H165 V360" stroke="#f87171" stroke-width="1.8" fill="none" stroke-dasharray="5 4"/>
    <rect x="45" y="194" width="240" height="48" rx="8" fill="#3b1d25" stroke="#f87171"/><text x="165" y="214" fill="#fecaca" font-size="13" font-weight="700">Si échec au niveau 2</text><text x="165" y="230" fill="#fca5a5" font-size="11">Contrôler Hello / compatibilité</text>
    <rect x="45" y="277" width="240" height="48" rx="8" fill="#3b1d25" stroke="#f87171"/><text x="165" y="297" fill="#fecaca" font-size="13" font-weight="700">Si échec au niveau 3</text><text x="165" y="313" fill="#fca5a5" font-size="11">Contrôler annonces et niveaux</text>
    <rect x="45" y="360" width="240" height="48" rx="8" fill="#3b1d25" stroke="#f87171"/><text x="165" y="380" fill="#fecaca" font-size="13" font-weight="700">Si échec au niveau 4</text><text x="165" y="396" fill="#fca5a5" font-size="11">Contrôler métrique et politiques</text>
    <rect x="690" y="194" width="225" height="214" rx="12" fill="#111c2d" stroke="#334155"/><text x="802" y="220" fill="#e2e8f0" font-size="14" font-weight="700">Autres vérifications</text><text x="712" y="248" fill="#cbd5e1" text-anchor="start" font-size="12">• System ID unique</text><text x="712" y="273" fill="#cbd5e1" text-anchor="start" font-size="12">• NET correct</text><text x="712" y="298" fill="#cbd5e1" text-anchor="start" font-size="12">• MTU et authentification</text><text x="712" y="323" fill="#cbd5e1" text-anchor="start" font-size="12">• Timers et niveau commun</text><text x="712" y="348" fill="#cbd5e1" text-anchor="start" font-size="12">• Interface passive ?</text><text x="712" y="373" fill="#cbd5e1" text-anchor="start" font-size="12">• Préfixe annoncé ?</text>
  </g>
</svg>

### 12.1 Tableau de dépannage

| Symptôme | Causes possibles | Vérifications de départ |
|---|---|---|
| Aucun voisin | Interface inactive, IS-IS non activé sur le lien, niveau non commun, Hello non reçus, mauvaise encapsulation ou type d’interface non pris en charge. | État de l’interface, configuration d’interface, liste des voisins, journaux. |
| Adjacency L1 absente mais L2 présente | Adresses d’aire L1 incompatibles ou niveau L1 non activé sur un côté. | NET de chaque routeur, type de routeur et niveaux activés sur le lien. |
| Voisin présent, route absente | Préfixe non annoncé, mauvais niveau, base incomplète, métrique ou politique, route rejetée par la table. | Base IS-IS, routes IS-IS calculées, table de routage et configuration des interfaces/loopbacks. |
| Une loopback n’est pas joignable | Loopback non incluse dans IS-IS, annonce filtrée, route de retour manquante ou test ICMP filtré. | Activation IS-IS sur la loopback, route à destination et route de retour. |
| Les voisins apparaissent puis disparaissent | Perte de paquets Hello, instabilité du lien, MTU ou paramètres incohérents, charge ou défaut matériel. | Compteurs d’interface, journaux, compteurs d’erreurs, timers et stabilité physique. |
| Conflit ou comportement étrange autour d’un routeur | System ID dupliqué ou NET mal configuré. | Comparer les NET et s’assurer que chaque System ID est distinct. |
| Communication inter-aires impossible | Ossature L2 non connectée ou annonces nécessaires non propagées entre niveaux. | Adjacencies L2 sur tout le domaine, routeurs L1/L2, routes de niveau 2 et règles d’annonce. |

### 12.2 La méthode « quatre couches de vérification »

Pour un débutant, cette méthode évite de confondre symptômes et causes :

**Couche 1 — Le lien :** l’interface est-elle active ? L’adressage IP est-il cohérent ? Le segment est-il accessible ?

**Couche 2 — Le voisinage :** l’instance IS-IS est-elle activée sur la bonne interface ? Les niveaux, l’aire, les timers, l’authentification et les autres paramètres compatibles permettent-ils d’établir l’adjacency ?

**Couche 3 — La topologie :** le routeur voit-il les LSP de ses voisins et les préfixes attendus ? Les informations sont-elles présentes dans la base au bon niveau ?

**Couche 4 — Le transfert :** la route est-elle calculée et installée ? Le prochain saut est-il valide ? Le chemin retour existe-t-il ? Des ACL ou d’autres politiques empêchent-elles le trafic ?

## 13. Bonnes pratiques et erreurs fréquentes

### Bonnes pratiques

- Établissez un plan NET avant de configurer les équipements ; documentez l’aire et le System ID de chaque routeur.
- Utilisez un System ID unique pour chaque routeur de votre domaine IS-IS.
- Activez le protocole uniquement sur les interfaces qui doivent participer au routage. Utilisez une configuration passive pour une interface de préfixe utilisateur lorsque la plateforme et le besoin le justifient, tout en vérifiant que le préfixe reste annoncé comme attendu.
- Gardez des métriques cohérentes et vérifiez le mode de métrique sur tous les équipements concernés.
- Validez les voisins, la LSDB et la table de routage après chaque changement significatif.
- Documentez les niveaux par routeur et par lien dans les architectures multi-aires.
- Avant une modification d’un réseau de production, utilisez une fenêtre de changement et un plan de retour arrière.

### Erreurs fréquentes chez les débutants

1. **Confondre le NET et l’adresse IP.** Le NET identifie l’instance IS-IS ; les interfaces ont toujours besoin de leur propre configuration IP.
2. **Dupliquer le System ID.** Un copier-coller sans changement de l’identifiant peut provoquer des collisions.
3. **Croire qu’un voisin signifie que toutes les routes sont présentes.** L’adjacency, la LSDB et la table de routage sont des états différents.
4. **Confondre Level 2 et couche 2.** Le niveau 2 d’IS-IS est un niveau de routage, pas une référence à Ethernet.
5. **Croire que l’adresse IP détermine automatiquement l’aire IS-IS.** Le plan IP et l’adresse d’aire IS-IS sont distincts, même s’ils peuvent être conçus de manière cohérente.
6. **Comparer des métriques sans vérifier leur mode.** Les anciennes métriques étroites et les wide metrics n’ont pas les mêmes capacités.
7. **Modifier plusieurs paramètres en même temps.** Cela rend l’origine d’une panne difficile à isoler.
8. **Oublier la route de retour.** Un ping peut échouer même si le trajet aller existe.

## 14. Mini-laboratoire guidé

Effectuez les tâches dans l’ordre. Notez vos observations au lieu de vous contenter de copier les commandes.

### Étape A — Adressage

1. Configurez les adresses des liens de R1, R2 et R3 selon le tableau du laboratoire.
2. Configurez une loopback sur chaque routeur.
3. Vérifiez l’état `up/up` et testez les pings entre voisins directement connectés.

**Question de contrôle :** si R1 ne peut pas joindre `10.0.12.2`, est-il utile de chercher d’abord un problème de calcul SPF ? Pourquoi ?

### Étape B — Activation d’IS-IS

1. Attribuez un NET différent à chaque routeur avec la même adresse d’aire `49.0001`.
2. Configurez le même nom de processus dans cet exemple (`LAB`) sur chaque routeur.
3. Activez IS-IS sur les interfaces inter-routeurs et sur les loopbacks destinées à être annoncées.
4. Contrôlez la présence des voisins.

**Question de contrôle :** qu’est-ce qui doit rester unique dans les trois NET, et qu’est-ce qui doit être cohérent pour former une adjacency L1 ?

### Étape C — Routes et connectivité

1. Inspectez la LSDB depuis R1 et identifiez les LSP des autres routeurs.
2. Consultez la table IPv4 et recherchez la route vers `192.0.2.3/32`.
3. Testez le ping de R1 vers `192.0.2.3` puis vers `192.0.2.2`.
4. Répétez les vérifications depuis R3.

**Question de contrôle :** si le voisin R2 est présent mais que `192.0.2.3/32` n’apparaît pas sur R1, quelles sont les deux premières informations que vous inspectez ?

### Étape D — Panne volontaire

Dans un environnement de laboratoire uniquement, supprimez temporairement l’activation IS-IS sur l’une des interfaces inter-routeurs, ou désactivez l’interface. Observez ce qui change dans la table des voisins, la LSDB et la table de routage. Rétablissez ensuite la configuration initiale.

**Objectif :** apprendre à relier une action précise à ses effets observables. N’effectuez pas cette manipulation sur un réseau de production.

## 15. Quiz de validation

Répondez sans relire les sections précédentes, puis vérifiez le corrigé.

### Questions

**1. IS-IS est principalement :**

A. Un protocole de routage statique  
B. Un protocole de routage interne à état de liens  
C. Un protocole de résolution d’adresse MAC  
D. Un protocole de transport fiable au-dessus de TCP

**2. Quel est le rôle principal des messages IIH ?**

A. Envoyer les données applicatives  
B. Découvrir et maintenir les voisins IS-IS  
C. Remplacer la table de routage IP  
D. Chiffrer les paquets utilisateurs

**3. À quoi sert un LSP ?**

A. À décrire des informations de topologie et de reachability  
B. À attribuer des adresses IP aux clients  
C. À résoudre un nom DNS  
D. À établir une session TCP

**4. Quelle est la fonction générale du niveau L1 ?**

A. Router uniquement entre domaines administratifs distincts  
B. Décrire et utiliser la topologie au sein d’une aire  
C. Gérer les VLAN de couche 2  
D. Remplacer le niveau L2

**5. Quel est le rôle général de L2 ?**

A. Former l’ossature de routage entre aires  
B. Distribuer les adresses DHCP  
C. Transporter les trames Ethernet uniquement  
D. Remplacer toutes les métriques par des adresses IP

**6. Dans le NET `49.0001.0000.0000.0001.00`, que représente `0000.0000.0001` ?**

A. L’adresse IPv4 de R1  
B. Le System ID  
C. Le masque de sous-réseau  
D. Le NSEL

**7. Quelle valeur de NSEL est couramment utilisée à la fin d’un NET IS-IS ?**

A. `FF`  
B. `01`  
C. `00`  
D. `255.255.255.0`

**8. Pourquoi le System ID doit-il être unique ?**

A. Pour identifier distinctement les routeurs dans le domaine IS-IS  
B. Pour déterminer le masque IPv4 automatiquement  
C. Pour permettre l’utilisation de DHCP  
D. Pour choisir un VLAN natif

**9. Quel message résume les LSP présents dans une base, notamment pour faciliter la synchronisation sur un réseau multi-accès ?**

A. IIH  
B. CSNP  
C. ARP  
D. DHCPACK

**10. Que fait l’algorithme SPF ?**

A. Il chiffre les LSP  
B. Il calcule les chemins à partir de la topologie et des métriques  
C. Il attribue un NET à chaque routeur  
D. Il remplace les Hello

**11. Le DIS est principalement associé :**

A. À l’élection d’un routeur DNS  
B. À un segment multi-accès tel qu’un réseau Ethernet partagé  
C. À la résolution de noms de domaine  
D. À la configuration d’un masque de sous-réseau

**12. Un voisin IS-IS est visible, mais une route attendue est absente. Quelle conclusion est correcte ?**

A. Le routage fonctionne nécessairement pour tous les préfixes  
B. Il faut vérifier les LSP, l’annonce du préfixe, la LSDB et la table de routage  
C. Il faut obligatoirement changer les adresses IP  
D. Il faut supprimer tous les NET

**13. Le NET remplace-t-il l’adresse IP de l’interface ?**

A. Oui  
B. Non

**14. Si deux chemins ont des métriques cumulées de 15 et 30, lequel SPF préfère-t-il normalement pour la même destination ?**

A. Le chemin de coût 30  
B. Le chemin de coût 15  
C. Toujours celui qui possède le plus de routeurs  
D. Impossible de comparer deux coûts

**15. Pour diagnostiquer une absence de route, quelle progression est la plus méthodique ?**

A. Modifier tous les paramètres en même temps  
B. Vérifier le lien, le voisinage, la LSDB, puis la route installée  
C. Redémarrer tous les routeurs immédiatement  
D. Changer l’aire sans inspecter les voisins

### Corrigé commenté

| N° | Réponse | Explication |
|---:|---|---|
| 1 | B | IS-IS est un IGP à état de liens. |
| 2 | B | Les IIH servent à découvrir et maintenir les adjacencies. |
| 3 | A | Les LSP diffusent des informations d’état de liens. |
| 4 | B | L1 concerne la topologie interne à une aire. |
| 5 | A | L2 constitue l’ossature de routage inter-aires. |
| 6 | B | Le groupe du milieu est le System ID dans cet exemple de NET. |
| 7 | C | Le NSEL est couramment `00` dans un NET IS-IS. |
| 8 | A | Le System ID identifie le routeur dans la topologie IS-IS ; évitez toute duplication. |
| 9 | B | CSNP signifie Complete Sequence Numbers PDU. |
| 10 | B | SPF calcule les chemins de coût minimal à partir de la LSDB. |
| 11 | B | Le DIS intervient sur les réseaux multi-accès. |
| 12 | B | Une adjacency ne garantit pas que chaque préfixe est annoncé et installé. |
| 13 | B | NET et adressage IP ont des rôles distincts. |
| 14 | B | À critères comparables, le coût total le plus faible est normalement préféré. |
| 15 | B | Cette séquence isole les causes sans modifier la configuration au hasard. |

## 16. Glossaire récapitulatif

- **Adjacency :** relation de voisinage établie entre deux routeurs IS-IS.
- **Area / aire :** regroupement logique des routeurs au niveau 1.
- **CSNP :** PDU qui fournit un résumé des LSP présents dans la base.
- **DIS :** routeur désigné pour certains rôles de topologie/synchronisation sur un segment multi-accès.
- **IGP :** protocole de routage utilisé au sein d’un domaine administratif.
- **IIH :** Hello IS-IS, utilisé pour détecter et maintenir les voisins.
- **IS :** Intermediate System, terme OSI pour un routeur dans IS-IS.
- **L1 :** niveau de routage au sein d’une aire.
- **L2 :** niveau qui interconnecte les aires dans le domaine IS-IS.
- **L1/L2 :** routeur qui participe aux deux niveaux.
- **LSDB :** base de données des informations d’état de liens.
- **LSP :** message d’état de liens qui annonce la connectivité connue.
- **Metric / métrique :** coût utilisé pour comparer les chemins.
- **NET :** adresse/identifiant de l’instance IS-IS avec adresse d’aire, System ID et NSEL.
- **NSEL :** octet sélecteur, couramment `00` pour un NET IS-IS.
- **PSNP :** PDU portant des informations partielles de séquence, utilisées notamment pour demander ou acquitter des LSP spécifiques.
- **SPF :** calcul des plus courts chemins à partir de la topologie et des métriques.
- **System ID :** identifiant du routeur incorporé au NET.
- **Wide metrics :** format de métrique plus étendu que les métriques historiques étroites.

## 17. Ce qu’il faut absolument retenir

1. **IS-IS est un protocole de routage dynamique à état de liens.** Il apprend la topologie, construit une LSDB et calcule les meilleurs chemins avec SPF.
2. **Les IIH créent et maintiennent les voisinages.** Les LSP annoncent les informations de topologie ; CSNP et PSNP participent aux mécanismes de synchronisation.
3. **L1 fonctionne au sein d’une aire ; L2 relie les aires.** Un routeur L1/L2 participe aux deux niveaux.
4. **Le NET n’est pas une adresse IP.** Il comprend une adresse d’aire, un System ID unique et un NSEL, couramment `00`.
5. **Voisinage, LSDB et table de routage sont trois vérifications différentes.** Une route absente doit être investiguée à chaque étape.
6. **La configuration dépend de la plateforme.** Vérifiez toujours la syntaxe, les niveaux, les métriques et les commandes d’affichage propres à votre version.

## Références techniques

Ces références servent à approfondir ou à vérifier les notions présentées. Les exemples de configuration de ce cours sont volontairement simplifiés pour l’apprentissage et doivent être adaptés à la plateforme utilisée.

- [RFC 1195 — Use of OSI IS-IS for routing in TCP/IP and dual environments](https://www.rfc-editor.org/rfc/rfc1195.html) — principes d’Integrated IS-IS et routage IP.
- [Cisco — IS-IS Overview and Basic Configuration](https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-routing/b-ip-routing/m_irs-ovrvw-cf.html) — vue d’ensemble, niveaux et NET.
- [Cisco — IS-IS Configuration Guide](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr3-fwd/isis/is-is-configuration-guide/is-is.html) — exemple de configuration, `net` et niveaux.
- [RFC 5302 — Domain-wide Prefix Distribution with Two-Level IS-IS](https://www.rfc-editor.org/rfc/rfc5302.html) — interaction des niveaux et distribution des préfixes.
