# Le modèle OSI & TCP/IP — Cours intermédiaire

> **Niveau :** Intermédiaire  
> **Prérequis :** connaître les sept couches OSI, les adresses MAC et IP, les ports, ainsi que les bases de TCP et UDP.  
> **Objectif :** analyser un échange réseau réel, interpréter une capture et localiser une panne à partir d'observations vérifiables.


## Sommaire

1. Revoir le modèle OSI avec précision
2. Comprendre la correspondance avec TCP/IP
3. Encapsulation et PDU
4. Adressage local et acheminement IP
5. Commutation Ethernet et VLAN
6. Routage et passerelle par défaut
7. TCP, UDP et numéros de ports
8. MTU, fragmentation et MSS
9. DNS, DHCP et ARP/Neighbor Discovery
10. Lire une capture avec Wireshark
11. Diagnostiquer un échange TCP
12. Méthodologie de dépannage
13. Travaux pratiques
14. Exercices et corrigés
15. Glossaire technique


# 1. Revoir le modèle OSI avec précision

Le modèle OSI est une grille de lecture. Il permet de décrire différentes fonctions présentes dans une communication, mais tous les protocoles modernes ne se répartissent pas parfaitement dans sept couches distinctes.

Il faut distinguer deux idées :

- La **fonction logique** : ce que le système doit accomplir.
- L’**implémentation réelle** : le composant logiciel ou matériel qui accomplit cette fonction.

Par exemple, la présentation des données, le chiffrement et certaines fonctions de session peuvent être gérés par une bibliothèque applicative. Elles ne sont pas nécessairement isolées dans une couche OSI physiquement indépendante.

## 1.1 Couche 1 — Physique

Cette couche concerne les propriétés de transmission du signal.

Exemples d'éléments à examiner :

- caractéristiques du média ;
- connecteurs ;
- qualité du signal ;
- puissance et sensibilité radio ;
- pertes sur le support ;
- synchronisation et débit ;
- erreurs physiques rapportées par les interfaces.

Dans un réseau Ethernet, des compteurs d’erreurs physiques ou de couche liaison peuvent aider à identifier un problème de câble, de connecteur, de module optique ou de négociation.

Les outils système ne fournissent pas tous les mêmes compteurs. Leurs valeurs doivent être interprétées selon le constructeur et le type d’interface.

## 1.2 Couche 2 — Liaison de données

Cette couche permet de transférer des trames sur un lien.

Dans Ethernet, les fonctions de liaison comprennent notamment le format de trame, les adresses MAC et le contrôle d’intégrité de la trame.

Un commutateur de couche 2 apprend les adresses MAC sources qu’il observe et les associe à des ports logiques. Il utilise ensuite sa table de transfert pour décider où envoyer les trames.

Les VLAN permettent de séparer logiquement des domaines de couche 2. Une trame appartenant à un VLAN donné ne doit pas être considérée comme librement transférable vers tous les autres VLAN.

Les comportements exacts dépendent des interfaces, de la configuration et des fonctions de sécurité du matériel.

## 1.3 Couche 3 — Réseau

IP fournit l’adressage logique et l’acheminement des paquets.

Les responsabilités comprennent :

- l’utilisation de préfixes IP ;
- le traitement de l’adresse de destination ;
- la sélection d’un prochain saut ;
- le choix de l’interface de sortie ;
- le traitement du TTL IPv4 ou du Hop Limit IPv6 ;
- la gestion de certaines erreurs d’acheminement.

Le protocole ICMP fournit des messages de contrôle et de diagnostic associés à IP. ICMP n’est pas une garantie de disponibilité du service applicatif.

Un routeur choisit normalement sa route à partir des informations de la table de routage et de ses règles de transfert, pas à partir du contenu HTTP de chaque paquet.

## 1.4 Couche 4 — Transport

TCP et UDP fournissent des mécanismes de communication entre points d’extrémité.

TCP fournit notamment :

- un flux d’octets ordonné ;
- la retransmission des données non acquittées ;
- des numéros de séquence ;
- des accusés de réception ;
- un contrôle de flux ;
- un contrôle de congestion.

UDP permet de transporter des datagrammes sans fournir, à lui seul, la fiabilité de TCP.

Le numéro de port aide le système à distribuer les données au bon processus ou point d’extrémité. Un port ne constitue pas une adresse de routage.

## 1.5 Couches 5 à 7 — Session, présentation et application

Ces couches sont utiles pour classifier le traitement du dialogue, la représentation des données et les protocoles utilisés par les applications.

Dans une analyse réelle, la séparation dépend de la technologie. HTTP est un protocole applicatif. TLS protège les données échangées selon sa configuration. DNS peut être transporté au moyen de différents mécanismes. QUIC combine des fonctionnalités de transport et de sécurité au-dessus d’UDP.

L’objectif de l’analyste n’est pas de forcer chaque fonctionnalité dans une case unique, mais de comprendre où elle agit, quelles informations elle consomme et quel composant peut être responsable du comportement observé.


# 2. OSI et TCP/IP : comprendre la correspondance

Le modèle OSI sépare sept couches. Le modèle TCP/IP traditionnel en regroupe généralement quatre.

| Modèle TCP/IP à quatre couches | Couches OSI approximativement correspondantes | Exemples |
|---|---|---|
| Application | 5, 6 et 7 | HTTP, DNS, SMTP, SSH |
| Transport | 4 | TCP, UDP |
| Internet | 3 | IPv4, IPv6, ICMP |
| Accès réseau | 1 et 2 | Ethernet, Wi-Fi |

Un modèle à cinq couches est également utilisé dans l'enseignement : Application, Transport, Réseau, Liaison et Physique.

Ces représentations ne se contredisent pas nécessairement. Elles regroupent les fonctions différemment.

## 2.1 TLS et les applications

TLS fournit des propriétés de sécurité, notamment la confidentialité et l’intégrité des données, ainsi qu'une authentification selon le protocole et la configuration utilisés.

Dans les architectures courantes :

- HTTP/1.1 et HTTP/2 fonctionnent généralement sur TCP ;
- HTTPS utilise TLS pour protéger les échanges HTTP ;
- HTTP/3 utilise QUIC, lui-même construit au-dessus d'UDP.

Ces différences ont une conséquence pratique : une capture TCP ne permet pas à elle seule d’expliquer tous les échanges Web modernes.

Une session HTTP/3, par exemple, ne ressemble pas à un flux HTTP/2 transporté sur TCP, même si les deux permettent d’échanger des requêtes Web.

## 2.2 Les modèles aident à structurer, pas à simplifier à outrance

Prenons trois symptômes :

- Une interface Ethernet n’établit pas de lien.
- Un serveur répond au ping mais refuse une connexion TCP.
- Un navigateur établit la connexion, puis affiche une erreur HTTP.

Ces symptômes orientent vers des fonctions différentes.

Le premier nécessite d’étudier la couche physique ou la liaison. Le deuxième nécessite d’examiner les ports, les règles de filtrage et l’écoute du service. Le troisième nécessite d’analyser les échanges applicatifs et les réponses du serveur.

Ce classement n’est pas une preuve. Il indique plutôt où commencer les recherches.


# 3. Encapsulation, PDU et interprétation des paquets

L’encapsulation ajoute les informations nécessaires au fonctionnement des protocoles.

Pour un échange classique HTTP/1.1 sur TLS et TCP, le parcours peut inclure :

1. Le navigateur produit des données applicatives.
2. TLS les protège.
3. TCP transporte le flux.
4. IP prépare le paquet.
5. Ethernet ou Wi-Fi prépare les informations nécessaires au lien.
6. Le média transmet le signal.

Le parcours exact dépend du protocole utilisé, des optimisations du système et des équipements présents sur le chemin.

## 3.1 Les unités de données

| Niveau habituel | Nom usuel de l’unité | Informations caractéristiques |
|---|---|---|
| Application | Données | Contenu du protocole applicatif |
| Transport TCP | Segment TCP | Ports, séquences, acquittements |
| Transport UDP | Datagramme UDP | Ports et longueur du datagramme |
| Internet | Paquet IP | Adresses IP, TTL ou Hop Limit |
| Liaison | Trame | Adresses MAC ou identifiants de liaison |
| Physique | Bits ou symboles | Transmission sur le média |

Le vocabulaire est parfois utilisé avec souplesse dans les documents techniques. Un « paquet » peut être utilisé de façon générique, alors qu’en analyse précise il est préférable d’indiquer si l’on parle d’un segment TCP, d’un datagramme UDP, d’un paquet IP ou d’une trame.

## 3.2 Ce qui change lors du passage dans un routeur

Sur un réseau routé Ethernet :

- Le routeur reçoit une trame sur une interface.
- Il traite l’en-tête de liaison entrant.
- Il examine les informations IP nécessaires à l’acheminement.
- Il sélectionne un prochain saut.
- Il met à jour les champs qui le nécessitent.
- Il construit une nouvelle trame pour le lien de sortie.

Dans un cas habituel sans NAT, le paquet conserve ses adresses IP source et destination de bout en bout. En revanche, les adresses MAC de la trame correspondent au lien courant.

Des mécanismes intermédiaires, tels que NAT, un tunnel ou un proxy, peuvent modifier davantage le trafic.

## 3.3 SVG animé — Empilement des en-têtes

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 390" role="img" aria-labelledby="enc2-title enc2-desc">
<title id="enc2-title">Encapsulation d'un paquet réseau</title>
<desc id="enc2-desc">Quatre étapes montrent comment les en-têtes de transport, IP et liaison s'ajoutent aux données. Des traits animés représentent l'avancement de la construction des enveloppes.</desc>
<rect width="940" height="390" rx="18" fill="#f8fafc"/>
<text x="28" y="38" fill="#0f172a" font-size="23" font-family="Arial,sans-serif" font-weight="700">Encapsulation étape par étape</text>
<g font-family="Arial,sans-serif" font-size="14" font-weight="700">
  <rect x="35" y="80" width="170" height="55" rx="7" fill="#bfdbfe" stroke="#2563eb" stroke-width="2"/>
  <text x="120" y="103" text-anchor="middle" fill="#1e3a8a">Données</text><text x="120" y="122" text-anchor="middle" fill="#1e3a8a" font-weight="400">Application</text>
  <path d="M205 107 H245" stroke="#2563eb" stroke-width="3" stroke-dasharray="8 7"><animate attributeName="stroke-dashoffset" values="0;-30" dur="1.4s" repeatCount="indefinite"/></path>
  <rect x="255" y="80" width="125" height="55" rx="7" fill="#bbf7d0" stroke="#15803d" stroke-width="2"/><text x="317" y="112" text-anchor="middle" fill="#14532d">TCP</text>
  <rect x="380" y="80" width="170" height="55" rx="7" fill="#bfdbfe" stroke="#2563eb" stroke-width="2"/><text x="465" y="103" text-anchor="middle" fill="#1e3a8a">Données</text><text x="465" y="122" text-anchor="middle" fill="#1e3a8a" font-weight="400">Segment TCP</text>
  <path d="M317 139 V164 H370" fill="none" stroke="#b45309" stroke-width="3" stroke-dasharray="7 5"><animate attributeName="stroke-dashoffset" values="0;-24" dur="1.1s" repeatCount="indefinite"/></path>
  <rect x="255" y="169" width="125" height="55" rx="7" fill="#fde68a" stroke="#b45309" stroke-width="2"/><text x="317" y="202" text-anchor="middle" fill="#78350f">IP</text>
  <rect x="380" y="169" width="290" height="55" rx="7" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/><text x="525" y="202" text-anchor="middle" fill="#1e3a8a">En-tête IP + segment TCP</text>
  <path d="M317 228 V253 H370" fill="none" stroke="#b91c1c" stroke-width="3" stroke-dasharray="7 5"><animate attributeName="stroke-dashoffset" values="0;-24" dur="1.1s" repeatCount="indefinite"/></path>
  <rect x="255" y="258" width="125" height="55" rx="7" fill="#fecaca" stroke="#b91c1c" stroke-width="2"/><text x="317" y="291" text-anchor="middle" fill="#7f1d1d">Ethernet</text>
  <rect x="380" y="258" width="395" height="55" rx="7" fill="#e2e8f0" stroke="#475569" stroke-width="2"/><text x="577" y="291" text-anchor="middle" fill="#0f172a">En-tête Ethernet + paquet IP + contrôle</text>
  <text x="710" y="95" fill="#334155">Ports</text><text x="710" y="120" fill="#334155" font-weight="400">Transport</text>
  <text x="710" y="183" fill="#334155">Adresses IP</text><text x="710" y="208" fill="#334155" font-weight="400">Réseau</text>
  <text x="790" y="270" fill="#334155">Adresses MAC</text><text x="790" y="295" fill="#334155" font-weight="400">Liaison</text>
</g>
<text x="35" y="355" fill="#475569" font-family="Arial,sans-serif" font-size="13">Les traits en mouvement illustrent les étapes ; ils ne représentent pas un débit réel ou une mesure de performance.</text>
</svg>


# 4. Adresses locales et acheminement IP

Une machine doit déterminer si la destination IP se trouve sur son réseau local ou si elle doit utiliser un routeur.

Le système compare l’adresse de destination et son préfixe selon les règles d’adressage configurées.

## 4.1 Destination locale

Si la destination est considérée comme directement accessible sur le lien :

1. Le poste détermine l’adresse de couche 2 correspondante.
2. Il utilise ARP en IPv4 ou Neighbor Discovery en IPv6 lorsque nécessaire.
3. Il construit une trame vers la machine de destination.
4. La trame est transférée sur le réseau local.

## 4.2 Destination distante

Si la destination est hors du sous-réseau :

1. Le poste sélectionne une route.
2. Il utilise normalement sa passerelle par défaut s’il n’existe pas de route plus spécifique.
3. Il résout l’adresse de liaison du prochain saut.
4. Il construit une trame destinée à cette passerelle.
5. Le routeur reçoit et traite le paquet IP.

L’adresse MAC de destination correspond donc généralement au prochain saut sur le lien, et pas à l’adresse MAC du serveur distant.

## 4.3 Plusieurs routeurs

Chaque routeur peut choisir un nouveau prochain saut. Le paquet IP traverse différents liens et reçoit de nouvelles enveloppes de liaison.

Le trajet aller et le trajet retour peuvent être différents. Un diagnostic ne doit donc pas supposer que les paquets suivent obligatoirement le même chemin dans les deux directions.


# 5. Commutation Ethernet et VLAN

## 5.1 Apprentissage MAC

Un commutateur apprend les adresses MAC sources qu’il observe sur ses ports.

Sa table de transfert peut être schématisée ainsi :

| VLAN | Adresse MAC apprise | Port associé |
|---|---|---|
| 10 | 00:11:22:33:44:55 | Gi1/0/1 |
| 10 | 00:11:22:33:44:66 | Gi1/0/2 |
| 20 | 00:11:22:33:44:77 | Gi1/0/8 |

Ces valeurs sont fictives. Elles illustrent le principe selon lequel une entrée doit être interprétée avec le VLAN et le contexte de commutation concernés.

Le commutateur n’apprend pas directement le nom d’utilisateur ni la fonction applicative de chaque machine. Il associe principalement des informations de couche 2 à des interfaces logiques.

## 5.2 Qu’est-ce qu’un VLAN ?

Un VLAN définit un domaine logique de couche 2.

Plusieurs VLAN peuvent utiliser le même commutateur physique tout en conservant une séparation logique. La configuration exacte dépend de l’infrastructure.

Les ports d’accès sont normalement associés à un VLAN de terminaison. Les liens de type trunk peuvent transporter plusieurs VLAN selon la configuration et les mécanismes de balisage employés.

Deux machines situées dans des VLAN distincts ont généralement besoin d’un service de couche 3 pour communiquer entre elles.

## 5.3 Pistes de diagnostic d’un problème de VLAN

- Vérifier le VLAN attribué au port.
- Vérifier le mode du port et le VLAN natif s’il existe.
- Vérifier les VLAN autorisés sur les trunks.
- Vérifier l’existence de la passerelle du VLAN.
- Vérifier les adresses IP et les préfixes.
- Vérifier les règles de routage et les ACL.
- Vérifier les protections de couche 2 et l’état des ports.

Une adresse IP apparemment correcte ne prouve pas que le poste se trouve dans le VLAN adapté.


# 6. Routage et passerelle par défaut

La table de routage permet de choisir une route en fonction de la destination.

Une machine peut connaître :

- une route directement connectée ;
- une route vers un réseau distant ;
- une route spécifique vers un préfixe ;
- une route par défaut.

La route par défaut n’est normalement utilisée que si aucune route plus spécifique retenue ne correspond à la destination.

## 6.1 Préfixe le plus long

Lorsqu’une table contient plusieurs routes qui correspondent à une destination, le mécanisme de transfert IP privilégie normalement la route avec le préfixe le plus long parmi les routes retenues pour le transfert.

Cela signifie qu’une route vers un réseau plus spécifique peut être sélectionnée plutôt qu’une route plus générale.

Les protocoles de routage, les politiques et les règles d’installation des routes déterminent quelles routes deviennent disponibles dans la table utilisée pour le transfert.

## 6.2 Schéma SVG animé — Décision locale ou distante

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 930 390" role="img" aria-labelledby="decision2-title decision2-desc">
<title id="decision2-title">Décision d'acheminement IP</title>
<desc id="decision2-desc">Un poste compare la destination au préfixe local. Une branche conduit au destinataire sur le lien local, l'autre vers la passerelle. Les traits de chaque branche s'animent indépendamment.</desc>
<rect width="930" height="390" rx="18" fill="#f8fafc"/>
<text x="28" y="38" fill="#0f172a" font-size="23" font-family="Arial,sans-serif" font-weight="700">Comment le poste choisit-il le prochain saut ?</text>
<g font-family="Arial,sans-serif">
  <rect x="300" y="65" width="330" height="64" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="465" y="91" text-anchor="middle" font-size="17" font-weight="700" fill="#1e3a8a">Destination IP connue</text>
  <text x="465" y="113" text-anchor="middle" font-size="14" fill="#1e3a8a">Recherche d'une route applicable</text>
  <path d="M465 129 V157 H227 V186 M465 157 H703 V186" fill="none" stroke="#475569" stroke-width="3"/>
  <path d="M227 157 H227 V186" stroke="#2563eb" stroke-width="3" stroke-dasharray="7 6"><animate attributeName="stroke-dashoffset" values="0;-26" dur="1.3s" repeatCount="indefinite"/></path>
  <path d="M703 157 V186" stroke="#0f766e" stroke-width="3" stroke-dasharray="7 6"><animate attributeName="stroke-dashoffset" values="0;-26" dur="1.3s" repeatCount="indefinite"/></path>
  <rect x="55" y="190" width="345" height="95" rx="10" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="227" y="219" text-anchor="middle" font-size="17" font-weight="700" fill="#166534">Destination locale</text>
  <text x="227" y="244" text-anchor="middle" font-size="14" fill="#166534">Résoudre la MAC de l'hôte</text>
  <text x="227" y="265" text-anchor="middle" font-size="14" fill="#166534">Envoyer sur le lien local</text>
  <rect x="530" y="190" width="345" height="95" rx="10" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="703" y="219" text-anchor="middle" font-size="17" font-weight="700" fill="#92400e">Destination distante</text>
  <text x="703" y="244" text-anchor="middle" font-size="14" fill="#92400e">Choisir le prochain saut</text>
  <text x="703" y="265" text-anchor="middle" font-size="14" fill="#92400e">Utiliser la passerelle si nécessaire</text>
  <text x="55" y="325" font-size="14" fill="#334155">Adresse IP de destination : généralement inchangée par ce choix local.</text>
  <text x="55" y="350" font-size="14" fill="#334155">Adresse MAC de destination : celle du prochain saut sur le lien courant.</text>
</g>
</svg>


# 7. TCP, UDP et numéros de ports

## 7.1 TCP : flux fiable et ordonné

TCP utilise un mécanisme d’établissement de connexion traditionnellement illustré par trois messages :

1. SYN ;
2. SYN-ACK ;
3. ACK.

Ce dialogue établit les paramètres initiaux de la connexion TCP. Ensuite, les données sont transmises selon les mécanismes de séquencement, d’acquittement, de contrôle de flux et de congestion.

TCP offre un flux d’octets. Il ne préserve pas nécessairement les frontières entre les appels d’écriture de l’application. Une application doit définir elle-même comment reconnaître les messages dans ce flux.

## 7.2 UDP : datagrammes

UDP fournit une abstraction différente : les données sont transportées sous forme de datagrammes. UDP ne met pas en œuvre, à lui seul, les retransmissions ou le contrôle de congestion de TCP.

Cela ne signifie pas que les applications basées sur UDP ne peuvent pas être fiables. Elles peuvent implémenter leurs propres mécanismes ou utiliser un protocole supérieur comme QUIC.

## 7.3 Ports source et destination

Une communication TCP est couramment identifiée par le protocole et le tuple formé par :

- l’adresse IP source ;
- le port source ;
- l’adresse IP destination ;
- le port destination.

L’adresse et le port source identifient un point d’extrémité de l’échange. L’adresse et le port destination identifient l’autre point d’extrémité visible à cet endroit du chemin.

NAT et les proxys peuvent modifier ce que l’on observe dans ce tuple.

## 7.4 SVG animé — Établissement de connexion TCP

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 930 420" role="img" aria-labelledby="tcp2-title tcp2-desc">
<title id="tcp2-title">Handshake TCP en trois étapes</title>
<desc id="tcp2-desc">Les trois flèches SYN, SYN-ACK et ACK s'animent séparément entre client et serveur. Les étapes sont accompagnées de leur ordre.</desc>
<rect width="930" height="420" rx="18" fill="#f8fafc"/>
<text x="28" y="38" fill="#0f172a" font-size="23" font-family="Arial,sans-serif" font-weight="700">TCP : établissement d'une connexion classique</text>
<g font-family="Arial,sans-serif">
  <text x="135" y="78" font-size="18" font-weight="700" fill="#1d4ed8">Client</text>
  <text x="710" y="78" font-size="18" font-weight="700" fill="#047857">Serveur</text>
  <path d="M160 95 V356 M740 95 V356" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6 6"/>
  <path d="M170 130 L730 180" stroke="#2563eb" stroke-width="4" stroke-dasharray="13 10"><animate attributeName="stroke-dashoffset" values="0;-46" dur="1.4s" repeatCount="indefinite"/></path>
  <path d="M715 169 l15 11 -17 5" fill="none" stroke="#2563eb" stroke-width="3"/>
  <rect x="386" y="131" width="116" height="30" rx="6" fill="#dbeafe" stroke="#2563eb"/>
  <text x="444" y="151" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">1. SYN</text>
  <path d="M730 220 L170 270" stroke="#059669" stroke-width="4" stroke-dasharray="13 10"><animate attributeName="stroke-dashoffset" values="0;46" dur="1.4s" repeatCount="indefinite"/></path>
  <path d="M185 264 l-15 6 16 6" fill="none" stroke="#059669" stroke-width="3"/>
  <rect x="355" y="223" width="176" height="30" rx="6" fill="#dcfce7" stroke="#16a34a"/>
  <text x="443" y="243" text-anchor="middle" font-size="15" font-weight="700" fill="#166534">2. SYN-ACK</text>
  <path d="M170 300 L730 340" stroke="#7c3aed" stroke-width="4" stroke-dasharray="13 10"><animate attributeName="stroke-dashoffset" values="0;-46" dur="1.4s" repeatCount="indefinite"/></path>
  <path d="M715 330 l15 10 -17 5" fill="none" stroke="#7c3aed" stroke-width="3"/>
  <rect x="386" y="302" width="116" height="30" rx="6" fill="#ede9fe" stroke="#7c3aed"/>
  <text x="444" y="322" text-anchor="middle" font-size="15" font-weight="700" fill="#5b21b6">3. ACK</text>
  <text x="28" y="383" font-size="14" fill="#334155">Après l'établissement, TCP peut transporter des données selon son mécanisme de flux et d'acquittement.</text>
</g>
</svg>

## 7.5 Interpréter les symptômes TCP

| Observation | Explications possibles | Autres vérifications |
|---|---|---|
| SYN répétés sans réponse | Perte, filtrage silencieux, route absente, hôte inaccessible | Captures des deux côtés, tables de routage, ACL |
| RST reçu | Port refusé, fermeture ou équipement intermédiaire | Adresse source du RST, état du service, point de capture |
| Connexion établie puis blocage | Application lente, perte de données, contrôle de flux, filtrage en cours de session | Chronologie TCP, journaux applicatifs |
| Retransmissions | Absence d’accusé de réception, perte, congestion ou capture incomplète | Numéros de séquence et ACK, captures synchronisées |
| Connexion rapide puis erreur HTTP | Problème applicatif, authentification, proxy, serveur | Réponse HTTP et journaux |

Ces observations ne constituent pas des diagnostics définitifs. Plusieurs causes différentes peuvent produire des symptômes similaires.


# 8. MTU, fragmentation et MSS

## 8.1 Comprendre la MTU

La **Maximum Transmission Unit (MTU)** correspond à la taille maximale de l’unité transportée sur un lien, selon le protocole et sa définition.

Une MTU couramment rencontrée sur Ethernet est de 1500 octets pour le paquet IP, mais d’autres valeurs existent. Il faut vérifier les propriétés réelles du chemin et des interfaces.

Les tunnels, VPN et autres mécanismes d’encapsulation ajoutent des en-têtes qui diminuent la capacité disponible pour le paquet intérieur.

## 8.2 Pourquoi les gros transferts peuvent-ils échouer ?

Supposons qu’une connexion transporte de petites requêtes correctement, mais se bloque dès que la quantité de données augmente.

Une MTU trop grande sur une portion du chemin peut être une hypothèse pertinente. D’autres explications restent possibles : filtrage, perte de paquets, bugs, problèmes applicatifs ou congestion.

Le diagnostic doit confronter cette hypothèse aux mesures.

## 8.3 IPv4 et IPv6

IPv4 permet la fragmentation dans certaines conditions. Le bit DF peut interdire la fragmentation et faire apparaître un problème de MTU de chemin.

IPv6 fonctionne différemment : les routeurs ne fragmentent pas les paquets IPv6. L’émetteur adapte la taille et peut utiliser les mécanismes de fragmentation prévus par IPv6. Les messages ICMPv6 « Packet Too Big » jouent un rôle essentiel dans le fonctionnement normal.

Bloquer les messages ICMP nécessaires à la découverte de MTU peut causer des pannes difficiles à identifier.

## 8.4 MSS TCP

Le **Maximum Segment Size (MSS)** représente la quantité maximale de données TCP dans un segment, hors en-têtes TCP et IP.

Le MSS annoncé participe à la détermination de la taille des segments. L’ajustement du MSS peut aider à éviter des paquets trop grands dans certains chemins, mais il ne règle pas automatiquement toutes les pannes MTU et ne couvre pas tous les transports UDP.

## 8.5 SVG animé — MTU et tunnel

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 930 400" role="img" aria-labelledby="mtu2-title mtu2-desc">
<title id="mtu2-title">MTU réduite par l'encapsulation d'un tunnel</title>
<desc id="mtu2-desc">Un paquet intérieur est entouré par une enveloppe de tunnel. La barre de capacité disponible se réduit de façon animée quand la surcharge du tunnel est représentée.</desc>
<rect width="930" height="400" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" fill="#0f172a" font-family="Arial,sans-serif" font-weight="700">MTU : le tunnel consomme une partie de la capacité</text>
<g font-family="Arial,sans-serif">
  <text x="65" y="83" font-size="16" font-weight="700" fill="#334155">Lien sans tunnel</text>
  <rect x="65" y="98" width="690" height="48" rx="7" fill="#bfdbfe" stroke="#2563eb" stroke-width="2"/>
  <text x="410" y="128" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">Paquet IP transporté sur le lien</text>
  <text x="65" y="192" font-size="16" font-weight="700" fill="#334155">Lien avec tunnel</text>
  <rect x="65" y="207" width="690" height="60" rx="7" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
  <rect x="65" y="207" width="108" height="60" rx="7" fill="#fecaca" stroke="#b91c1c" stroke-width="2"/>
  <text x="119" y="232" text-anchor="middle" font-size="12" font-weight="700" fill="#7f1d1d">En-tête</text><text x="119" y="249" text-anchor="middle" font-size="12" fill="#7f1d1d">tunnel</text>
  <rect x="174" y="207" width="581" height="60" rx="7" fill="#bbf7d0" stroke="#15803d" stroke-width="2"/>
  <text x="464" y="232" text-anchor="middle" font-size="15" font-weight="700" fill="#14532d">Paquet intérieur</text><text x="464" y="251" text-anchor="middle" font-size="13" fill="#14532d">Données + transport + IP intérieur</text>
  <text x="790" y="119" font-size="15" fill="#1e3a8a">Capacité</text><text x="790" y="139" font-size="15" fill="#1e3a8a">disponible</text>
  <text x="790" y="229" font-size="15" fill="#7f1d1d">Surcharge</text><text x="790" y="249" font-size="15" fill="#7f1d1d">du tunnel</text>
  <rect x="65" y="304" width="690" height="20" rx="5" fill="#cbd5e1"/>
  <rect x="65" y="304" width="690" height="20" rx="5" fill="#2563eb">
    <animate attributeName="width" values="690;600;690" dur="4s" repeatCount="indefinite"/>
  </rect>
  <text x="65" y="352" font-size="14" fill="#334155">Illustration conceptuelle : la surcharge diminue la place disponible pour le paquet intérieur.</text>
  <text x="65" y="375" font-size="13" fill="#64748b">Les valeurs réelles dépendent du type de tunnel, de l'IP utilisée et des options d'encapsulation.</text>
</g>
</svg>

## 8.6 Diagnostic d’une suspicion de MTU

1. Identifier l’ensemble du chemin, y compris les VPN et tunnels.
2. relever la MTU configurée sur les interfaces ;
3. déterminer si les petits échanges fonctionnent ;
4. tester les tailles de paquets appropriées dans un environnement autorisé ;
5. examiner les messages ICMP et la découverte de MTU ;
6. observer la taille des segments et les retransmissions TCP ;
7. comparer, si possible, les captures prises à plusieurs points ;
8. modifier un seul paramètre à la fois et répéter les tests.

Ne concluez pas automatiquement à une panne de MTU parce qu’un transfert volumineux échoue.


# 9. DNS, DHCP et résolution locale

## 9.1 DNS

DNS permet de rechercher des informations à partir de noms de domaine.

Un client peut interroger un résolveur configuré, qui utilise éventuellement un cache et effectue les recherches nécessaires.

Types d’enregistrements courants :

- A : adresse IPv4 ;
- AAAA : adresse IPv6 ;
- CNAME : alias ;
- MX : informations relatives aux serveurs de messagerie ;
- NS : serveurs faisant autorité pour une zone ;
- TXT : informations textuelles utilisées par différents services.

Une réponse DNS correcte ne garantit pas que le service hébergé à l’adresse renvoyée est disponible.

## 9.2 DHCP

DHCP permet à un client d’obtenir automatiquement des paramètres réseau.

La séquence pédagogique souvent résumée par DORA comprend :

1. Discover ;
2. Offer ;
3. Request ;
4. Acknowledgement.

Les implémentations et scénarios de renouvellement peuvent être différents. Le but essentiel est de fournir les paramètres nécessaires tels que l’adresse IP, le préfixe, la passerelle et les serveurs DNS.

Une mauvaise configuration DHCP peut provoquer un problème de connectivité même si la carte réseau et le câble fonctionnent.

## 9.3 ARP et Neighbor Discovery

ARP permet de résoudre une adresse IPv4 vers une adresse de liaison dans le contexte du réseau local.

En IPv6, Neighbor Discovery fournit notamment les mécanismes de découverte des voisins et de résolution nécessaires au fonctionnement local.

Un problème de résolution locale peut empêcher une machine de remettre ses paquets au prochain saut, même si l’adresse IP et la route paraissent correctes.


# 10. Lire une capture avec Wireshark

Wireshark permet de capturer et d’analyser des paquets à partir d’une interface ou d’un fichier de capture autorisé.

Une capture est une observation prise à un endroit donné. Elle peut être incomplète ou influencée par les propriétés de l’interface, les pertes de capture, les offloads et le point d’observation.

## 10.1 Filtres d’affichage courants

| Filtre | Utilité |
|---|---|
| `dns` | Afficher les paquets DNS reconnus |
| `tcp` | Afficher les paquets TCP |
| `icmp` | Afficher ICMP pour IPv4 |
| `icmpv6` | Afficher ICMPv6 |
| `ip.addr == 192.0.2.10` | Filtrer les paquets ayant cette adresse IPv4 comme source ou destination |
| `tcp.port == 443` | Afficher les paquets TCP associés au port 443 |
| `tcp.flags.syn == 1` | Afficher les segments dont le bit SYN est positionné |
| `tcp.analysis.retransmission` | Afficher les retransmissions détectées selon l’analyse de Wireshark |

Les adresses du tableau sont fictives.

La syntaxe ci-dessus correspond à des filtres d’affichage Wireshark, pas aux filtres de capture utilisés pour décider quels paquets enregistrer au départ.

## 10.2 Filtre de capture contre filtre d’affichage

Un **filtre de capture** peut empêcher certains paquets d’être enregistrés.

Un **filtre d’affichage** masque certains paquets dans l’interface d’analyse, mais conserve les paquets capturés dans le fichier.

Cette différence est importante : un paquet absent du fichier n’est pas récupérable par un filtre d’affichage.

## 10.3 Premiers éléments à observer

Lorsqu’une connexion échoue :

1. Identifier l’adresse IP et le port source.
2. Identifier l’adresse IP et le port destination.
3. Vérifier le protocole transport.
4. Observer les messages initiaux de l’échange.
5. Examiner l’intervalle entre les requêtes et les réponses.
6. Rechercher les retransmissions et les rejets.
7. Relier les observations aux journaux ou mesures disponibles.

Ne vous contentez pas d’un paquet isolé. Une chronologie est souvent nécessaire pour distinguer une absence de réponse, un retard et une retransmission.

## 10.4 SVG animé — Chronologie d’une connexion et d’une retransmission

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 405" role="img" aria-labelledby="trace2-title trace2-desc">
<title id="trace2-title">Chronologie TCP pour l'analyse Wireshark</title>
<desc id="trace2-desc">Une séquence montre le SYN, l'absence de SYN-ACK visible, puis la répétition d'un SYN. Les lignes et les points de chronologie s'animent pour mettre en évidence le délai.</desc>
<rect width="950" height="405" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-family="Arial,sans-serif" font-weight="700" fill="#0f172a">Capture : distinguer une tentative et une retransmission</text>
<g font-family="Arial,sans-serif">
  <text x="80" y="79" font-size="16" font-weight="700" fill="#1d4ed8">Client</text>
  <text x="740" y="79" font-size="16" font-weight="700" fill="#047857">Serveur</text>
  <path d="M105 92 V320 M770 92 V320" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6 6"/>
  <path d="M110 125 H765" stroke="#2563eb" stroke-width="4" stroke-dasharray="12 8"><animate attributeName="stroke-dashoffset" values="0;-40" dur="1.2s" repeatCount="indefinite"/></path>
  <path d="M750 116 l15 9 -15 9" fill="none" stroke="#2563eb" stroke-width="3"/>
  <rect x="360" y="103" width="130" height="35" rx="7" fill="#dbeafe" stroke="#2563eb"/><text x="425" y="125" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">SYN initial</text>
  <path d="M770 178 H105" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4 9"/>
  <text x="445" y="168" text-anchor="middle" font-size="14" fill="#64748b">Aucune réponse visible dans cet exemple</text>
  <path d="M110 220 H765" stroke="#b91c1c" stroke-width="4" stroke-dasharray="12 8"><animate attributeName="stroke-dashoffset" values="0;-40" dur="1.2s" repeatCount="indefinite"/></path>
  <path d="M750 211 l15 9 -15 9" fill="none" stroke="#b91c1c" stroke-width="3"/>
  <rect x="334" y="198" width="184" height="36" rx="7" fill="#fee2e2" stroke="#b91c1c"/><text x="426" y="221" text-anchor="middle" font-size="15" font-weight="700" fill="#991b1b">SYN retransmis</text>
  <rect x="80" y="270" width="730" height="27" rx="6" fill="#e2e8f0"/>
  <rect x="80" y="270" width="25" height="27" rx="6" fill="#2563eb">
    <animate attributeName="width" values="25;660;25" dur="5s" repeatCount="indefinite"/>
  </rect>
  <text x="80" y="333" font-size="14" fill="#334155">Une retransmission peut indiquer une perte, un filtrage silencieux ou un autre problème de chemin.</text>
  <text x="80" y="357" font-size="14" fill="#334155">Il faut examiner le côté serveur, les routes et les règles réseau avant de conclure.</text>
  <text x="80" y="382" font-size="13" fill="#64748b">Schéma didactique : les intervalles affichés ne sont pas une mesure chronométrique réelle.</text>
</g>
</svg>

## 10.5 Attention aux offloads

Une capture réalisée sur l’hôte émetteur peut présenter :

- des checksums qui semblent incorrects ;
- des segments plus grands que ceux observés sur le réseau ;
- des paquets regroupés ou séparés par des optimisations réseau.

Certaines cartes réseau calculent les checksums ou segmentent les données à proximité de l’émission. Une capture prise à cet endroit peut refléter un état avant le traitement final par le matériel.

Avant de déclarer une corruption du trafic, vérifiez le point de capture et les offloads.


# 11. Méthodologie de dépannage intermédiaire

Un diagnostic doit pouvoir être reproduit par un autre technicien.

## 11.1 Formuler une hypothèse vérifiable

Mauvaise hypothèse :

> Internet ne fonctionne pas.

Hypothèses plus utiles :

- Le résolveur configuré ne répond pas.
- La passerelle locale n’est pas joignable au niveau IP.
- La route vers le préfixe de destination est absente.
- Le service TCP refuse la connexion.
- Le serveur accepte la connexion, mais ne répond pas correctement à la requête HTTP.
- Le trafic volumineux est affecté par une difficulté de MTU.

Une hypothèse précise peut être confirmée ou infirmée par un test adapté.

## 11.2 Noter les conditions du test

Pour chaque observation, conservez si possible :

- l’heure ;
- l’équipement de départ ;
- l’équipement de destination ;
- les adresses et ports ;
- l’interface concernée ;
- les commandes exécutées ;
- les filtres utilisés ;
- le résultat attendu ;
- le résultat observé ;
- les changements récents.

Ne transmettez pas de secrets, de données sensibles ou de captures contenant du contenu confidentiel à des personnes non autorisées.

## 11.3 Utiliser un témoin fonctionnel

Lorsqu’un seul poste rencontre une panne, comparez-le à un poste fonctionnel du même contexte.

Lorsqu’un site complet rencontre une panne, comparez les observations sur plusieurs VLAN, routeurs ou points de présence selon l’architecture.

Le but n’est pas d’effectuer tous les tests partout, mais d’identifier le point où les symptômes commencent à diverger.


# 12. Travaux pratiques

## TP 1 — Cartographier un échange DNS

Objectif : identifier le résolveur, la question DNS et la réponse.

1. Lancez une capture sur une interface autorisée.
2. Utilisez le filtre d’affichage `dns`.
3. Exécutez `nslookup exemple.com`.
4. Identifiez la requête et la réponse correspondantes.
5. Notez le type de question et le contenu de la réponse.
6. Comparez ensuite avec un nom inexistant dans un domaine de test adapté.

Un cache DNS peut faire varier les échanges observés. Une requête réussie n’implique donc pas toujours qu’une nouvelle résolution externe a été effectuée.

## TP 2 — Lire une ouverture TCP

1. Lancez une capture.
2. Effectuez une connexion vers un service TCP autorisé.
3. Utilisez `tcp.flags.syn == 1`.
4. Repérez SYN et SYN-ACK.
5. Examinez l’ACK qui achève l’établissement classique.
6. Notez les adresses et ports aux deux extrémités.
7. Observez le reste de la connexion.

Si vous utilisez HTTPS, le contenu applicatif sera généralement chiffré par TLS. Il reste toutefois possible d’observer plusieurs métadonnées de transport.

## TP 3 — Observer le routage

Sous Windows :

```powershell
ipconfig /all
route print
tracert exemple.com
```

Sous Linux :

```bash
ip address
ip route
ip neigh
traceroute exemple.com
```

Comparez la configuration locale et les résultats du chemin. Un routeur qui ne répond pas au message de diagnostic n’est pas nécessairement incapable de transférer le trafic.

## TP 4 — Tester une application Web

Exécutez :

```bash
curl -Iv https://exemple.com
```

Observez séparément :

- la résolution du nom ;
- l'établissement du transport ;
- la négociation TLS ;
- la réponse HTTP.

Une erreur au niveau TLS n’est pas identique à un rejet TCP. Une réponse HTTP d’erreur prouve que certaines étapes précédentes ont réussi, mais ne signifie pas que l’opération applicative a abouti.


# 13. Exercices

## Exercice 1 — Correspondance des modèles

Expliquez pourquoi les couches Session et Présentation sont généralement regroupées dans la couche Application du modèle TCP/IP traditionnel.

## Exercice 2 — Adresses sur un chemin routé

Un poste envoie un paquet vers un serveur situé sur un réseau différent.

Quelle adresse MAC utilise-t-il comme destination dans la première trame Ethernet ? Quelles adresses IP apparaissent dans le paquet avant et après le premier routeur si aucun mécanisme ne les modifie ?

## Exercice 3 — SYN sans réponse

Wireshark montre plusieurs SYN vers le même serveur, sans SYN-ACK visible.

Donnez au moins quatre causes possibles et expliquez comment les départager.

## Exercice 4 — MTU

Des requêtes courtes fonctionnent, mais de gros transferts se bloquent.

Expliquez pourquoi la MTU est une hypothèse possible, et proposez quatre vérifications.

## Exercice 5 — DNS

Un poste résout un nom de domaine avec `nslookup`, mais la page Web ne s’ouvre pas.

Expliquez pourquoi la résolution réussie ne suffit pas et construisez une procédure de diagnostic.

## Exercice 6 — Filtre Wireshark

Quelle différence existe entre un filtre de capture et un filtre d’affichage ? Pourquoi est-ce important en investigation ?

## Exercice 7 — VLAN

Deux ordinateurs peuvent communiquer avec leur passerelle, mais ne peuvent pas communiquer directement entre eux. Donnez des hypothèses liées au VLAN, au routage et aux politiques de sécurité.

## Exercice 8 — Offload

Une capture effectuée sur l’émetteur présente des checksums TCP incorrects. Expliquez pourquoi cette observation ne prouve pas automatiquement que les trames présentes sur le réseau sont corrompues.

## Exercice 9 — TCP ou application ?

Une connexion TCP s’établit, puis le client reçoit une réponse HTTP `500`.

À quelles couches faut-il poursuivre le diagnostic ? Que démontre cette réponse, et que ne démontre-t-elle pas ?


# 14. Corrigés commentés

**Exercice 1**

Le modèle TCP/IP regroupe ces fonctions dans une couche Application plus large. Elles n’ont pas disparu : la gestion de session, la présentation des données ou le chiffrement peuvent être implémentés par différents protocoles et bibliothèques.

**Exercice 2**

Le poste utilise généralement la MAC de la passerelle locale ou du prochain saut. En l’absence de NAT ou de modification particulière, l’adresse IP source et l’adresse IP destination du paquet restent celles du poste et du serveur final lors du passage dans le premier routeur.

**Exercice 3**

Causes possibles : filtrage silencieux, hôte inaccessible, route incorrecte, perte sur le chemin, service ou système qui ne répond pas, capture effectuée au mauvais endroit.

Pour départager les cas, vérifiez les routes, les ACL, les journaux du service, les captures simultanées lorsque c’est possible, ainsi que la réponse depuis d’autres points du réseau.

**Exercice 4**

Une MTU incohérente peut empêcher le transport de certains paquets sans que les petits paquets soient affectés. Vérifiez le chemin, les interfaces et les tunnels, les messages ICMP pertinents, les tailles des paquets et les retransmissions. Comparez les captures à plusieurs points si possible.

**Exercice 5**

DNS ne prouve pas que le serveur fonctionne ni que le port est joignable. Vérifiez l’adresse obtenue, le chemin, la connexion au port, TLS, la réponse HTTP et les journaux autorisés du service.

**Exercice 6**

Le filtre de capture peut empêcher l’enregistrement de certains paquets. Le filtre d’affichage masque des paquets déjà enregistrés. Une capture incomplète ne peut pas être rendue complète en modifiant uniquement le filtre d’affichage.

**Exercice 7**

Hypothèses : isolation entre VLAN, ACL, règles de pare-feu, mauvais masque, politique de communication inter-VLAN ou filtrage local. Le fonctionnement de la passerelle ne prouve pas que les deux postes ont le droit de communiquer entre eux.

**Exercice 8**

La carte réseau peut calculer le checksum après le point de capture, en raison d’un offload. Il faut examiner les offloads et comparer éventuellement avec une capture externe avant de déclarer une corruption.

**Exercice 9**

La réponse HTTP `500` indique qu’une réponse HTTP a été reçue et que le traitement applicatif a rencontré une erreur côté serveur ou dans son contexte d’exécution. Le diagnostic doit se poursuivre au niveau applicatif, des dépendances et des journaux. Cela ne prouve pas que tous les composants internes du service sont sains.


# 15. Fiche de révision intermédiaire

- OSI est un modèle de référence à sept couches.
- TCP/IP est une architecture de protocoles souvent représentée en quatre couches.
- Les adresses MAC identifient la destination de liaison sur le lien courant.
- Les adresses IP participent au routage entre réseaux.
- Les ports identifient les extrémités de transport.
- Un routeur traite IP et construit une nouvelle trame sur le lien de sortie.
- Un VLAN sépare des domaines de couche 2.
- TCP utilise des séquences, des acquittements et des retransmissions.
- UDP transporte des datagrammes sans garantie de livraison intégrée.
- Une MTU incohérente peut provoquer des pannes partielles.
- DNS traduit ou recherche des informations associées à des noms ; il ne valide pas l’ensemble d’un service Web.
- Wireshark observe des paquets à un point précis ; une capture peut être incomplète.
- Chaque hypothèse de diagnostic doit être reliée à une observation testable.

## Glossaire

**ACL :** liste de contrôle d’accès utilisée pour autoriser ou bloquer certains trafics.

**DORA :** séquence pédagogique courante utilisée pour décrire l’attribution initiale des paramètres DHCP en IPv4.

**MSS :** quantité maximale de données TCP proposée pour un segment, hors en-têtes TCP et IP.

**MTU :** taille maximale d’une unité transportée sur un lien selon les règles du protocole concerné.

**NAT :** mécanisme qui traduit certaines informations d’adressage, parfois avec traduction des ports.

**Offload :** traitement délégué à la carte réseau ou au matériel.

**Préfixe :** portion de bits d’une adresse IP associée au réseau.

**Retransmission :** nouvel envoi de données dont la livraison n’a pas été confirmée dans les conditions prévues par le protocole.

**SYN :** indicateur TCP associé notamment à l’établissement d’une connexion.

**TLS :** protocole de sécurité utilisé pour protéger des communications.

**Trunk :** lien configuré pour transporter plusieurs VLAN selon les règles du matériel.

**VLAN :** réseau local logique associé à une séparation de couche 2.


## Conclusion

À ce niveau, il faut être capable de passer de la théorie aux observations concrètes.

Quand un service échoue, posez-vous les questions suivantes :

1. Où la communication fonctionne-t-elle encore ?
2. Quelle est la première observation qui contredit le fonctionnement attendu ?
3. Quelle couche ou fonction est impliquée par cette observation ?
4. Quelle preuve permet de départager les hypothèses ?
5. Le résultat est-il reproductible ?

Le niveau expert approfondira les diagnostics multi-sauts, NAT, les tunnels, les particularités de TCP, les limites des captures et la rédaction de conclusions techniquement défendables.