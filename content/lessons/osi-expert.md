# Le modèle OSI & TCP/IP — Ingénierie et diagnostic expert

> **Niveau :** Expert  
> **Prérequis :** maîtrise du routage IPv4/IPv6, des VLAN, de TCP/UDP, de DNS, de la MTU et des principes de Wireshark.  
> **Objectif :** expliquer un incident réseau à partir de preuves, distinguer le comportement des protocoles de celui des équipements intermédiaires et produire un diagnostic reproductible.


## Sommaire

1. Limites et valeur des modèles OSI et TCP/IP
2. Plans de données, de contrôle et de gestion
3. Encapsulation avancée et points de terminaison
4. Routage multi-sauts et asymétrie
5. NAT, proxys et tunnels
6. MTU de chemin, PMTUD et MSS
7. TCP : séquences, retransmissions et fenêtres
8. Wireshark : limites et méthodes d’analyse
9. Sécurité et observation multi-couches
10. Démarche de diagnostic expert
11. Laboratoires avancés
12. Exercices et corrigés
13. Modèle de rapport d’incident
14. Glossaire technique


# 1. La valeur et les limites des modèles OSI et TCP/IP

OSI et TCP/IP sont des outils pour raisonner sur les communications, pas des descriptions parfaites de chaque implémentation logicielle et matérielle.

Le modèle OSI distingue sept couches conceptuelles. Le modèle TCP/IP regroupe certaines de ces fonctions et met l’accent sur les protocoles utilisés pour construire les communications en réseau.

Dans un réseau actuel, une même fonction peut être répartie sur plusieurs composants.

Exemples :

- Une application peut utiliser une bibliothèque TLS pour sécuriser les échanges.
- Un proxy peut terminer une connexion TCP, déchiffrer une requête autorisée, puis ouvrir une seconde connexion.
- Un équipement de sécurité peut appliquer simultanément des règles IP, TCP, TLS et applicatives.
- Un tunnel peut ajouter une nouvelle enveloppe IP autour d’un paquet déjà encapsulé.
- Un répartiteur de charge peut fonctionner au niveau IP/transport ou comprendre le protocole applicatif.
- Un mécanisme de virtualisation peut ajouter des interfaces, des commutateurs virtuels et plusieurs points de filtrage.

La bonne question n’est donc pas seulement : « À quelle couche appartient cet équipement ? »

Il faut également demander :

- Quelles informations examine-t-il ?
- Quelles informations modifie-t-il ?
- Termine-t-il une connexion ou se contente-t-il de transférer le trafic ?
- Maintient-il un état ?
- Où ses décisions sont-elles visibles ?
- Quel point d’observation permet de confirmer son rôle ?

## 1.1 Deux connexions applicatives peuvent masquer plusieurs flux réseau

Un client peut ouvrir une connexion vers un proxy. Le proxy peut ensuite ouvrir une autre connexion vers le serveur.

Le client et le serveur paraissent communiquer au niveau applicatif, mais il existe alors deux connexions de transport distinctes.

Les numéros de séquence TCP du premier flux ne sont pas les numéros de séquence TCP du second. Les ports source peuvent différer. Les adresses IP visibles sur chaque liaison peuvent aussi différer.

Cette distinction est essentielle dans une investigation : l’absence d’un segment identique de part et d’autre du proxy ne prouve pas une perte.

## 1.2 Les couches servent à localiser une responsabilité

Une panne physique peut empêcher une communication avant même qu’un paquet atteigne la couche IP.

À l’inverse, une erreur HTTP peut apparaître alors que les couches physiques, liaison, réseau, transport et sécurité ont suffisamment fonctionné pour transmettre une requête et renvoyer une réponse.

Une analyse rigoureuse recherche le point où le comportement observé diverge de celui attendu. Elle ne suppose pas qu’une seule couche explique toujours toute la panne.


# 2. Plans de données, de contrôle et de gestion

En ingénierie réseau, il est utile de distinguer trois plans.

## 2.1 Plan de données

Le plan de données traite le transfert effectif du trafic.

Exemples :

- transfert d’une trame par un commutateur ;
- traitement d’un paquet IP par un routeur ;
- filtrage d’un paquet par une règle installée ;
- transfert d’un flux à travers une interface ;
- application d’une traduction NAT à un paquet correspondant à un état.

Lorsqu’un trafic est interrompu, il faut comprendre si le plan de données a reçu le paquet, l’a accepté et a tenté de le transmettre.

## 2.2 Plan de contrôle

Le plan de contrôle participe à l’établissement et à la mise à jour des informations permettant au réseau de fonctionner.

Exemples :

- apprentissage dynamique de routes ;
- protocoles de routage ;
- Spanning Tree Protocol ;
- mécanismes de découverte de voisins ;
- protocoles de contrôle propres aux équipements.

Une table de routage incorrecte peut empêcher le bon transfert même si les interfaces sont physiquement opérationnelles.

À l’inverse, la présence d’une route ne prouve pas que toutes les règles du plan de données autorisent le transfert.

## 2.3 Plan de gestion

Le plan de gestion concerne la configuration, la supervision et l’administration des équipements.

Exemples :

- interface d’administration ;
- API de configuration ;
- télémétrie ;
- journaux ;
- sauvegarde de configuration ;
- collecte des compteurs d’interface.

Un équipement peut être inaccessible à son interface d’administration tout en continuant à transférer le trafic. La panne du plan de gestion ne correspond donc pas systématiquement à une panne du plan de données.

## 2.4 Conséquence pour l’investigation

Séparez toujours les questions suivantes :

1. L’équipement est-il joignable pour l’administration ?
2. Ses interfaces et voisins sont-ils dans l’état attendu ?
3. Sa table de transfert contient-elle les informations nécessaires ?
4. Le paquet est-il reçu sur le point d’entrée ?
5. Le paquet est-il autorisé et transmis sur la sortie ?
6. Le destinataire reçoit-il ce paquet ?
7. L’application traite-t-elle correctement la requête ?

Ces questions ne sont pas équivalentes. Elles réduisent le risque de conclure à tort qu’un équipement fonctionne complètement parce qu’un seul test réussit.


# 3. Encapsulation avancée et points de terminaison

L’encapsulation représente la façon dont différents protocoles ajoutent ou retirent des informations nécessaires à la transmission.

Une analyse avancée doit distinguer l’enveloppe extérieure de l’enveloppe intérieure.

## 3.1 Encapsulation classique

Un flux de données peut être représenté comme suit :

```text
Données applicatives
└── Données protégées ou transformées, selon le protocole
    └── Segment TCP ou datagramme UDP
        └── Paquet IP
            └── Trame de liaison
                └── Transmission physique
```

Cette hiérarchie est conceptuelle. Les détails changent selon le protocole, le transport et les mécanismes de sécurité utilisés.

## 3.2 Encapsulation de tunnel

Un tunnel transporte un paquet au moyen d’un autre mécanisme de transmission. Selon la technologie, il peut ajouter de nouveaux en-têtes IP, UDP, Ethernet ou d’autres informations.

Exemple conceptuel :

```text
Paquet IP intérieur
└── En-tête de tunnel
    └── Paquet IP extérieur
        └── Trame du lien de transport
```

Les en-têtes extérieurs servent à acheminer le trafic vers le point de terminaison du tunnel. Le paquet intérieur peut représenter la communication entre les machines originales.

Le point de terminaison retire l’enveloppe du tunnel afin de retrouver le paquet intérieur. Certains tunnels appliquent également chiffrement, authentification ou contrôles d’intégrité.

## 3.3 SVG animé — Encapsulation d’un tunnel

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 420" role="img" aria-labelledby="tun3-title tun3-desc">
<title id="tun3-title">Encapsulation d'un paquet dans un tunnel</title>
<desc id="tun3-desc">Le paquet intérieur est placé dans une enveloppe extérieure au point d'entrée du tunnel. Au point de sortie, l'enveloppe extérieure est retirée. Une animation distincte souligne successivement les deux enveloppes.</desc>
<rect width="960" height="420" rx="18" fill="#f8fafc"/>
<text x="28" y="38" fill="#0f172a" font-family="Arial,sans-serif" font-size="23" font-weight="700">Tunnel : enveloppe extérieure et paquet intérieur</text>
<g font-family="Arial,sans-serif">
  <rect x="35" y="110" width="190" height="120" rx="12" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="130" y="145" text-anchor="middle" font-size="18" font-weight="700" fill="#1e3a8a">Site A</text>
  <text x="130" y="173" text-anchor="middle" font-size="14" fill="#1e3a8a">Paquet original</text>
  <text x="130" y="197" text-anchor="middle" font-size="13" fill="#1e3a8a">Source → destination</text>
  <rect x="345" y="78" width="270" height="185" rx="16" fill="#fee2e2" stroke="#b91c1c" stroke-width="3"/>
  <text x="480" y="108" text-anchor="middle" font-size="18" font-weight="700" fill="#991b1b">Tunnel</text>
  <rect x="390" y="139" width="180" height="70" rx="9" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="480" y="168" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">Paquet intérieur</text>
  <text x="480" y="190" text-anchor="middle" font-size="13" fill="#1e3a8a">Adresses originales</text>
  <rect x="340" y="73" width="280" height="195" rx="18" fill="none" stroke="#dc2626" stroke-width="4">
    <animate attributeName="stroke-opacity" values="0.3;1;0.3" dur="3.5s" repeatCount="indefinite"/>
  </rect>
  <rect x="735" y="110" width="190" height="120" rx="12" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="830" y="145" text-anchor="middle" font-size="18" font-weight="700" fill="#166534">Site B</text>
  <text x="830" y="173" text-anchor="middle" font-size="14" fill="#166534">Paquet décapsulé</text>
  <text x="830" y="197" text-anchor="middle" font-size="13" fill="#166534">Livraison locale</text>
  <path d="M225 170 H332" stroke="#2563eb" stroke-width="4" stroke-dasharray="12 9"><animate attributeName="stroke-dashoffset" values="0;-42" dur="1.4s" repeatCount="indefinite"/></path>
  <path d="M320 160 l12 10 -12 10" fill="none" stroke="#2563eb" stroke-width="3"/>
  <path d="M620 170 H722" stroke="#16a34a" stroke-width="4" stroke-dasharray="12 9"><animate attributeName="stroke-dashoffset" values="0;-42" dur="1.4s" repeatCount="indefinite"/></path>
  <path d="M710 160 l12 10 -12 10" fill="none" stroke="#16a34a" stroke-width="3"/>
  <text x="35" y="302" font-size="15" font-weight="700" fill="#334155">Au point d'entrée</text>
  <text x="35" y="326" font-size="14" fill="#475569">L'enveloppe extérieure est créée.</text>
  <text x="515" y="302" font-size="15" font-weight="700" fill="#334155">Au point de sortie</text>
  <text x="515" y="326" font-size="14" fill="#475569">L'enveloppe extérieure est retirée.</text>
  <text x="35" y="377" font-size="13" fill="#64748b">Le dessin est conceptuel : les en-têtes exacts et les garanties de sécurité dépendent du protocole de tunnel.</text>
</g>
</svg>

## 3.4 NAT : modification du tuple visible

Le NAT traduit des informations d’adressage conformément à sa configuration.

Dans le cas d’un NAT avec surcharge, plusieurs flux peuvent être différenciés par les ports traduits.

Avant le NAT, un flux peut être observé comme :

```text
192.0.2.25:51000 → 198.51.100.80:443
```

Après traduction, il peut apparaître comme :

```text
203.0.113.10:62001 → 198.51.100.80:443
```

Les adresses ci-dessus sont des valeurs réservées aux exemples documentaires.

Cet exemple illustre une traduction possible de l’adresse et du port source. Il ne constitue pas une description universelle de tous les NAT.

Lorsqu’une capture est réalisée de part et d’autre du NAT, les tuples observés doivent être mis en correspondance. Il est incorrect de conclure que deux flux sont nécessairement différents uniquement parce que leur adresse source ou leur port source n’est pas identique.

## 3.5 Proxy : terminaison et nouvelle connexion

Un proxy qui termine une connexion ne se comporte pas comme un simple routeur.

La connexion entre le client et le proxy se termine au proxy. Le proxy peut analyser ou traiter la requête, puis créer une connexion distincte vers le serveur.

Conséquences :

- les numéros de séquence TCP ne sont pas conservés entre les deux connexions ;
- les temporisations peuvent différer ;
- le proxy peut générer sa propre erreur ;
- le serveur peut voir l’adresse du proxy comme source ;
- la réussite d’une connexion client-proxy ne prouve pas la réussite de la connexion proxy-serveur.

Les captures et les journaux des deux côtés sont souvent nécessaires pour déterminer où se situe la défaillance.


# 4. Routage multi-sauts et asymétrie

## 4.1 Sélection d’une route

Le routage repose sur les préfixes, les informations installées dans les tables et les règles de transfert.

Il faut distinguer :

- le protocole qui apprend une route ;
- la route retenue dans la table de routage ;
- la résolution du prochain saut ;
- la décision effective de transfert du paquet ;
- les restrictions imposées par les politiques de sécurité.

La règle du préfixe le plus long est fondamentale pour sélectionner une route correspondante. Toutefois, il faut également tenir compte des règles qui déterminent quelles routes sont présentes et valides dans la table utilisée pour le transfert.

## 4.2 Routage asymétrique

Le chemin aller peut différer du chemin retour.

Cela peut être normal dans certaines architectures, mais provoquer des complications dans d’autres.

Exemples de problèmes potentiels :

- un pare-feu à état voit une seule direction d’un flux ;
- les captures de deux sites ne montrent pas les mêmes intermédiaires ;
- le trafic retour suit une route avec une MTU différente ;
- une règle de filtrage dépend de l’interface d’entrée ;
- un système de répartition de charge sélectionne un autre chemin.

L’asymétrie n’est pas automatiquement une panne. Il faut examiner l’architecture, les politiques et les propriétés des équipements concernés.

## 4.3 TTL IPv4 et Hop Limit IPv6

Le TTL IPv4 et le Hop Limit IPv6 limitent la durée de vie d’un paquet en nombre de sauts, plutôt qu’en durée réelle écoulée.

Lorsqu’un routeur transmet le paquet, le champ correspondant est décrémenté. Si sa valeur atteint la limite prévue par le protocole, le paquet ne peut pas continuer à être transféré normalement.

Ce comportement participe à éviter qu’un paquet circule indéfiniment dans une boucle de routage.

## 4.4 SVG animé — Deux chemins possibles

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 440" role="img" aria-labelledby="asym3-title asym3-desc">
<title id="asym3-title">Chemins aller et retour potentiellement asymétriques</title>
<desc id="asym3-desc">Le trafic aller emprunte une route supérieure, tandis que le trafic retour passe par une route inférieure. Les deux flux sont animés séparément et aboutissent aux mêmes extrémités.</desc>
<rect width="960" height="440" rx="18" fill="#f8fafc"/>
<text x="28" y="38" fill="#0f172a" font-family="Arial,sans-serif" font-size="23" font-weight="700">Asymétrie : le retour peut emprunter une autre route</text>
<g font-family="Arial,sans-serif">
  <rect x="40" y="165" width="155" height="90" rx="12" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="117" y="201" text-anchor="middle" font-size="17" font-weight="700" fill="#1e3a8a">Client</text>
  <text x="117" y="225" text-anchor="middle" font-size="13" fill="#1e3a8a">Point A</text>
  <rect x="765" y="165" width="155" height="90" rx="12" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="842" y="201" text-anchor="middle" font-size="17" font-weight="700" fill="#166534">Serveur</text>
  <text x="842" y="225" text-anchor="middle" font-size="13" fill="#166534">Point B</text>
  <rect x="325" y="80" width="155" height="70" rx="10" fill="#e0e7ff" stroke="#4f46e5" stroke-width="2"/>
  <text x="402" y="108" text-anchor="middle" font-size="15" font-weight="700" fill="#3730a3">Routeur R1</text><text x="402" y="130" text-anchor="middle" font-size="12" fill="#3730a3">Chemin aller</text>
  <rect x="515" y="80" width="155" height="70" rx="10" fill="#e0e7ff" stroke="#4f46e5" stroke-width="2"/>
  <text x="592" y="108" text-anchor="middle" font-size="15" font-weight="700" fill="#3730a3">Routeur R2</text><text x="592" y="130" text-anchor="middle" font-size="12" fill="#3730a3">Chemin aller</text>
  <rect x="325" y="295" width="155" height="70" rx="10" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="402" y="323" text-anchor="middle" font-size="15" font-weight="700" fill="#92400e">Routeur R3</text><text x="402" y="345" text-anchor="middle" font-size="12" fill="#92400e">Chemin retour</text>
  <rect x="515" y="295" width="155" height="70" rx="10" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="592" y="323" text-anchor="middle" font-size="15" font-weight="700" fill="#92400e">Routeur R4</text><text x="592" y="345" text-anchor="middle" font-size="12" fill="#92400e">Chemin retour</text>
  <path d="M195 185 L325 125 M480 115 H515 M670 125 L765 185" fill="none" stroke="#2563eb" stroke-width="4" stroke-dasharray="11 8"><animate attributeName="stroke-dashoffset" values="0;-38" dur="1.3s" repeatCount="indefinite"/></path>
  <path d="M765 235 L670 330 M515 330 H480 M325 330 L195 235" fill="none" stroke="#d97706" stroke-width="4" stroke-dasharray="11 8"><animate attributeName="stroke-dashoffset" values="0;38" dur="1.3s" repeatCount="indefinite"/></path>
  <text x="230" y="100" font-size="14" font-weight="700" fill="#1d4ed8">Aller</text>
  <text x="230" y="365" font-size="14" font-weight="700" fill="#92400e">Retour</text>
  <text x="40" y="403" font-size="13" fill="#475569">Des routes différentes peuvent être normales ; vérifiez les politiques, la symétrie attendue et l'état des équipements.</text>
</g>
</svg>

## 4.5 Méthode de vérification

Pour analyser un incident potentiellement lié à l’asymétrie :

1. Identifiez le point de départ et la destination.
2. Relevez les routes aller et retour lorsque vous pouvez les observer.
3. Recueillez les journaux de filtrage disponibles.
4. Comparez les interfaces d’entrée et de sortie.
5. Examinez la présence ou l’absence de chaque paquet aux points de capture.
6. Vérifiez si un équipement à état nécessite de voir les deux directions.
7. Distinguez une différence de chemin d’une véritable perte.


# 5. MTU de chemin, PMTUD et MSS

La MTU est essentielle lorsqu’un paquet doit traverser plusieurs liens ou un tunnel.

La **MTU de chemin** représente la plus petite MTU rencontrée sur le chemin considéré, pour le protocole et le contexte analysés.

## 5.1 Path MTU Discovery

La découverte de MTU de chemin, souvent abrégée PMTUD, permet à un émetteur de déterminer une taille adaptée aux capacités du chemin.

En IPv4, le bit DF et les messages ICMP indiquant qu’une fragmentation est nécessaire peuvent intervenir.

En IPv6, les routeurs ne fragmentent pas les paquets en transit. Les messages ICMPv6 « Packet Too Big » permettent notamment à l’émetteur d’ajuster le comportement.

Si les messages requis sont bloqués, certains échanges peuvent devenir difficiles ou impossibles dès que les paquets dépassent la capacité effective du chemin.

## 5.2 Pourquoi TCP et UDP réagissent différemment

Le MSS TCP aide à contrôler la taille des segments de données TCP. Il ne couvre cependant pas tous les problèmes de taille associés à tous les transports.

Les applications UDP qui émettent de grands datagrammes peuvent rencontrer des restrictions différentes. Une adaptation du MSS TCP ne corrige pas automatiquement ces datagrammes.

Les tunnels diminuent souvent la MTU utile en raison des en-têtes supplémentaires. Une valeur valable sur le réseau sous-jacent n’est donc pas forcément valable pour le paquet intérieur du tunnel.

## 5.3 Mesurer au lieu de deviner

La procédure doit au minimum prendre en compte :

- les MTU locales ;
- les interfaces de tunnel ;
- les technologies d’encapsulation ;
- les tailles des paquets qui passent et échouent ;
- les messages ICMP pertinents ;
- les symptômes de retransmission ;
- le point précis où chaque capture est réalisée.

Un ping réussi avec de petits paquets ne garantit pas que tous les paquets plus grands seront transportés correctement.

De même, un échec de ping de grande taille doit être interprété selon les options employées, les réponses possibles et les politiques de sécurité sur le chemin.

## 5.4 SVG animé — Rétrécissement de la capacité utile

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 410" role="img" aria-labelledby="mtu3-title mtu3-desc">
<title id="mtu3-title">Impact de la surcharge d'encapsulation sur la MTU utile</title>
<desc id="mtu3-desc">Une barre de capacité présente une enveloppe extérieure et un paquet intérieur. La portion disponible pour le paquet intérieur se réduit puis revient à sa taille illustrative initiale.</desc>
<rect width="960" height="410" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-weight="700" fill="#0f172a" font-family="Arial,sans-serif">Capacité totale et capacité utile du paquet</text>
<g font-family="Arial,sans-serif">
  <text x="55" y="86" font-size="16" font-weight="700" fill="#334155">Sans encapsulation extérieure</text>
  <rect x="55" y="101" width="760" height="54" rx="8" fill="#bfdbfe" stroke="#2563eb" stroke-width="2"/>
  <text x="435" y="134" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">Capacité représentée par un seul paquet IP</text>
  <text x="55" y="205" font-size="16" font-weight="700" fill="#334155">Avec tunnel</text>
  <rect x="55" y="220" width="760" height="70" rx="8" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
  <rect x="55" y="220" width="125" height="70" rx="8" fill="#fecaca" stroke="#b91c1c" stroke-width="2"/>
  <text x="117" y="247" text-anchor="middle" font-size="13" font-weight="700" fill="#991b1b">En-têtes</text><text x="117" y="267" text-anchor="middle" font-size="13" fill="#991b1b">extérieurs</text>
  <rect x="183" y="220" width="630" height="70" rx="8" fill="#bbf7d0" stroke="#15803d" stroke-width="2"/>
  <text x="498" y="247" text-anchor="middle" font-size="15" font-weight="700" fill="#14532d">Paquet intérieur</text>
  <text x="498" y="268" text-anchor="middle" font-size="13" fill="#14532d">Espace restant après la surcharge</text>
  <rect x="55" y="318" width="760" height="18" rx="5" fill="#cbd5e1"/>
  <rect x="55" y="318" width="760" height="18" rx="5" fill="#2563eb">
    <animate attributeName="width" values="760;640;700;640;760" dur="5s" repeatCount="indefinite"/>
  </rect>
  <text x="55" y="366" font-size="14" fill="#334155">Illustration sans échelle : ne pas utiliser ces proportions comme valeur réelle de MTU ou de MSS.</text>
  <text x="55" y="389" font-size="13" fill="#64748b">Les valeurs doivent être déterminées à partir du réseau, du tunnel et des protocoles employés.</text>
</g>
</svg>


# 6. TCP : séquences, retransmissions et fenêtres

TCP est un protocole à état qui fournit un flux d’octets fiable et ordonné.

L’analyse avancée exige d’examiner la relation entre les données émises, les accusés de réception, les fenêtres et le temps.

## 6.1 Numéros de séquence et accusés de réception

Les segments TCP utilisent des numéros de séquence pour repérer les octets dans le flux.

Les accusés de réception indiquent au correspondant les données reçues selon les mécanismes TCP. Ils permettent notamment de déterminer ce qui doit encore être retransmis.

Une absence d’accusé de réception peut avoir plusieurs causes :

- perte sur le chemin ;
- paquet filtré ;
- chemin retour défaillant ;
- destinataire indisponible ;
- congestion ;
- capture incomplète ;
- point de collecte situé avant certains traitements de la carte réseau.

Il faut donc étudier la chronologie et les numéros de séquence plutôt que de conclure à partir d'une seule annotation.

## 6.2 Contrôle de flux

TCP utilise une fenêtre de réception qui participe à éviter que l’émetteur n’envoie plus de données que le récepteur n’est prêt à en accepter.

Si la fenêtre annoncée devient très petite, l’émetteur peut se retrouver temporairement limité par le récepteur.

Ce phénomène doit être différencié d’une perte sur le réseau ou d'un contrôle de congestion.

## 6.3 Contrôle de congestion

TCP adapte son comportement à la congestion présumée. Les mécanismes précis dépendent de l’implémentation et de la variante utilisée.

Une capture peut montrer des retransmissions, des accusés de réception dupliqués ou des changements dans le rythme d’émission. Ces signes doivent être interprétés dans leur contexte.

La présence de retransmissions ne prouve pas à elle seule que le routeur situé au milieu du chemin est défectueux.

## 6.4 SYN, RST et délais d’expiration

Un échange TCP classique commence par SYN, SYN-ACK puis ACK.

Plusieurs situations peuvent suivre :

- Un SYN sans réponse visible peut indiquer une perte, un filtrage silencieux ou une destination qui ne répond pas.
- Un RST peut indiquer un rejet de connexion ou une fermeture dans le contexte observé.
- Un délai d’expiration peut indiquer une absence de réponse, un filtrage silencieux ou un autre problème sur le chemin.
- Une connexion établie suivie d’un silence peut orienter vers le traitement des données, l’application ou les mécanismes de transport.

Le point d’émission du RST doit être déterminé lorsque c’est possible : il peut provenir du serveur ou d’un équipement intermédiaire.

## 6.5 Offloads et captures sur l’hôte

Les cartes réseau modernes peuvent réaliser certains traitements au lieu de laisser le système d’exploitation effectuer toutes les opérations.

Par exemple :

- calcul du checksum ;
- segmentation ;
- regroupement de données reçues.

Une capture locale peut donc afficher des objets différents de ceux qui sont observés après le traitement matériel.

Avant de conclure à une corruption sur le réseau, examinez les propriétés de la carte, le point de capture et les résultats d’une éventuelle capture indépendante.


# 7. Wireshark : limites et méthodes d’analyse

## 7.1 Une capture est une mesure située

Une capture montre ce qu’un point d’observation a enregistré.

Elle ne montre pas automatiquement :

- les paquets perdus avant ce point ;
- les paquets qui n’atteignent pas l’interface observée ;
- les décisions internes d’un pare-feu ;
- les échanges qui se produisent sur une autre interface ;
- le comportement exact d’un proxy situé ailleurs ;
- les opérations qui ont lieu après le point de collecte.

Notez l’interface, l’heure, le sens du trafic, les filtres, les pertes de capture et la relation entre le poste qui capture et les appareils étudiés.

## 7.2 Filtres utiles

Exemples de filtres d’affichage :

```text
dns
tcp
icmp
icmpv6
ip.addr == 192.0.2.10
tcp.port == 443
tcp.flags.syn == 1
tcp.analysis.retransmission
```

Ces filtres utilisent des adresses de documentation lorsque des adresses sont indiquées.

Les filtres doivent être adaptés au protocole et à la version de Wireshark. Un filtre de capture n’a pas la même fonction qu’un filtre d’affichage.

## 7.3 Comparer deux captures

Deux captures peuvent être comparées si les points d’observation, les heures et les conditions sont suffisamment connus.

Recherchez :

1. Le paquet de référence.
2. Son point d’émission et son point de réception supposé.
3. Les champs qui peuvent être modifiés par les équipements intermédiaires.
4. Les retransmissions ou différences de chronologie.
5. Les journaux qui corroborent ou contredisent l’hypothèse.
6. Les pertes de capture et les particularités d’horodatage.

Le même paquet IP peut être visible sous des trames Ethernet différentes sur deux liens successifs. Il ne faut pas rechercher une identité parfaite de tous les octets de la trame lorsqu’un routeur est présent.

## 7.4 Chiffrement et métadonnées

TLS protège le contenu applicatif selon sa version et sa configuration. Une capture ordinaire peut montrer certaines métadonnées, mais le contenu chiffré ne peut pas être interprété comme du texte applicatif sans mécanisme de déchiffrement autorisé et approprié.

Ne contournez pas les protections d’accès et n’essayez pas de recueillir des données confidentielles auxquelles vous n’êtes pas autorisé à accéder.

Une analyse professionnelle se limite aux données nécessaires à l’incident, respecte les règles de conservation et protège les fichiers de capture.


# 8. Méthode experte de diagnostic multicouche

L’approche experte combine une analyse descendante et une analyse ascendante.

L’approche descendante part du symptôme applicatif. L’approche ascendante vérifie d’abord le lien et les chemins de transmission.

Aucune des deux n’est toujours supérieure à l’autre. Le meilleur point de départ dépend du périmètre et des preuves disponibles.

## 8.1 Phase 1 — Définir le périmètre

Posez clairement :

- Qui rencontre le problème ?
- Quelle application ou destination est concernée ?
- Depuis quel site ou VLAN ?
- À quelles heures ?
- Tous les utilisateurs sont-ils affectés ?
- Le problème est-il permanent ou intermittent ?
- Quels changements ont eu lieu récemment ?

Le périmètre évite de confondre une panne générale et une panne limitée à un utilisateur ou à un service.

## 8.2 Phase 2 — Construire le chemin logique

Dessinez les éléments connus :

```text
Client
  ↓
Réseau local / VLAN
  ↓
Passerelle
  ↓
Réseau de transit / WAN / VPN éventuel
  ↓
Pare-feu / NAT / proxy éventuels
  ↓
Réseau distant
  ↓
Serveur / application
```

Adaptez le dessin à l’architecture réelle. N’ajoutez pas des équipements uniquement parce qu’ils sont courants dans d’autres réseaux.

## 8.3 Phase 3 — Définir la preuve attendue

Pour chaque hypothèse, définissez le résultat qui la soutiendrait ou la contredirait.

Exemple :

**Hypothèse :** le serveur ne répond pas au SYN.

Preuves utiles :

- capture proche de l’émetteur ;
- capture proche du serveur ;
- journaux ou compteurs de filtrage ;
- état du service et du système ;
- routes aller et retour.

Si la capture côté serveur ne montre jamais les SYN reçus par le client, cherchez le point où le trafic disparaît. Si les SYN arrivent au serveur mais qu’aucune réponse ne quitte son interface, examinez son état local et les mécanismes de filtrage.

Ces interprétations doivent rester adaptées au point de capture et aux pertes éventuelles.

## 8.4 Phase 4 — Isoler les variables

Évitez de changer simultanément la MTU, les routes, les règles du pare-feu et la configuration du service.

Une modification à la fois permet de mieux identifier la cause d’un changement de résultat.

Lorsque la modification est susceptible d'affecter la production :

- obtenez l’autorisation requise ;
- préparez une sauvegarde ;
- définissez un plan de retour arrière ;
- déterminez la fenêtre de changement ;
- préparez un test de validation ;
- consignez les résultats.

## 8.5 SVG animé — Arbre de décision de diagnostic

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 550" role="img" aria-labelledby="diag3-title diag3-desc">
<title id="diag3-title">Arbre de diagnostic d'un incident réseau</title>
<desc id="diag3-desc">Le diagnostic part du symptôme et s'oriente vers la vérification du lien, du routage, du transport et de l'application. Chaque étape possède son propre contour animé pour signaler la progression sans déplacer un marqueur commun.</desc>
<rect width="980" height="550" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-family="Arial,sans-serif" font-weight="700" fill="#0f172a">Diagnostic : du symptôme à la preuve</text>
<g font-family="Arial,sans-serif">
  <rect x="335" y="60" width="310" height="65" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="490" y="87" text-anchor="middle" font-size="17" font-weight="700" fill="#1e3a8a">Définir le symptôme</text>
  <text x="490" y="108" text-anchor="middle" font-size="13" fill="#1e3a8a">Périmètre, heure, destination</text>
  <path d="M490 125 V157" stroke="#475569" stroke-width="3"/>
  <rect x="335" y="157" width="310" height="65" rx="10" fill="#fee2e2" stroke="#b91c1c" stroke-width="2"/>
  <rect x="331" y="153" width="318" height="73" rx="13" fill="none" stroke="#b91c1c" stroke-width="3"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="3.8s" repeatCount="indefinite"/></rect>
  <text x="490" y="184" text-anchor="middle" font-size="17" font-weight="700" fill="#991b1b">1. Lien et liaison</text>
  <text x="490" y="205" text-anchor="middle" font-size="13" fill="#991b1b">Interface, VLAN, voisins</text>
  <path d="M490 222 V254" stroke="#475569" stroke-width="3"/>
  <rect x="335" y="254" width="310" height="65" rx="10" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <rect x="331" y="250" width="318" height="73" rx="13" fill="none" stroke="#d97706" stroke-width="3"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="4.1s" repeatCount="indefinite"/></rect>
  <text x="490" y="281" text-anchor="middle" font-size="17" font-weight="700" fill="#92400e">2. Réseau IP</text>
  <text x="490" y="302" text-anchor="middle" font-size="13" fill="#92400e">Routes, MTU, ICMP, NAT</text>
  <path d="M490 319 V351" stroke="#475569" stroke-width="3"/>
  <rect x="335" y="351" width="310" height="65" rx="10" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <rect x="331" y="347" width="318" height="73" rx="13" fill="none" stroke="#7c3aed" stroke-width="3"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="4.4s" repeatCount="indefinite"/></rect>
  <text x="490" y="378" text-anchor="middle" font-size="17" font-weight="700" fill="#5b21b6">3. Transport</text>
  <text x="490" y="399" text-anchor="middle" font-size="13" fill="#5b21b6">Ports, SYN, ACK, RST</text>
  <path d="M490 416 V448" stroke="#475569" stroke-width="3"/>
  <rect x="335" y="448" width="310" height="65" rx="10" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <rect x="331" y="444" width="318" height="73" rx="13" fill="none" stroke="#16a34a" stroke-width="3"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="4.7s" repeatCount="indefinite"/></rect>
  <text x="490" y="475" text-anchor="middle" font-size="17" font-weight="700" fill="#166534">4. Application</text>
  <text x="490" y="496" text-anchor="middle" font-size="13" fill="#166534">DNS, TLS, HTTP, journaux</text>
  <text x="45" y="180" font-size="15" font-weight="700" fill="#334155">Pour chaque étape :</text>
  <text x="45" y="207" font-size="14" fill="#475569">Définir le résultat attendu.</text>
  <text x="45" y="231" font-size="14" fill="#475569">Capturer une preuve.</text>
  <text x="45" y="255" font-size="14" fill="#475569">Comparer les hypothèses.</text>
  <text x="700" y="180" font-size="15" font-weight="700" fill="#334155">Avant de corriger :</text>
  <text x="700" y="207" font-size="14" fill="#475569">Établir une référence.</text>
  <text x="700" y="231" font-size="14" fill="#475569">Modifier une variable.</text>
  <text x="700" y="255" font-size="14" fill="#475569">Préparer le retour arrière.</text>
  <text x="45" y="532" font-size="13" fill="#64748b">L'arbre est un guide : l'ordre réel peut être adapté au symptôme et aux preuves déjà disponibles.</text>
</g>
</svg>


# 9. Sécurité et observation multi-couches

Les équipements de sécurité peuvent intervenir à plusieurs niveaux.

Un pare-feu à état peut suivre les connexions et appliquer des règles en fonction des adresses, des ports et du contexte de session.

Un proxy peut terminer une connexion et traiter le contenu applicatif.

Un système de détection peut analyser les caractéristiques d’un flux ou rechercher des signatures. Un mécanisme de protection peut interrompre le trafic lorsqu’une règle est déclenchée.

En conséquence, une panne apparemment « réseau » peut dépendre d’une règle de sécurité ou d’une politique applicative.

## 9.1 Journaliser le point exact de décision

Les informations utiles comprennent, selon la solution :

- l’interface d’entrée ;
- l’interface de sortie ;
- le tuple source/destination ;
- l’action appliquée ;
- la règle concernée ;
- l’horodatage ;
- l’identifiant de session ;
- la raison du rejet, si elle est disponible.

Ces journaux doivent être protégés et conservés conformément aux règles de l’organisation.

## 9.2 Ne pas confondre filtrage et perte

Un paquet qui n’atteint pas un destinataire peut avoir été :

- rejeté explicitement ;
- supprimé silencieusement ;
- perdu pendant le transfert ;
- envoyé par une route inattendue ;
- reçu puis ignoré par le système final.

Les symptômes chez le client peuvent sembler identiques. Les captures et journaux associés sont nécessaires pour départager ces cas.


# 10. Laboratoires avancés

## Laboratoire 1 — Investigation TCP multi-points

### Objectif

Distinguer l’absence de réception d’un SYN de l’absence de réponse du serveur.

### Procédure

1. Identifiez une connexion TCP autorisée à analyser.
2. Capturez le flux côté client.
3. Capturez le flux près du serveur si vous y êtes autorisé.
4. Corrélez les captures à partir du tuple, de l’horodatage et des caractéristiques disponibles.
5. Déterminez si le SYN est visible côté client, côté serveur, ou aux deux emplacements.
6. Si le SYN arrive au serveur, examinez la présence d’un SYN-ACK ou d’un RST.
7. Recherchez les règles de filtrage et journaux associés.
8. Notez les limites de la collecte et toute différence d’horodatage.

### Interprétation

- SYN visible uniquement au client : une perte ou un filtrage intermédiaire est possible, mais il faut d’abord vérifier que la capture côté serveur est complète et correctement placée.
- SYN visible près du serveur sans réponse visible : examinez l’état de la pile réseau, l’écoute du service et les politiques locales.
- SYN-ACK visible près du serveur mais absent du client : examinez le trajet retour.
- Établissement TCP réussi suivi d’un blocage : étudiez aussi le flux de données et la couche applicative.

Ces conclusions restent conditionnelles aux captures et ne remplacent pas la vérification de l’architecture réelle.

## Laboratoire 2 — Étude de MTU dans un tunnel

### Objectif

Vérifier si l’encapsulation affecte la taille utile des paquets.

### Étapes

1. Dessinez le chemin, y compris les extrémités du tunnel.
2. Relevez les MTU des interfaces.
3. Identifiez le type d’encapsulation et la surcharge introduite.
4. Mesurez ou testez les tailles de paquets selon les outils et permissions disponibles.
5. Examinez les messages ICMP nécessaires au fonctionnement normal.
6. Observez les retransmissions TCP et comparez des échanges avec différentes tailles.
7. Vérifiez séparément les flux TCP et UDP.
8. Formulez une hypothèse testable avant toute modification.

### Validation

Un correctif potentiel doit être validé en répétant le scénario initial et en contrôlant des flux représentatifs.

N’imposez pas une MTU arbitraire sans comprendre la capacité du chemin et les contraintes des équipements.

## Laboratoire 3 — Analyse de NAT

### Objectif

Mettre en correspondance les observations avant et après une traduction.

### Étapes

1. Identifiez le point de départ et le point d’arrivée.
2. Observez le tuple source/destination avant le NAT.
3. Observez le tuple après le NAT.
4. Déterminez quelles informations ont été traduites.
5. Consultez l’état de traduction et les journaux autorisés.
6. Vérifiez les ports, le protocole et la durée de l’état.
7. Distinguez la traduction d’adresse d’un proxy qui termine une connexion.

La comparaison doit porter sur des informations qui peuvent réellement être reliées entre les points d’observation.

## Laboratoire 4 — Établir un rapport d’incident

Préparez un rapport qui inclut :

- un résumé du symptôme ;
- le périmètre ;
- la chronologie ;
- le schéma logique du chemin ;
- les points de capture ;
- les filtres utilisés ;
- les observations ;
- les hypothèses retenues ou éliminées ;
- la cause racine démontrée ;
- la correction effectuée ;
- les résultats de validation ;
- les limites de l’investigation.

Un rapport ne doit pas présenter une hypothèse comme une cause racine si les preuves ne suffisent pas à la démontrer.


# 11. Exercices experts

## Exercice 1 — Proxy et TCP

Une capture entre un client et un proxy montre un flux TCP qui se termine avec succès. Une autre capture vers le serveur montre un échec TCP.

Expliquez pourquoi le premier résultat ne prouve pas que le serveur est accessible.

## Exercice 2 — NAT

Le tuple observé côté client diffère de celui observé après un équipement intermédiaire.

Décrivez les informations nécessaires pour déterminer si le phénomène est cohérent avec une traduction NAT.

## Exercice 3 — Asymétrie

Une capture aller est complète, mais la capture retour ne montre aucun des paquets attendus.

Donnez plusieurs explications et décrivez comment vérifier si le résultat reflète le routage, un filtrage ou une limite de capture.

## Exercice 4 — MTU

Des flux TCP passent après une adaptation du MSS, mais une application UDP échoue toujours pour ses datagrammes volumineux.

Expliquez pourquoi ce résultat est cohérent avec les différences entre les transports.

## Exercice 5 — Checksum

Une capture effectuée sur le client affiche plusieurs checksums TCP incorrects. Une capture externe ne reproduit pas ces erreurs.

Quelle hypothèse technique devient pertinente ? Quelles précautions faut-il prendre avant de conclure ?

## Exercice 6 — Retransmissions

Wireshark indique des retransmissions TCP, mais le serveur paraît fonctionner normalement.

Expliquez pourquoi cette observation n’identifie pas à elle seule la cause de la panne.

## Exercice 7 — Sécurité

La poignée de main TCP aboutit, mais l’application échoue immédiatement après le démarrage de TLS.

Citez les vérifications à effectuer aux niveaux transport, TLS et applicatif. Expliquez quelles conclusions sont possibles à chaque étape.

## Exercice 8 — Rapport

Quelles données minimales un technicien doit-il inclure dans un rapport de diagnostic pour qu’un autre technicien puisse reproduire les tests et vérifier les conclusions ?


# 12. Corrigés commentés

**Exercice 1**

Le proxy termine la connexion du client. Il peut créer une nouvelle connexion vers le serveur. Le succès de la première connexion ne démontre donc pas que la seconde est établie. Il faut consulter les observations et les journaux des deux flux.

**Exercice 2**

Il faut examiner les adresses source et destination, les ports, le protocole, le point d’observation et les entrées d’état NAT disponibles. Une traduction peut modifier l’adresse source ou destination et éventuellement le port. Il faut exclure les autres mécanismes, notamment les proxys et les tunnels.

**Exercice 3**

Explications possibles : chemin retour différent, filtrage, perte, mauvaise interface de capture, capture incomplète, décalage temporel ou trafic qui n’emprunte pas le chemin supposé. Les routes, les journaux de sécurité et les captures complémentaires doivent être corrélés.

**Exercice 4**

L’adaptation du MSS concerne les segments TCP. UDP ne reçoit pas automatiquement le même ajustement. Les applications UDP doivent adapter leur propre comportement ou utiliser les mécanismes qui leur sont appropriés. La MTU de chemin reste un sujet distinct.

**Exercice 5**

Un mécanisme d’offload peut calculer le checksum après le point de capture. La capture externe peut montrer les trames après le traitement matériel. Il faut vérifier les paramètres de la carte réseau et le placement de chaque capture avant de conclure à une corruption.

**Exercice 6**

Les retransmissions peuvent provenir d’une perte, d’un filtrage, d’une congestion, d’un chemin retour différent ou d’une capture incomplète. Elles doivent être interprétées avec les numéros de séquence, les accusés de réception, la chronologie et les autres points de collecte.

**Exercice 7**

La poignée de main TCP prouve que l’établissement du transport a suffisamment fonctionné jusqu’à son terme. Elle ne garantit pas le succès de TLS. Il faut examiner les erreurs de négociation TLS, les certificats, les versions et suites compatibles, les politiques de sécurité, puis les erreurs applicatives qui suivent.

**Exercice 8**

Incluez le périmètre, les heures, la topologie pertinente, les commandes, les filtres, les résultats, les points de capture, les hypothèses, la cause racine avec les preuves disponibles, les modifications appliquées et les résultats de validation. Précisez également les limites et incertitudes.


# 13. Modèle de rapport d’incident

Utilisez la trame suivante pour une investigation reproductible.

## 13.1 Résumé

- Symptôme :
- Application ou service concerné :
- Utilisateurs et sites affectés :
- Date et heure :
- Impact opérationnel :

## 13.2 Architecture

- Point de départ :
- Destination :
- VLAN ou sous-réseau :
- Passerelles et routes connues :
- Pare-feu, NAT, proxy ou tunnel :
- Points de capture :

## 13.3 Observations

Pour chaque test :

- Heure :
- Commande ou filtre :
- Résultat attendu :
- Résultat observé :
- Capture ou journal associé :
- Limites de l’observation :

## 13.4 Hypothèses

| Hypothèse | Preuve recherchée | Résultat | Statut |
|---|---|---|---|
| Résolution DNS incorrecte | Réponse DNS observée et comparaison | À renseigner | À confirmer |
| Routage incorrect | Tables de routage et observations du chemin | À renseigner | À confirmer |
| Filtrage du transport | Journaux, captures, règles applicables | À renseigner | À confirmer |
| Erreur applicative | Réponses du service et journaux autorisés | À renseigner | À confirmer |

Ne marquez une cause comme confirmée que lorsque les observations la soutiennent suffisamment.

## 13.5 Correction et validation

- Cause racine retenue :
- Preuves principales :
- Correction effectuée :
- Plan de retour arrière :
- Tests réalisés après correction :
- Résultats :
- Risques ou limites restant à surveiller :


# 14. Glossaire expert

**Asymétrie de routage :** situation dans laquelle le chemin aller et le chemin retour ne sont pas identiques.

**Checksum :** valeur utilisée pour détecter certaines altérations des données, selon les mécanismes du protocole concerné.

**Encapsulation :** ajout des informations nécessaires à un protocole autour d'une unité de données existante.

**MSS :** taille maximale de données TCP annoncée pour un segment, hors en-têtes TCP et IP.

**MTU de chemin :** plus petite MTU rencontrée sur le chemin considéré dans le contexte analysé.

**NAT :** traduction d’informations d’adressage selon une configuration.

**Offload :** délégation d’une tâche réseau au matériel ou à la carte réseau.

**Plan de contrôle :** fonctions de contrôle qui contribuent à établir les informations nécessaires au transfert.

**Plan de données :** fonctions qui transfèrent effectivement les paquets et trames.

**Plan de gestion :** fonctions d’administration et de supervision.

**PMTUD :** mécanisme de découverte de la MTU du chemin.

**Proxy :** intermédiaire qui reçoit des communications et peut établir ses propres connexions vers la destination.

**RST :** indicateur TCP associé notamment à la réinitialisation ou au rejet d’une connexion.

**SYN :** indicateur TCP notamment utilisé dans l’établissement d’une connexion.

**Tunnel :** mécanisme qui transporte une unité de données au moyen d’une autre encapsulation.


# 15. Fiche de validation d’un diagnostic expert

Avant de déclarer un incident résolu, vérifiez que :

- le périmètre réel est établi ;
- le chemin logique est documenté ;
- les observations sont associées à des points de capture précis ;
- les hypothèses sont distinguées des faits ;
- les routes aller et retour pertinentes ont été prises en compte ;
- les éventuels NAT, proxys et tunnels sont documentés ;
- la MTU et les contraintes d’encapsulation ont été considérées lorsque pertinentes ;
- les effets des offloads et des pertes de capture ont été évalués ;
- la correction a été testée de façon reproductible ;
- un plan de retour arrière existe pour les modifications sensibles ;
- les limites de l’analyse sont clairement consignées.


## Conclusion générale

Les modèles OSI et TCP/IP sont particulièrement utiles lorsqu’ils servent à organiser une investigation plutôt qu’à réciter des définitions.

Le niveau expert exige de corréler plusieurs sources : captures, routes, tables de transfert, journaux de sécurité, états NAT, métriques d’interface et réponses applicatives.

Le point essentiel est de localiser la première divergence entre le comportement attendu et le comportement observé. Ensuite, il faut tester des hypothèses vérifiables, modifier le moins de variables possible et confirmer la correction par des tests reproductibles.

Un diagnostic de qualité n’est pas seulement une explication plausible. C’est une conclusion soutenue par des observations, dont les limites sont connues et qui peut être vérifiée par un autre technicien.