# Le modèle OSI & TCP/IP — Cours complet débutant

> **Niveau :** Débutant  
> **Domaine :** Réseaux informatiques  
> **Objectif :** comprendre le chemin parcouru par les données entre deux applications et acquérir une méthode simple de dépannage réseau.

---

## Sommaire

1. Pourquoi modéliser les réseaux ?
2. Comprendre les couches et les protocoles
3. Les sept couches OSI
4. Le modèle TCP/IP
5. OSI et TCP/IP : tableau de correspondance
6. Encapsulation et décapsulation
7. Adresses MAC, adresses IP et ports
8. Le rôle des équipements réseau
9. Comprendre un échange Web
10. Méthode de dépannage
11. Laboratoires pratiques
12. Exercices et corrigés
13. Glossaire et fiche de révision

---

# 1. Pourquoi modéliser les réseaux ?

Un réseau informatique permet à plusieurs appareils d’échanger des informations. Ces appareils peuvent être des ordinateurs, des téléphones, des serveurs, des imprimantes, des caméras IP ou des équipements industriels.

Pour communiquer, ils doivent respecter des règles communes. Ces règles définissent notamment la manière de représenter les données, d’identifier les destinataires, de signaler les erreurs et de transporter les informations.

Prenons une situation simple : un utilisateur ouvre un navigateur et visite un site Web.

Plusieurs opérations doivent réussir :

- L’ordinateur doit disposer d’une interface réseau fonctionnelle.
- Il doit pouvoir rejoindre le réseau local.
- Il doit posséder une configuration IP utilisable.
- Le nom du site doit pouvoir être résolu en adresse IP, si le navigateur utilise un nom.
- Le trafic doit pouvoir traverser les routeurs et les éventuels pare-feu.
- Une connexion doit être établie avec le service distant.
- Le serveur doit traiter la requête et renvoyer une réponse.
- Le navigateur doit interpréter cette réponse et afficher la page.

Si une seule de ces étapes échoue, l’utilisateur peut dire : « Internet ne fonctionne pas ».

Pourtant, la panne peut être très différente selon le cas. Un câble débranché, une mauvaise passerelle, une résolution DNS impossible et un serveur Web indisponible ne se corrigent pas de la même façon.

Le modèle OSI aide à classer les fonctions et les problèmes pour raisonner plus clairement.

## 1.1 Qu’est-ce que le modèle OSI ?

OSI signifie **Open Systems Interconnection**.

Le modèle OSI est un modèle de référence qui organise les fonctions d’une communication réseau en sept couches. Chaque couche représente une famille de responsabilités.

Il permet notamment de :

- communiquer avec des termes techniques communs ;
- apprendre les principes des réseaux dans un ordre logique ;
- identifier la nature probable d’une panne ;
- expliquer la coopération entre protocoles et équipements ;
- structurer des procédures de diagnostic ;
- comprendre l’encapsulation des données.

Le modèle OSI n’est pas un programme que l’on installe sur un ordinateur. C’est une représentation conceptuelle des différentes fonctions nécessaires à la communication.

## 1.2 L’analogie de la lettre

Imaginons que vous envoyiez une lettre à une personne qui habite dans une autre ville.

Vous rédigez d’abord le message. Vous le placez ensuite dans une enveloppe. Vous inscrivez les adresses nécessaires. La lettre est remise à un service de distribution, transportée et remise au destinataire. Celui-ci ouvre l’enveloppe et lit le message.

Chaque étape a un rôle différent.

Dans un réseau informatique, les opérations sont numériques, les règles sont définies par des protocoles et les enveloppes contiennent des informations de contrôle. Le principe de séparation des responsabilités reste utile.

Attention : l’analogie explique l’idée générale, mais une communication réseau est bien plus dynamique qu’une lettre. Les paquets peuvent suivre des chemins différents, être retransmis, être filtrés ou être traités par plusieurs intermédiaires.

---

# 2. Comprendre les couches et les protocoles

Une **couche** représente une responsabilité logique.

Un **protocole** définit les règles suivies par des participants qui échangent des informations.

Par exemple :

- Ethernet définit des mécanismes de communication sur un réseau local câblé.
- IP définit l’adressage logique et l’acheminement des paquets.
- TCP fournit un transport fiable et ordonné.
- UDP fournit un transport par datagrammes sans garantie de livraison intégrée.
- DNS permet de retrouver des informations à partir de noms de domaine.
- HTTP définit des échanges utilisés par les applications Web.

Les couches permettent d’éviter qu’un protocole ait à gérer toutes les opérations de bout en bout.

Une application Web n’a pas besoin de commander directement les signaux électriques du câble. Elle utilise des services fournis par d’autres éléments du système.

## 2.1 Services, interfaces et protocoles

Ces trois notions sont liées, mais différentes.

**Un service** est une capacité offerte à une couche supérieure.

**Une interface** définit comment une couche ou un composant utilise cette capacité.

**Un protocole** définit les règles de communication entre entités qui coopèrent à un même niveau logique.

Par exemple, une application peut demander au système d’exploitation d’envoyer des données sur une connexion TCP. Le protocole TCP gère le transport des octets, tandis que IP participe à leur acheminement entre réseaux.

## 2.2 Communication logique entre couches

Deux applications peuvent communiquer à travers plusieurs équipements. Les fonctions homologues sont décrites comme si elles échangeaient selon des règles communes, mais les données physiques transitent réellement par les interfaces réseau et les supports de transmission.

Le modèle est donc à la fois vertical, car les couches coopèrent sur une machine, et horizontal, car des protocoles organisent la communication entre les participants.

---

# 3. Les sept couches du modèle OSI

Il est important de connaître l’ordre des couches.

De la couche la plus proche des applications vers le média physique :

| Numéro | Couche | Fonction principale | Exemples de technologies ou de protocoles |
|---:|---|---|---|
| 7 | Application | Services réseau utilisés par les applications | HTTP, DNS, SMTP |
| 6 | Présentation | Représentation et transformation des données | Encodage, sérialisation, fonctions de chiffrement |
| 5 | Session | Organisation du dialogue | Gestion conceptuelle d’un dialogue |
| 4 | Transport | Communication entre processus | TCP, UDP |
| 3 | Réseau | Adressage logique et acheminement | IPv4, IPv6, ICMP |
| 2 | Liaison de données | Transmission de trames sur un lien | Ethernet, Wi-Fi |
| 1 | Physique | Signaux et transmission physique | Cuivre, fibre optique, radio |

Les exemples du tableau sont pédagogiques. Dans une architecture réelle, certaines fonctionnalités se trouvent dans des bibliothèques, dans des protocoles transversaux ou dans plusieurs couches à la fois.

## 3.1 Couche 7 — Application

La couche Application contient les protocoles qui fournissent des fonctions de communication aux logiciels.

Exemples :

- **HTTP** : échange de requêtes et de réponses pour le Web.
- **DNS** : recherche d’informations associées aux noms de domaine.
- **SMTP** : transfert de courrier électronique.
- **SSH** : accès distant sécurisé à un système.
- **DHCP** : attribution automatique de paramètres de configuration IP.

Une confusion fréquente consiste à croire que la couche Application représente exactement l’interface graphique de l’application. Ce n’est pas le cas.

Un navigateur possède une interface utilisateur, mais il utilise aussi des protocoles et des bibliothèques qui organisent les échanges réseau.

**Exemple :** lorsque vous demandez une page à un serveur Web, le navigateur construit une requête HTTP ou HTTPS. Les couches inférieures permettent de transporter cette requête.

### Questions à se poser à cette couche

- Le bon nom de domaine est-il utilisé ?
- Le service distant fonctionne-t-il ?
- La requête est-elle correcte ?
- Le serveur répond-il avec une erreur applicative ?
- Une authentification est-elle nécessaire ?

## 3.2 Couche 6 — Présentation

Dans le modèle OSI, la couche Présentation concerne la représentation des données.

Elle peut être associée conceptuellement à :

- l’encodage ;
- la conversion de formats ;
- la sérialisation ;
- la compression ;
- le chiffrement et le déchiffrement.

Deux systèmes doivent interpréter les données de façon compatible. Une séquence d’octets ne suffit pas si les participants ne savent pas comment la représenter.

Il faut cependant éviter une simplification excessive : dans les réseaux modernes, les fonctions de présentation ne sont pas toujours isolées dans une couche dédiée.

Par exemple, TLS est généralement implémenté au moyen de bibliothèques et de mécanismes qui ne correspondent pas parfaitement à une couche OSI indépendante.

## 3.3 Couche 5 — Session

La couche Session représente la gestion logique du dialogue entre applications.

Elle peut être associée à l’établissement, à la gestion et à la reprise d’un échange.

Cette distinction est utile pour comprendre les responsabilités, mais les protocoles modernes répartissent souvent ces fonctions entre les applications, les bibliothèques et les mécanismes de transport.

Ne cherchez donc pas systématiquement un protocole moderne unique qui représenterait toute la couche Session.

## 3.4 Couche 4 — Transport

La couche Transport organise les communications entre processus.

Elle utilise notamment des **ports** pour identifier les points d’extrémité des échanges.

Deux protocoles courants sont TCP et UDP.

### TCP

TCP fournit un flux d’octets fiable et ordonné. Il utilise notamment :

- des numéros de séquence ;
- des accusés de réception ;
- des retransmissions ;
- un contrôle de flux ;
- des mécanismes de contrôle de congestion.

TCP est utilisé par de nombreuses applications qui ont besoin d’un transport fiable.

### UDP

UDP transporte des datagrammes et utilise lui aussi des ports. Il ne garantit pas, à lui seul, que les données seront livrées, qu’elles arriveront dans l’ordre ou qu’elles seront retransmises.

UDP est utilisé par différentes applications, notamment certains échanges DNS, la voix sur IP, les jeux en réseau et des protocoles modernes comme QUIC.

**À retenir :** TCP n’est pas « plus rapide dans tous les cas » et UDP n’est pas « toujours meilleur pour la vidéo ». Le choix dépend des besoins du protocole applicatif.

## 3.5 Couche 3 — Réseau

La couche Réseau fournit l’adressage logique et l’acheminement entre réseaux.

IP est le protocole central de cette couche.

Une adresse IP identifie une interface dans un contexte réseau. Le préfixe IP permet de déterminer l’appartenance à un sous-réseau et participe à la décision d’acheminement.

Les routeurs examinent les paquets IP et utilisent leurs tables de routage afin de sélectionner un prochain saut.

Exemples de responsabilités :

- examiner l’adresse IP de destination ;
- rechercher une route adaptée ;
- choisir une interface ou un prochain saut ;
- diminuer le TTL IPv4 ou le Hop Limit IPv6 ;
- réencapsuler le paquet dans une trame adaptée au lien de sortie.

Le routage ne consiste pas à envoyer directement une trame Ethernet de l’ordinateur jusqu’au serveur distant. La trame change généralement à chaque lien routé.

## 3.6 Couche 2 — Liaison de données

La couche Liaison organise la transmission de trames sur un lien.

Ethernet et Wi-Fi possèdent des fonctions de liaison de données.

Sur un réseau Ethernet, les trames utilisent notamment des adresses MAC. Un commutateur Ethernet apprend les adresses MAC sources observées et construit une table qui l’aide à transférer les trames.

Dans un réseau IP, le poste émetteur doit souvent déterminer la MAC du prochain saut :

- ARP est utilisé pour résoudre les adresses IPv4 sur le lien local ;
- Neighbor Discovery, qui s’appuie sur ICMPv6, intervient pour les fonctions équivalentes en IPv6.

Une adresse MAC ne remplace pas une adresse IP. Elles répondent à des besoins différents.

## 3.7 Couche 1 — Physique

La couche Physique concerne la transmission physique des informations.

Les caractéristiques peuvent comprendre :

- le support utilisé ;
- les connecteurs ;
- les caractéristiques électriques ;
- les signaux optiques ;
- les fréquences radio ;
- la modulation ;
- le débit physique ;
- les limites physiques de transmission.

Exemples de problèmes physiques :

- câble débranché ;
- câble ou connecteur endommagé ;
- interface désactivée ;
- défaut optique ;
- signal Wi-Fi trop faible ;
- interférences radio ;
- problème d’alimentation d’un équipement.

Un câble connecté ne garantit pas que toute la communication fonctionne, mais l’absence de lien physique peut empêcher le reste des couches d’être utilisable.

---

# 4. Schéma SVG animé — Les sept couches OSI

Le schéma suivant présente les couches dans l’ordre. La surbrillance animée attire l’attention sur le transport, tandis que les colonnes indiquent le sens conceptuel de l’encapsulation et de la décapsulation.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 540" role="img" aria-labelledby="osi1-title osi1-desc">
<title id="osi1-title">Les sept couches du modèle OSI</title>
<desc id="osi1-desc">Sept couches de couleurs distinctes avec une surbrillance animée sur la couche Transport. Les flèches montrent les directions conceptuelles de l'émission et de la réception.</desc>
<defs>
  <marker id="osi1-arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#334155"/></marker>
</defs>
<rect width="900" height="540" rx="18" fill="#f8fafc"/>
<text x="30" y="38" fill="#0f172a" font-size="24" font-weight="700">Modèle OSI : les sept responsabilités</text>
<g font-family="Arial,sans-serif">
  <g>
    <rect x="45" y="65" width="500" height="48" rx="8" fill="#bfdbfe"/><text x="62" y="94" font-size="17" font-weight="700" fill="#1e3a8a">7 · Application</text><text x="523" y="94" text-anchor="end" font-size="14" fill="#1e3a8a">HTTP · DNS</text>
    <rect x="45" y="119" width="500" height="48" rx="8" fill="#c7d2fe"/><text x="62" y="148" font-size="17" font-weight="700" fill="#312e81">6 · Présentation</text><text x="523" y="148" text-anchor="end" font-size="14" fill="#312e81">Formats · encodage</text>
    <rect x="45" y="173" width="500" height="48" rx="8" fill="#ddd6fe"/><text x="62" y="202" font-size="17" font-weight="700" fill="#5b21b6">5 · Session</text><text x="523" y="202" text-anchor="end" font-size="14" fill="#5b21b6">Dialogue</text>
    <rect x="45" y="227" width="500" height="48" rx="8" fill="#bbf7d0"/><text x="62" y="256" font-size="17" font-weight="700" fill="#14532d">4 · Transport</text><text x="523" y="256" text-anchor="end" font-size="14" fill="#14532d">TCP · UDP · ports</text>
    <rect x="45" y="281" width="500" height="48" rx="8" fill="#fde68a"/><text x="62" y="310" font-size="17" font-weight="700" fill="#78350f">3 · Réseau</text><text x="523" y="310" text-anchor="end" font-size="14" fill="#78350f">IP · routage</text>
    <rect x="45" y="335" width="500" height="48" rx="8" fill="#fed7aa"/><text x="62" y="364" font-size="17" font-weight="700" fill="#9a3412">2 · Liaison</text><text x="523" y="364" text-anchor="end" font-size="14" fill="#9a3412">Trames · MAC</text>
    <rect x="45" y="389" width="500" height="48" rx="8" fill="#fecaca"/><text x="62" y="418" font-size="17" font-weight="700" fill="#991b1b">1 · Physique</text><text x="523" y="418" text-anchor="end" font-size="14" fill="#991b1b">Signaux · média</text>
  </g>
  <rect x="39" y="221" width="512" height="60" rx="11" fill="none" stroke="#0f766e" stroke-width="4" opacity="0.9">
    <animate attributeName="stroke-opacity" values="0.25;1;0.25" dur="2.8s" repeatCount="indefinite"/>
  </rect>
  <path d="M610 95 V420" stroke="#334155" stroke-width="3" marker-end="url(#osi1-arrow)"/>
  <text x="635" y="175" font-size="18" font-weight="700" fill="#1e293b">Émission</text>
  <text x="635" y="199" font-size="14" fill="#475569">Vers le média</text>
  <path d="M790 420 V95" stroke="#0f766e" stroke-width="3" marker-end="url(#osi1-arrow)"/>
  <text x="770" y="455" font-size="17" font-weight="700" fill="#0f766e">Réception</text>
  <text x="635" y="478" font-size="14" fill="#475569">Décapsulation conceptuelle</text>
  <text x="45" y="490" font-size="13" fill="#64748b">Les fonctions réelles peuvent être réparties différemment selon les protocoles.</text>
</g>
</svg>

---

# 5. Le modèle TCP/IP

Le modèle TCP/IP est associé à l’architecture de protocoles utilisée sur Internet et dans de nombreux réseaux privés.

Une représentation courante contient quatre couches :

| Couche TCP/IP | Rôle | Exemples |
|---|---|---|
| Application | Protocoles utilisés par les logiciels | HTTP, DNS, SMTP, SSH |
| Transport | Communication entre processus | TCP, UDP |
| Internet | Adressage logique et acheminement | IPv4, IPv6, ICMP |
| Accès réseau | Transmission sur le réseau local et support | Ethernet, Wi-Fi |

Certains cours utilisent un modèle TCP/IP en cinq couches en séparant les fonctions de liaison et les fonctions physiques. Les deux représentations peuvent être utiles, à condition d’annoncer le modèle employé.

## 5.1 Pourquoi le modèle TCP/IP regroupe-t-il certaines couches OSI ?

Le modèle OSI sépare sept familles de fonctions. Le modèle TCP/IP traditionnel regroupe plusieurs fonctions de présentation, de session et d’application dans une couche Application plus large.

Cette différence ne signifie pas que les fonctions de présentation et de session ont disparu. Elle signifie qu’elles ne sont pas isolées de la même manière dans ce modèle simplifié.

## 5.2 Tableau de correspondance

| OSI | TCP/IP à quatre couches |
|---|---|
| Couche 7 — Application | Application |
| Couche 6 — Présentation | Application |
| Couche 5 — Session | Application |
| Couche 4 — Transport | Transport |
| Couche 3 — Réseau | Internet |
| Couche 2 — Liaison | Accès réseau |
| Couche 1 — Physique | Accès réseau |

Cette correspondance est approximative. Il s’agit d’une comparaison conceptuelle, pas d’une équivalence parfaite entre toutes les technologies.

---

# 6. Encapsulation et décapsulation

L’encapsulation est l’un des concepts les plus importants en réseau.

Lorsqu’une application émet des données, les couches ajoutent progressivement les informations nécessaires à la communication.

Exemple simplifié :

1. L’application produit des données.
2. TCP ajoute les informations de transport si l’application utilise TCP.
3. IP ajoute un en-tête contenant notamment les adresses IP.
4. Ethernet ou un autre protocole de liaison ajoute les informations requises sur le lien.
5. Le média transmet les symboles ou bits.

Le destinataire effectue le processus inverse, appelé décapsulation.

Les unités de données portent des noms qui varient selon les protocoles. Une convention courante distingue :

- **données** : unité visible au niveau applicatif ;
- **segment TCP** : unité de données TCP ;
- **datagramme UDP** : unité de données UDP ;
- **paquet IP** : unité transportée au niveau IP ;
- **trame** : unité de données de la liaison ;
- **bits ou symboles** : éléments transmis par le média physique.

Le terme général utilisé pour une unité de données de protocole est **PDU**.

## 6.1 Schéma SVG animé — Construction des enveloppes

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 930 390" role="img" aria-labelledby="enc1-title enc1-desc">
<title id="enc1-title">Encapsulation des données réseau</title>
<desc id="enc1-desc">Les données applicatives sont enrichies par les en-têtes TCP, IP et Ethernet. Des flèches animées montrent le sens de progression de l'encapsulation.</desc>
<rect width="930" height="390" rx="18" fill="#f8fafc"/>
<text x="28" y="38" fill="#0f172a" font-size="23" font-weight="700">De données applicatives à trame réseau</text>
<g font-family="Arial,sans-serif" font-size="14" font-weight="700">
  <rect x="35" y="82" width="170" height="64" rx="8" fill="#bfdbfe" stroke="#2563eb" stroke-width="2"/>
  <text x="120" y="108" text-anchor="middle" fill="#1e3a8a">Données</text><text x="120" y="128" text-anchor="middle" fill="#1e3a8a" font-weight="400">Application</text>
  <path d="M210 114 H245" stroke="#334155" stroke-width="2" stroke-dasharray="6 5"><animate attributeName="stroke-dashoffset" values="0;-22" dur="1s" repeatCount="indefinite"/></path>
  <path d="M238 106 l9 8 -9 8" fill="none" stroke="#334155" stroke-width="2"/>
  <rect x="255" y="82" width="90" height="64" rx="8" fill="#bbf7d0" stroke="#15803d" stroke-width="2"/><text x="300" y="118" text-anchor="middle" fill="#14532d">TCP</text>
  <rect x="345" y="82" width="160" height="64" rx="8" fill="#bfdbfe" stroke="#2563eb" stroke-width="2"/><text x="425" y="108" text-anchor="middle" fill="#1e3a8a">Données</text><text x="425" y="128" text-anchor="middle" fill="#1e3a8a" font-weight="400">Segment TCP</text>
  <path d="M300 151 V176 H360" fill="none" stroke="#334155" stroke-width="2" stroke-dasharray="5 5"><animate attributeName="stroke-dashoffset" values="0;-20" dur="1s" repeatCount="indefinite"/></path>
  <rect x="255" y="181" width="90" height="64" rx="8" fill="#fde68a" stroke="#b45309" stroke-width="2"/><text x="300" y="218" text-anchor="middle" fill="#78350f">IP</text>
  <rect x="345" y="181" width="300" height="64" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/><text x="495" y="208" text-anchor="middle" fill="#1e3a8a">En-tête IP + TCP + données</text><text x="495" y="228" text-anchor="middle" fill="#1e3a8a" font-weight="400">Paquet IP</text>
  <path d="M300 250 V270 H360" fill="none" stroke="#334155" stroke-width="2" stroke-dasharray="5 5"><animate attributeName="stroke-dashoffset" values="0;-20" dur="1s" repeatCount="indefinite"/></path>
  <rect x="255" y="275" width="110" height="64" rx="8" fill="#fecaca" stroke="#b91c1c" stroke-width="2"/><text x="310" y="312" text-anchor="middle" fill="#7f1d1d">Ethernet</text>
  <rect x="365" y="275" width="400" height="64" rx="8" fill="#e2e8f0" stroke="#475569" stroke-width="2"/><text x="565" y="302" text-anchor="middle" fill="#0f172a">En-tête Ethernet + paquet IP + contrôle</text><text x="565" y="322" text-anchor="middle" fill="#0f172a" font-weight="400">Trame Ethernet simplifiée</text>
  <text x="690" y="102" fill="#334155">Transport</text><text x="690" y="127" fill="#334155" font-weight="400">Ports, fiabilité TCP</text>
  <text x="690" y="194" fill="#334155">Réseau</text><text x="690" y="219" fill="#334155" font-weight="400">Adresses IP</text>
  <text x="790" y="290" fill="#334155">Liaison</text><text x="790" y="315" fill="#334155" font-weight="400">Adresses MAC</text>
</g>
<text x="35" y="368" font-size="13" fill="#475569">Schéma pédagogique : les détails exacts varient selon le protocole et les options utilisées.</text>
</svg>

## 6.2 Pourquoi les en-têtes sont-ils nécessaires ?

Un en-tête transporte les informations nécessaires au protocole qui l’utilise.

Exemples :

- L’en-tête TCP contient des ports et des numéros de séquence.
- L’en-tête IP contient des adresses et des informations utiles à l’acheminement.
- L’en-tête Ethernet contient des adresses MAC source et destination.
- Une trame Ethernet comporte aussi un mécanisme de contrôle d’erreur.

Chaque information a une portée précise. L’adresse MAC concerne le lien local ; l’adresse IP intervient dans l’acheminement entre réseaux ; le port identifie une extrémité de transport.

## 6.3 Ce qui se passe au niveau d’un routeur

Un routeur reçoit une trame sur une interface, traite le paquet IP contenu dans cette trame puis construit une nouvelle enveloppe de liaison pour l’interface de sortie.

La trame de départ n’est donc généralement pas conservée de bout en bout.

En revanche, l’adresse IP de destination reste normalement celle de la destination finale. Des mécanismes comme NAT, les proxys et les tunnels peuvent modifier cette observation.

---

# 7. Adresses MAC, adresses IP et ports

Ces trois notions sont fondamentales et ne doivent pas être confondues.

| Élément | Rôle principal | Portée |
|---|---|---|
| Adresse MAC | Identifier une interface au niveau de la liaison | Lien local |
| Adresse IP | Identifier une interface dans le plan IP et permettre le routage | Entre réseaux |
| Port TCP/UDP | Identifier un point d’extrémité de transport | Communication entre processus |

## 7.1 Adresse MAC

Une adresse MAC Ethernet classique est représentée par six octets, souvent écrits sous forme hexadécimale, par exemple :

`00:1A:2B:3C:4D:5E`

C’est une représentation illustrative. Une adresse MAC peut être administrée localement par le système et ne doit pas être considérée comme une identité universelle et immuable d’une personne ou d’un appareil.

## 7.2 Adresse IP

Une adresse IPv4 est composée de 32 bits et est souvent représentée sous la forme de quatre nombres décimaux :

`192.0.2.10`

Cette adresse appartient à une plage réservée à la documentation. Elle sert ici d’exemple.

Une adresse IPv6 utilise 128 bits et est généralement représentée en hexadécimal avec des deux-points.

L’adresse IP n’indique pas nécessairement l’identité permanente d’une machine. Elle peut changer selon le réseau, la configuration et les mécanismes employés.

## 7.3 Port

Un port TCP ou UDP est un numéro qui aide le système à distribuer les données au bon point d’extrémité de transport.

Exemples courants :

- TCP 80 : HTTP traditionnel ;
- TCP 443 : HTTPS utilisant TCP ;
- UDP 53 et TCP 53 : DNS, selon le type de requête et les circonstances ;
- TCP 22 : SSH.

Ce sont des conventions courantes. La présence d’un numéro de port ne garantit pas qu’un service est réellement disponible sur ce port.

## 7.4 Quand utilise-t-on la passerelle ?

Si un poste souhaite communiquer avec une destination qui n’est pas sur son sous-réseau local, il envoie généralement le paquet à un routeur, souvent appelé passerelle par défaut.

La trame locale utilise alors l’adresse MAC de la passerelle comme adresse MAC de destination. L’adresse IP de destination du paquet reste normalement celle de l’hôte final.

---

# 8. Les équipements réseau et leurs rôles

| Équipement | Rôle principal | Couche dominante |
|---|---|---|
| Répéteur ou équipement physique simple | Régénération ou transmission de signaux | 1 |
| Commutateur Ethernet classique | Transfert de trames selon les MAC | 2 |
| Routeur | Acheminement des paquets IP | 3 |
| Pare-feu | Filtrage de trafic selon des règles | Plusieurs couches possibles |
| Point d’accès Wi-Fi | Connexion sans fil au réseau local | Principalement 2 |
| Proxy applicatif | Intermédiaire de communication applicative | Principalement 7 |
| Équilibreur de charge | Répartition de charges selon sa configuration | Plusieurs couches possibles |

Ces associations sont pédagogiques. Un équipement moderne peut intégrer plusieurs fonctions.

## 8.1 Fonctionnement simplifié d’un commutateur

Un commutateur Ethernet observe les adresses MAC sources des trames reçues et associe ces adresses aux ports d’entrée.

Lorsqu’une trame arrive :

1. Le commutateur apprend éventuellement l’adresse MAC source.
2. Il consulte sa table de transfert pour la destination.
3. S’il connaît le port de destination, il transmet selon les règles applicables.
4. Si la destination est inconnue, il peut diffuser la trame dans le VLAN concerné, selon le type de trame et sa configuration.
5. Les mécanismes de sécurité ou de contrôle peuvent modifier ce comportement.

## 8.2 Fonctionnement simplifié d’un routeur

Un routeur utilise l’adresse IP de destination pour rechercher une route applicable.

Il ne se contente pas de regarder l’adresse MAC de destination de la trame entrante. Cette dernière sert à livrer la trame sur le lien local.

Le routeur traite le paquet IP, applique les contrôles nécessaires et choisit un prochain saut.

---

# 9. Comprendre un échange Web de bout en bout

Imaginons que l’ordinateur utilise le nom `www.exemple.test`.

Les noms utilisés ici sont illustratifs.

Une séquence simplifiée peut être la suivante :

1. L’utilisateur demande le site dans le navigateur.
2. Le navigateur ou le système cherche à résoudre le nom.
3. Le système identifie l’adresse IP à contacter.
4. Il détermine si la destination se trouve sur le réseau local.
5. Si elle est distante, il utilise une route et généralement sa passerelle par défaut.
6. Il construit les informations de transport nécessaires.
7. IP prépare un paquet destiné à l’hôte distant.
8. La liaison encapsule le paquet pour le prochain lien.
9. Les routeurs acheminent les paquets vers le réseau de destination.
10. Le serveur traite les données reçues et répond.
11. Le client reçoit et interprète la réponse.

Selon la version HTTP, le transport et les mécanismes de sécurité employés, certaines étapes diffèrent. Par exemple, HTTP/3 utilise QUIC au-dessus d’UDP, tandis que les configurations HTTP/1.1 ou HTTP/2 classiques utilisent généralement TCP avec TLS pour HTTPS.

## 9.1 Schéma SVG animé — Parcours dans un réseau routé

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 390" role="img" aria-labelledby="route1-title route1-desc">
<title id="route1-title">Acheminement entre deux réseaux</title>
<desc id="route1-desc">Le paquet passe d'un ordinateur à un routeur puis à un serveur. Les flux animés sont distincts sur les deux liens ; chaque routeur réencapsule le paquet pour le lien de sortie.</desc>
<rect width="940" height="390" rx="18" fill="#f8fafc"/>
<text x="28" y="38" fill="#0f172a" font-size="23" font-weight="700">Trajet logique d’un paquet IP</text>
<g font-family="Arial,sans-serif">
  <rect x="40" y="105" width="190" height="116" rx="12" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="135" y="140" text-anchor="middle" font-size="19" font-weight="700" fill="#1e3a8a">PC source</text>
  <text x="135" y="169" text-anchor="middle" font-size="14" fill="#1e3a8a">192.0.2.10</text>
  <text x="135" y="194" text-anchor="middle" font-size="13" fill="#1e3a8a">Réseau A</text>
  <rect x="373" y="91" width="196" height="144" rx="12" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="471" y="132" text-anchor="middle" font-size="19" font-weight="700" fill="#92400e">Routeur</text>
  <text x="471" y="161" text-anchor="middle" font-size="14" fill="#92400e">Analyse IP</text>
  <text x="471" y="185" text-anchor="middle" font-size="14" fill="#92400e">Choix du prochain saut</text>
  <text x="471" y="209" text-anchor="middle" font-size="13" fill="#92400e">TTL / Hop Limit</text>
  <rect x="710" y="105" width="190" height="116" rx="12" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="805" y="140" text-anchor="middle" font-size="19" font-weight="700" fill="#166534">Serveur</text>
  <text x="805" y="169" text-anchor="middle" font-size="14" fill="#166534">198.51.100.20</text>
  <text x="805" y="194" text-anchor="middle" font-size="13" fill="#166534">Réseau B</text>
  <path d="M230 161 H368" stroke="#64748b" stroke-width="5"/>
  <path d="M569 161 H705" stroke="#64748b" stroke-width="5"/>
  <path d="M230 161 H368" stroke="#2563eb" stroke-width="3" stroke-dasharray="12 10">
    <animate attributeName="stroke-dashoffset" values="0;-44" dur="1.5s" repeatCount="indefinite"/>
  </path>
  <path d="M569 161 H705" stroke="#16a34a" stroke-width="3" stroke-dasharray="12 10">
    <animate attributeName="stroke-dashoffset" values="0;-44" dur="1.1s" repeatCount="indefinite"/>
  </path>
  <path d="M358 151 l12 10 -12 10 M695 151 l12 10 -12 10" fill="none" stroke="#334155" stroke-width="3"/>
  <rect x="248" y="113" width="102" height="28" rx="5" fill="#bfdbfe" stroke="#2563eb"/>
  <text x="299" y="132" text-anchor="middle" font-size="12" fill="#1e3a8a">Trame A</text>
  <rect x="588" y="113" width="102" height="28" rx="5" fill="#bbf7d0" stroke="#16a34a"/>
  <text x="639" y="132" text-anchor="middle" font-size="12" fill="#14532d">Trame B</text>
  <text x="40" y="273" font-size="15" font-weight="700" fill="#1e293b">Ce qui change :</text>
  <text x="40" y="298" font-size="14" fill="#475569">L’enveloppe de liaison et les MAC sont adaptées à chaque lien.</text>
  <text x="40" y="326" font-size="15" font-weight="700" fill="#1e293b">Ce qui reste normalement stable :</text>
  <text x="40" y="351" font-size="14" fill="#475569">Les adresses IP source et destination, hors NAT ou mécanismes particuliers.</text>
</g>
</svg>

---

# 10. Méthode de dépannage par couches

L’ordre suivant est une méthode pédagogique utile. En pratique, on peut aussi partir du symptôme et tester directement l’application.

## 10.1 Couche physique

Vérifications :

- Le câble est-il branché ?
- L’interface est-elle activée ?
- Les voyants indiquent-ils un lien ?
- Le signal Wi-Fi est-il suffisamment bon ?
- L’équipement est-il alimenté ?

## 10.2 Couche Liaison

Vérifications :

- Le poste est-il associé au bon réseau Wi-Fi ?
- Le port du commutateur est-il dans le bon VLAN ?
- Le lien est-il stable ?
- L’apprentissage MAC est-il cohérent avec la topologie ?
- Une protection de port bloque-t-elle le trafic ?

## 10.3 Couche Réseau

Vérifications :

- Le poste possède-t-il une adresse IP correcte ?
- Le masque ou préfixe est-il correct ?
- La passerelle est-elle configurée ?
- La destination est-elle sur le sous-réseau local ?
- Une route adaptée existe-t-elle ?
- La résolution ARP ou Neighbor Discovery fonctionne-t-elle ?

## 10.4 Couche Transport

Vérifications :

- Le service écoute-t-il sur le port attendu ?
- La connexion TCP aboutit-elle ?
- Un pare-feu filtre-t-il le port ?
- Le protocole utilise-t-il TCP, UDP ou QUIC ?
- Observe-t-on des retransmissions ou un rejet de connexion ?

## 10.5 Couches applicatives

Vérifications :

- Le nom DNS se résout-il correctement ?
- Le serveur fonctionne-t-il ?
- Le certificat TLS est-il valide dans le contexte d’utilisation ?
- L’URL et les identifiants sont-ils corrects ?
- L’application renvoie-t-elle une erreur HTTP ?
- Un proxy ou un répartiteur intervient-il ?

## 10.6 Un test ne prouve pas tout

Un ping réussi prouve qu’un échange ICMP a fonctionné dans les conditions du test. Il ne prouve pas que le port HTTPS est ouvert ni que le service Web fonctionne.

L’échec d’un ping ne prouve pas non plus que la machine distante est arrêtée. ICMP peut être bloqué par une politique de sécurité alors que d’autres services restent accessibles.

Le diagnostic repose sur une accumulation de preuves.

---

# 11. Laboratoires pratiques

## Laboratoire 1 — Lire sa configuration IP

### Sous Windows

```powershell
ipconfig /all
route print
arp -a
```

### Sous Linux

```bash
ip address
ip route
ip neigh
```

Objectifs :

1. Identifier l’adresse IP de l’interface active.
2. Identifier le préfixe ou le masque.
3. Relever la passerelle par défaut.
4. Identifier les résolveurs DNS configurés.
5. Observer les voisins connus sur le lien local.

N’interprétez pas une adresse sans tenir compte du contexte : une adresse virtuelle, un VPN ou plusieurs interfaces peuvent modifier les résultats.

## Laboratoire 2 — Vérifier la résolution DNS

Sous Windows ou Linux, selon les outils disponibles :

```text
nslookup exemple.com
```

Ou, si `dig` est installé :

```bash
dig exemple.com
```

Observez :

- le nom demandé ;
- le résolveur interrogé ;
- la réponse obtenue ;
- le type de réponse ;
- le temps nécessaire ;
- les éventuelles erreurs.

La réponse d’un nom de domaine peut varier selon la géographie, le type d’enregistrement, le résolveur et le moment.

## Laboratoire 3 — Observer le chemin

```bash
traceroute exemple.com
```

Sous Windows :

```powershell
tracert exemple.com
```

Le résultat présente une série de sauts visibles selon le comportement des routeurs et des politiques de filtrage.

Un saut affiché sous forme d’astérisques ne prouve pas nécessairement que le trafic applicatif est interrompu. Un routeur peut ne pas répondre aux messages de diagnostic tout en transférant normalement le trafic.

## Laboratoire 4 — Tester un service HTTPS

Avec `curl` :

```bash
curl -Iv https://exemple.com
```

Sous Windows PowerShell, un test de port TCP peut être effectué avec :

```powershell
Test-NetConnection exemple.com -Port 443
```

Ces commandes ne font pas toutes exactement le même test.

- Le test de port cherche à établir une connexion TCP vers le port indiqué.
- `curl` peut également mettre en évidence des erreurs liées à TLS, HTTP ou au traitement du nom.
- Aucun résultat unique ne doit être interprété hors contexte.

N’effectuez les tests que sur des systèmes que vous êtes autorisé à examiner.

---

# 12. Exercices

## Exercice 1 — Les couches

Citez les sept couches OSI dans l’ordre, de la couche 1 à la couche 7.

## Exercice 2 — Les adresses

Associez chaque élément à sa fonction principale :

- Adresse MAC
- Adresse IP
- Port TCP

Fonctions :

A. Identifier un point d’extrémité de transport.  
B. Identifier une destination logique au niveau IP.  
C. Identifier l’interface de destination sur un lien local.

## Exercice 3 — TCP et UDP

Expliquez la différence essentielle entre TCP et UDP en matière de fiabilité et d’ordre.

## Exercice 4 — Routage

Un ordinateur veut contacter un serveur qui se trouve sur un réseau IP différent. Quelle adresse MAC utilise-t-il généralement dans la première trame Ethernet ?

## Exercice 5 — Le ping

Le ping fonctionne, mais l’application Web ne répond pas. Citez au moins quatre pistes de diagnostic.

## Exercice 6 — Encapsulation

Remettez les unités suivantes dans l’ordre habituel d’encapsulation pour une application qui utilise TCP sur Ethernet :

- Trame Ethernet
- Données applicatives
- Paquet IP
- Segment TCP

## Exercice 7 — Les équipements

Associez les fonctions :

- Commutateur Ethernet classique
- Routeur IP
- Pare-feu

Fonctions :

A. Filtrer un trafic selon une politique de sécurité.  
B. Transférer des trames selon des informations de couche liaison.  
C. Acheminer des paquets entre réseaux IP.

## Exercice 8 — Raisonnement

Un poste ne peut pas accéder à un site par son nom. Donnez une procédure de diagnostic qui distingue un problème DNS d’un problème de transport ou de service Web.

---

# 13. Corrigés commentés

**Exercice 1**

1. Physique
2. Liaison de données
3. Réseau
4. Transport
5. Session
6. Présentation
7. Application

**Exercice 2**

- Adresse MAC : C.
- Adresse IP : B.
- Port TCP : A.

**Exercice 3**

TCP fournit un flux fiable et ordonné en utilisant notamment les accusés de réception et les retransmissions. UDP transporte des datagrammes, mais ne garantit pas, à lui seul, la livraison ou l’ordre.

**Exercice 4**

Le poste utilise généralement l’adresse MAC de sa passerelle ou du prochain saut sur le lien local. L’adresse IP de destination demeure normalement celle du serveur final.

**Exercice 5**

Exemples de pistes :

- résolution DNS ;
- port TCP utilisé par le site ;
- filtrage réseau ;
- erreur TLS ou certificat ;
- serveur Web indisponible ;
- proxy ou répartiteur de charge ;
- problème de routage ;
- erreur de l’application.

**Exercice 6**

Données applicatives → segment TCP → paquet IP → trame Ethernet.

Au niveau physique, la trame est transmise sous la forme de signaux ou de symboles.

**Exercice 7**

- Commutateur : B.
- Routeur : C.
- Pare-feu : A.

**Exercice 8**

Une procédure possible :

1. Vérifier la configuration IP et la passerelle.
2. Résoudre le nom avec `nslookup` ou `dig`.
3. Vérifier quelle adresse IP a été obtenue.
4. Tester le service sur le port approprié.
5. Examiner l’établissement TCP et la négociation TLS si applicable.
6. Consulter l’erreur HTTP et les journaux autorisés du service.
7. Comparer avec un autre poste fonctionnel si possible.

L’ordre peut être adapté au symptôme. Il est essentiel de séparer les observations des hypothèses.

---

# 14. Fiche de révision

- Le modèle OSI possède sept couches.
- TCP/IP regroupe les fonctions en un modèle plus proche de la suite de protocoles utilisée sur Internet.
- Une adresse MAC concerne principalement le lien local.
- Une adresse IP sert à l’acheminement entre réseaux.
- Un port identifie une extrémité de transport.
- TCP fournit un transport fiable et ordonné.
- UDP ne fournit pas à lui seul de garantie de livraison.
- Un commutateur Ethernet classique traite principalement les trames.
- Un routeur IP sélectionne un prochain saut.
- L’encapsulation ajoute les informations nécessaires à chaque protocole.
- La décapsulation retire ces informations à la réception.
- Un seul test réussi ou échoué ne suffit pas à prouver l’état de toutes les couches.

## Glossaire

**ARP :** protocole utilisé pour la résolution d’adresses IPv4 sur un lien local.

**DNS :** système distribué de noms de domaine.

**Encapsulation :** ajout des informations de contrôle propres aux protocoles utilisés.

**IP :** protocole d’adressage logique et d’acheminement des paquets.

**MAC :** adresse utilisée par la liaison de données sur les technologies concernées.

**MTU :** unité représentant la taille maximale transportable selon les règles du lien considéré.

**PDU :** unité de données de protocole.

**Port :** numéro permettant d’identifier une extrémité de transport TCP ou UDP.

**Routeur :** équipement qui prend des décisions d’acheminement au niveau IP.

**TCP :** protocole de transport fiable et ordonné fondé sur une connexion.

**UDP :** protocole de transport par datagrammes, sans garantie de livraison intégrée.

**VLAN :** mécanisme de séparation logique de réseaux locaux de couche 2.

**Wireshark :** outil d’analyse de trafic réseau.

---

## Conclusion

Le modèle OSI et le modèle TCP/IP fournissent un vocabulaire commun pour comprendre une communication réseau.

Le véritable objectif n’est pas simplement de mémoriser sept noms. Il faut comprendre la fonction de chaque niveau, savoir quelles informations sont utilisées à chaque étape et être capable de construire des hypothèses de dépannage testables.

Le cours intermédiaire développera l’analyse de captures, le routage, les MTU, TCP/UDP et les défaillances plus subtiles. Le cours expert abordera l’analyse multi-sauts, les middleboxes, les tunnels, les limites de capture et le diagnostic fondé sur des preuves.