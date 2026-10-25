# TCP, UDP & Ports — Cours complet débutant

> **Niveau :** Débutant  
> **Domaine :** Réseaux informatiques  
> **Prérequis :** connaître les notions élémentaires d'adresse IP et de réseau local.  
> **Objectif :** comprendre le rôle de TCP, UDP et des ports, reconnaître leurs différences, identifier les principaux services réseau et effectuer les premiers tests de connectivité.


## Sommaire

1. Introduction aux protocoles de transport
2. Pourquoi TCP et UDP sont-ils nécessaires ?
3. Comprendre les ports réseau
4. Fonctionnement fondamental de TCP
5. Établissement d'une connexion TCP
6. Fiabilité, acquittements et retransmissions
7. Fonctionnement fondamental d'UDP
8. TCP contre UDP : comparaison complète
9. Les ports réseau les plus courants
10. Client, serveur, socket et connexion
11. Pare-feu, NAT et filtrage des ports
12. Schémas SVG animés
13. Premiers tests en ligne de commande
14. Travaux pratiques
15. Exercices et corrigés
16. Glossaire et fiche de révision


# 1. Introduction aux protocoles de transport

Lorsqu'un ordinateur communique avec un autre, plusieurs protocoles coopèrent.

IP permet principalement d'adresser les paquets et de les acheminer entre les réseaux. Mais IP ne permet pas, à lui seul, de fournir tous les mécanismes dont les applications ont besoin.

Imaginons un ordinateur qui exécute simultanément :

- un navigateur Web ;
- un client de messagerie ;
- un logiciel de visioconférence ;
- un client DNS ;
- une application de transfert de fichiers.

Ces programmes peuvent communiquer avec plusieurs serveurs en utilisant la même interface réseau et la même adresse IP.

Le système doit déterminer à quel programme remettre les données reçues. Il doit également fournir les garanties de transport nécessaires à chaque type d'application.

C'est là qu'intervient la couche Transport.

Les deux protocoles de transport les plus connus sur les réseaux IP sont :

- **TCP — Transmission Control Protocol** ;
- **UDP — User Datagram Protocol**.

TCP et UDP utilisent tous deux les numéros de ports. Ils ne fournissent cependant pas les mêmes services.

TCP apporte notamment un transport fiable et ordonné sous la forme d'un flux d'octets. UDP transporte des datagrammes sans assurer lui-même la livraison ou l'ordre des données.

Le choix du transport dépend de l'application et de son protocole.


# 2. Pourquoi TCP et UDP sont-ils nécessaires ?

## 2.1 Le problème du transport

IP peut acheminer un paquet vers une adresse de destination, mais IP ne garantit pas que ce paquet arrivera à destination.

Un paquet peut être perdu en raison d'une congestion, d'un problème de liaison, d'un changement de route ou d'une décision de filtrage.

Des paquets peuvent aussi arriver dans un ordre différent de celui de leur émission.

Une application doit donc choisir les mécanismes de communication qui correspondent à ses besoins.

Exemple : un logiciel qui télécharge un fichier doit généralement vérifier que tous les octets ont été reçus correctement et dans le bon ordre.

Un jeu multijoueur, en revanche, peut préférer recevoir régulièrement les états les plus récents plutôt que de bloquer son affichage en attendant une ancienne information retardée.

Ces exemples ne signifient pas que tous les jeux utilisent UDP ou que toutes les applications de transfert utilisent TCP. Ce sont des illustrations des compromis possibles.

## 2.2 Que fournit TCP ?

TCP fournit notamment :

- un flux d'octets fiable et ordonné ;
- des mécanismes de détection des données non acquittées ;
- des retransmissions ;
- des numéros de séquence ;
- des accusés de réception ;
- un contrôle de flux ;
- un contrôle de congestion.

Le logiciel peut ainsi lire un flux de données sans avoir à implémenter lui-même tous ces mécanismes de transport.

Attention : TCP ne garantit pas que l'application distante terminera une opération avec succès. Une connexion TCP peut fonctionner correctement alors que le serveur renvoie une erreur applicative.

## 2.3 Que fournit UDP ?

UDP fournit un transport par datagrammes.

Il possède notamment :

- des ports source et destination ;
- une longueur de datagramme ;
- un checksum utilisé pour détecter certaines erreurs, selon les règles du protocole et de la famille IP concernée.

UDP ne met pas en œuvre, à lui seul, les mécanismes de retransmission et d'ordre de TCP.

Un datagramme peut être perdu, retardé ou reçu dans un ordre différent de celui de son émission. Une application peut cependant ajouter ses propres mécanismes de fiabilité au-dessus d'UDP.

## 2.4 Analogie simple

On peut comparer les deux protocoles à deux stratégies d'échange.

**TCP :** les correspondants établissent une connexion logique, suivent les données transmises et utilisent des mécanismes de récupération lorsqu'une partie des données n'est pas acquittée.

**UDP :** l'application envoie un datagramme et poursuit son travail sans qu'UDP attende automatiquement un accusé de réception de l'application distante.

Cette analogie reste simplifiée. TCP et UDP ne sont pas des garanties absolues de réussite : une connexion TCP peut échouer et un protocole applicatif basé sur UDP peut être fiable.


# 3. Comprendre les ports réseau

Une adresse IP permet d'identifier une destination dans le réseau IP, mais elle ne suffit pas à distinguer tous les services présents sur une machine.

Un serveur peut fournir plusieurs services sur la même adresse IP.

Par exemple :

- un serveur Web ;
- un serveur SSH ;
- un service DNS ;
- un service de courrier électronique.

Les ports permettent au système d'identifier les extrémités de transport utilisées par ces services.

## 3.1 Qu'est-ce qu'un port ?

Un port TCP ou UDP est un numéro de 16 bits. Les valeurs possibles vont donc de 0 à 65535.

Le numéro de port est utilisé par le protocole de transport pour remettre les données au bon point d'extrémité.

Un port n'est pas :

- un connecteur physique ;
- une prise Ethernet ;
- une adresse IP ;
- une garantie qu'un service fonctionne ;
- une règle automatique de pare-feu.

Le fait qu'un serveur utilise habituellement le port TCP 443 pour HTTPS ne signifie pas que tous les serveurs utilisant ce port offrent nécessairement HTTPS.

Les services choisissent leur configuration, sous réserve des règles applicables et des contraintes du système.

## 3.2 Port source et port destination

Lorsqu'un client contacte un serveur, la communication comprend habituellement :

- l'adresse IP du client ;
- le port source du client ;
- l'adresse IP du serveur ;
- le port destination du serveur ;
- le protocole de transport utilisé.

Exemple pédagogique :

```text
Client : 192.0.2.25, port TCP 51000
Serveur : 198.51.100.80, port TCP 443

Flux TCP :
192.0.2.25:51000 → 198.51.100.80:443
```

Les adresses utilisées ici appartiennent à des plages réservées à la documentation.

Le serveur écoute généralement sur un port de service connu. Le client utilise souvent un port source temporaire attribué par son système.

Le serveur ne répond pas nécessairement au port source du client avec un nouveau port : dans une connexion TCP classique, les deux directions appartiennent au même flux et utilisent les mêmes deux ports, avec les rôles source et destination inversés dans les segments de retour.

## 3.3 Les trois catégories de ports

Selon la classification traditionnelle de l'IANA :

| Plage | Nom | Usage général |
|---|---|---|
| 0–1023 | Ports système, souvent appelés ports bien connus | Services largement connus |
| 1024–49151 | Ports enregistrés | Services enregistrés |
| 49152–65535 | Ports dynamiques ou privés | Utilisation dynamique ou locale |

Ces catégories ne signifient pas que chaque port d'une plage est obligatoirement utilisé, ni que tous les systèmes utilisent exactement la même stratégie pour choisir leurs ports sources temporaires.

La plage utilisée par un système pour ses ports éphémères peut varier selon le système d'exploitation et sa configuration.

La table officielle de référence est tenue par l'[IANA](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml).

## 3.4 TCP et UDP possèdent des espaces de ports distincts

Le port TCP 53 et le port UDP 53 sont associés à des espaces de transport différents.

Un service qui utilise UDP sur un numéro donné n'ouvre pas automatiquement ce numéro en TCP.

Cette distinction est importante lors de la configuration des pare-feu.

Exemple :

```text
UDP/53  : trafic DNS sur UDP
TCP/53  : trafic DNS sur TCP
TCP/443 : HTTPS utilisant TCP
UDP/443 : peut notamment transporter QUIC et HTTP/3
```

Il ne faut donc jamais considérer un numéro de port isolément. Le numéro doit être associé au protocole de transport et au contexte du service.


# 4. Fonctionnement fondamental de TCP

TCP est conçu pour fournir un flux d'octets fiable et ordonné entre deux points d'extrémité.

## 4.1 Une connexion logique

TCP utilise un état de connexion maintenu par les deux extrémités.

Lors de l'établissement d'une connexion classique, les participants échangent des segments de contrôle.

La séquence la plus connue est appelée three-way handshake :

1. SYN ;
2. SYN-ACK ;
3. ACK.

Le handshake synchronise les paramètres initiaux nécessaires à la connexion. Il ne prouve pas que l'application répondra ensuite correctement.

## 4.2 Les numéros de séquence

TCP numérote les octets dans le flux.

Les numéros de séquence permettent aux extrémités de savoir quelles données ont été envoyées et de replacer les données reçues dans le bon ordre.

Le système ne doit donc pas interpréter chaque segment comme un message applicatif indépendant.

Par exemple, si une application envoie un message de 4000 octets, TCP peut le transporter dans plusieurs segments. Inversement, plusieurs écritures de l'application peuvent être transportées d'une manière qui ne conserve pas les frontières entre ces écritures.

L'application doit définir son propre format de messages si elle a besoin de frontières explicites.

## 4.3 Les accusés de réception

Le récepteur TCP utilise des ACK pour indiquer les données reçues selon les règles du protocole.

Un numéro d'acquittement cumulatif indique habituellement le prochain numéro de séquence attendu.

Si le récepteur a reçu tous les octets jusqu'à un certain point du flux, il peut indiquer qu'il attend la suite à partir d'un numéro précis.

Cela ne signifie pas nécessairement que tous les segments ont reçu un ACK distinct. TCP peut acquitter plusieurs segments avec un seul ACK.

## 4.4 Les retransmissions

Lorsqu'un émetteur ne reçoit pas les informations attendues, TCP peut retransmettre les données non acquittées.

Cette récupération permet de compenser certaines pertes réseau.

Cependant, la retransmission peut augmenter la durée de transfert. Elle ne garantit pas la réussite si le problème persiste ou si la connexion doit finalement être abandonnée.

## 4.5 Le contrôle de flux

Le contrôle de flux aide à adapter la quantité de données en attente aux capacités de réception annoncées par l'autre extrémité.

Il évite qu'un émetteur continue indéfiniment à envoyer des données alors que le récepteur n'est pas prêt à les accepter.

Le contrôle de flux est différent du contrôle de congestion, qui porte sur la capacité et l'état du réseau.


# 5. Schéma SVG animé — Établissement d'une connexion TCP

Ce schéma montre les trois messages principaux de l'établissement classique d'une connexion TCP.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 390" role="img" aria-labelledby="tcp-beg-1-title tcp-beg-1-desc">
<title id="tcp-beg-1-title">Établissement TCP en trois étapes</title>
<desc id="tcp-beg-1-desc">Le client envoie SYN, le serveur répond SYN-ACK et le client renvoie ACK. Les lignes animées représentent séparément les trois messages.</desc>
<rect width="940" height="390" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-weight="700" fill="#0f172a" font-family="Arial,sans-serif">TCP : établir la connexion</text>
<g font-family="Arial,sans-serif">
  <text x="120" y="76" font-size="18" font-weight="700" fill="#1d4ed8">Client</text>
  <text x="740" y="76" font-size="18" font-weight="700" fill="#047857">Serveur</text>
  <path d="M145 90 V330 M765 90 V330" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 7"/>
  <path d="M155 130 H755" stroke="#2563eb" stroke-width="4" stroke-dasharray="12 9">
    <animate attributeName="stroke-dashoffset" values="0;-42" dur="1.4s" repeatCount="indefinite"/>
  </path>
  <path d="M741 119 l14 11 -14 11" fill="none" stroke="#2563eb" stroke-width="3"/>
  <rect x="380" y="108" width="150" height="34" rx="7" fill="#dbeafe" stroke="#2563eb"/>
  <text x="455" y="130" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">1. SYN</text>
  <path d="M755 195 H155" stroke="#059669" stroke-width="4" stroke-dasharray="12 9">
    <animate attributeName="stroke-dashoffset" values="0;42" dur="1.6s" repeatCount="indefinite"/>
  </path>
  <path d="M169 184 l-14 11 14 11" fill="none" stroke="#059669" stroke-width="3"/>
  <rect x="355" y="173" width="200" height="34" rx="7" fill="#dcfce7" stroke="#16a34a"/>
  <text x="455" y="195" text-anchor="middle" font-size="15" font-weight="700" fill="#166534">2. SYN-ACK</text>
  <path d="M155 260 H755" stroke="#7c3aed" stroke-width="4" stroke-dasharray="12 9">
    <animate attributeName="stroke-dashoffset" values="0;-42" dur="1.2s" repeatCount="indefinite"/>
  </path>
  <path d="M741 249 l14 11 -14 11" fill="none" stroke="#7c3aed" stroke-width="3"/>
  <rect x="380" y="238" width="150" height="34" rx="7" fill="#ede9fe" stroke="#7c3aed"/>
  <text x="455" y="260" text-anchor="middle" font-size="15" font-weight="700" fill="#5b21b6">3. ACK</text>
  <rect x="280" y="302" width="350" height="42" rx="9" fill="#f1f5f9" stroke="#64748b"/>
  <text x="455" y="328" text-anchor="middle" font-size="15" font-weight="700" fill="#334155">Connexion établie si les étapes aboutissent</text>
</g>
</svg>

## 5.1 Les trois étapes expliquées

**Étape 1 — SYN**

Le client demande l'établissement d'une connexion TCP. Le segment contient notamment un numéro de séquence initial.

**Étape 2 — SYN-ACK**

Le serveur répond pour accuser réception du SYN du client et annoncer ses propres paramètres initiaux.

**Étape 3 — ACK**

Le client accuse réception de la réponse du serveur.

Une fois l'établissement classique achevé, les extrémités peuvent commencer à échanger des données selon le protocole applicatif.

Il existe des exceptions et extensions au scénario pédagogique, et toutes les communications modernes ne reposent pas sur TCP. QUIC, par exemple, utilise UDP tout en fournissant ses propres mécanismes de connexion et de transport.


# 6. Fiabilité, acquittements et retransmissions

## 6.1 Que se passe-t-il lorsqu'un segment est perdu ?

Supposons qu'un émetteur transmette plusieurs segments TCP et qu'un segment n'arrive pas au destinataire.

Le destinataire ne peut pas confirmer la réception d'octets qu'il n'a pas obtenus.

Selon le contexte, le système peut envoyer des ACK dupliqués ou des informations de sélection des données reçues. L'émetteur peut alors détecter une perte et retransmettre des données.

Si les indices ne suffisent pas, l'expiration du temporisateur de retransmission peut déclencher une nouvelle transmission.

Il faut cependant éviter de croire que toutes les pertes entraînent immédiatement une retransmission identique. Le comportement dépend de la chronologie, des données en vol, des accusés de réception et des mécanismes de récupération utilisés.

## 6.2 Pourquoi la fiabilité a-t-elle un coût ?

La fiabilité implique notamment :

- du suivi d'état ;
- des numéros de séquence ;
- des accusés de réception ;
- des temporisateurs ;
- des retransmissions lorsque nécessaire ;
- le traitement du désordre ;
- des mécanismes de contrôle de flux et de congestion.

Ces mécanismes sont utiles, mais peuvent entraîner des délais supplémentaires lorsque la perte persiste ou que le réseau est instable.

TCP n'est donc pas intrinsèquement « lent », pas plus qu'UDP n'est toujours « rapide ». Les performances dépendent de l'application, du chemin réseau, de la taille des échanges et des mécanismes employés.


# 7. Schéma SVG animé — Perte et retransmission TCP

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 410" role="img" aria-labelledby="tcp-beg-2-title tcp-beg-2-desc">
<title id="tcp-beg-2-title">Récupération d'une perte TCP</title>
<desc id="tcp-beg-2-desc">Deux segments sont transmis, un segment manque dans la séquence observée et le sender retransmet les données nécessaires. Une barre de temporisation pulse au-dessus de la chronologie.</desc>
<rect width="940" height="410" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-weight="700" fill="#0f172a" font-family="Arial,sans-serif">TCP : détection et récupération d'une perte</text>
<g font-family="Arial,sans-serif">
  <text x="80" y="78" font-size="16" font-weight="700" fill="#1d4ed8">Émetteur</text>
  <text x="740" y="78" font-size="16" font-weight="700" fill="#047857">Récepteur</text>
  <path d="M110 90 V330 M770 90 V330" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 7"/>
  <rect x="95" y="105" width="690" height="14" rx="6" fill="#cbd5e1"/>
  <rect x="95" y="105" width="690" height="14" rx="6" fill="#2563eb">
    <animate attributeName="opacity" values="0.3;1;0.3" dur="2.8s" repeatCount="indefinite"/>
  </rect>
  <text x="95" y="96" font-size="12" fill="#334155">Temporisation du segment non acquitté</text>
  <path d="M120 150 H760" stroke="#2563eb" stroke-width="4" stroke-dasharray="12 9">
    <animate attributeName="stroke-dashoffset" values="0;-42" dur="1.4s" repeatCount="indefinite"/>
  </path>
  <path d="M745 139 l15 11 -15 11" fill="none" stroke="#2563eb" stroke-width="3"/>
  <rect x="300" y="134" width="180" height="34" rx="7" fill="#dbeafe" stroke="#2563eb"/>
  <text x="390" y="156" text-anchor="middle" font-size="14" font-weight="700" fill="#1e3a8a">Segment A : reçu</text>
  <path d="M120 200 H760" stroke="#b91c1c" stroke-width="4" stroke-dasharray="12 9" opacity="0.35"/>
  <rect x="300" y="184" width="180" height="34" rx="7" fill="#fee2e2" stroke="#b91c1c"/>
  <text x="390" y="206" text-anchor="middle" font-size="14" font-weight="700" fill="#991b1b">Segment B : perdu</text>
  <path d="M120 252 H760" stroke="#059669" stroke-width="4" stroke-dasharray="12 9">
    <animate attributeName="stroke-dashoffset" values="0;-42" dur="1.6s" repeatCount="indefinite"/>
  </path>
  <path d="M745 241 l15 11 -15 11" fill="none" stroke="#059669" stroke-width="3"/>
  <rect x="300" y="236" width="180" height="34" rx="7" fill="#dcfce7" stroke="#16a34a"/>
  <text x="390" y="258" text-anchor="middle" font-size="14" font-weight="700" fill="#166534">Segment C : reçu</text>
  <path d="M120 302 H760" stroke="#7c3aed" stroke-width="4" stroke-dasharray="12 9">
    <animate attributeName="stroke-dashoffset" values="0;-42" dur="1.2s" repeatCount="indefinite"/>
  </path>
  <path d="M745 291 l15 11 -15 11" fill="none" stroke="#7c3aed" stroke-width="3"/>
  <rect x="270" y="285" width="240" height="34" rx="7" fill="#ede9fe" stroke="#7c3aed"/>
  <text x="390" y="307" text-anchor="middle" font-size="14" font-weight="700" fill="#5b21b6">Retransmission des données</text>
  <text x="80" y="359" font-size="14" fill="#334155">La récupération dépend des ACK, du délai et de l'algorithme de TCP.</text>
  <text x="80" y="382" font-size="13" fill="#64748b">Exemple conceptuel : toutes les pertes n'ont pas la même signature dans une capture.</text>
</g>
</svg>

Le diagramme illustre le mécanisme général. En pratique, l'émetteur ne sait pas toujours immédiatement quel segment a été perdu. Il peut devoir attendre un indice suffisant ou l'expiration d'un temporisateur.


# 8. Fonctionnement fondamental d'UDP

UDP est un protocole de transport simple. Il transporte des datagrammes indépendants sans établir une connexion UDP équivalente à une connexion TCP.

Cela ne signifie pas que les machines n'ont aucune relation : un protocole applicatif peut prévoir une séquence de requêtes et de réponses au-dessus d'UDP.

## 8.1 Les datagrammes UDP

Chaque datagramme possède un en-tête UDP comprenant notamment les ports source et destination, une longueur et un checksum.

UDP ne fournit pas de mécanisme de retransmission automatique des datagrammes perdus.

L'application doit décider si elle a besoin d'un accusé de réception, d'une répétition de requête ou d'un traitement particulier du désordre.

## 8.2 Pourquoi utiliser UDP ?

UDP est utile lorsqu'une application veut :

- un transport avec peu de mécanismes intégrés ;
- des messages dont les frontières sont conservées ;
- contrôler elle-même la fiabilité et la répétition ;
- éviter certaines contraintes du flux d'octets TCP ;
- utiliser un protocole supérieur tel que QUIC.

Ces avantages ne garantissent pas une meilleure performance dans tous les cas.

## 8.3 Exemples d'utilisation

| Application ou service | Usage courant |
|---|---|
| DNS | Requêtes souvent transportées sur UDP ; TCP existe également |
| Voix sur IP | Transport possible de médias temps réel |
| Jeux en réseau | Transport possible d'états et d'événements sensibles au délai |
| NTP | Synchronisation temporelle souvent sur UDP |
| QUIC | Transport moderne au-dessus d'UDP |

Ce tableau donne des exemples, pas des règles universelles. Les protocoles et versions peuvent employer plusieurs transports.

## 8.4 DNS ne signifie pas toujours UDP

Les requêtes DNS classiques sont souvent transportées sur UDP. Toutefois, DNS utilise également TCP dans différents cas, notamment certaines réponses volumineuses et les transferts de zone.

Il faut donc éviter une règle simpliste telle que « DNS = UDP uniquement ».


# 9. Schéma SVG animé — UDP et les datagrammes

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 380" role="img" aria-labelledby="udp-beg-1-title udp-beg-1-desc">
<title id="udp-beg-1-title">UDP transmet des datagrammes indépendants</title>
<desc id="udp-beg-1-desc">Trois datagrammes indépendants sont représentés entre une application émettrice et une application destinataire. Chacun pulse séparément, sans flux de connexion TCP intégré.</desc>
<rect width="940" height="380" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-weight="700" fill="#0f172a" font-family="Arial,sans-serif">UDP : des datagrammes indépendants</text>
<g font-family="Arial,sans-serif">
  <rect x="40" y="110" width="180" height="150" rx="12" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="130" y="145" text-anchor="middle" font-size="18" font-weight="700" fill="#1e3a8a">Émetteur</text>
  <text x="130" y="174" text-anchor="middle" font-size="14" fill="#1e3a8a">Application</text>
  <text x="130" y="201" text-anchor="middle" font-size="13" fill="#1e3a8a">Envoie les messages</text>
  <rect x="720" y="110" width="180" height="150" rx="12" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="810" y="145" text-anchor="middle" font-size="18" font-weight="700" fill="#166534">Récepteur</text>
  <text x="810" y="174" text-anchor="middle" font-size="14" fill="#166534">Application</text>
  <text x="810" y="201" text-anchor="middle" font-size="13" fill="#166534">Traite les messages</text>
  <path d="M220 143 H705" stroke="#0f766e" stroke-width="4" stroke-dasharray="10 9">
    <animate attributeName="stroke-dashoffset" values="0;-38" dur="1.6s" repeatCount="indefinite"/>
  </path>
  <path d="M220 185 H705" stroke="#7c3aed" stroke-width="4" stroke-dasharray="10 9">
    <animate attributeName="stroke-dashoffset" values="0;-38" dur="2.2s" repeatCount="indefinite"/>
  </path>
  <path d="M220 227 H705" stroke="#d97706" stroke-width="4" stroke-dasharray="10 9">
    <animate attributeName="stroke-dashoffset" values="0;-38" dur="1.3s" repeatCount="indefinite"/>
  </path>
  <rect x="350" y="125" width="180" height="35" rx="7" fill="#ccfbf1" stroke="#0f766e"/>
  <text x="440" y="147" text-anchor="middle" font-size="14" font-weight="700" fill="#115e59">Datagramme A</text>
  <rect x="350" y="167" width="180" height="35" rx="7" fill="#ede9fe" stroke="#7c3aed"/>
  <text x="440" y="189" text-anchor="middle" font-size="14" font-weight="700" fill="#5b21b6">Datagramme B</text>
  <rect x="350" y="209" width="180" height="35" rx="7" fill="#fef3c7" stroke="#d97706"/>
  <text x="440" y="231" text-anchor="middle" font-size="14" font-weight="700" fill="#92400e">Datagramme C</text>
  <text x="40" y="300" font-size="14" fill="#334155">UDP n'assure pas lui-même les retransmissions ni l'ordre entre les messages.</text>
  <text x="40" y="325" font-size="14" fill="#334155">L'application peut ajouter ces fonctions si son besoin l'exige.</text>
  <text x="40" y="350" font-size="13" fill="#64748b">Les traits symbolisent le transport, pas la garantie que les trois datagrammes seront livrés.</text>
</g>
</svg>


# 10. TCP contre UDP : comparaison complète

| Caractéristique | TCP | UDP |
|---|---|---|
| Mode de transport | Flux d'octets | Datagrammes |
| Établissement classique | Handshake TCP | Pas de handshake UDP intégré |
| Livraison garantie par le transport | Fiabilité assurée selon les mécanismes TCP | Non |
| Ordre du flux | Flux livré dans l'ordre | Aucun ordre global garanti |
| Retransmissions intégrées | Oui | Non |
| Contrôle de flux | Oui | Non intégré |
| Contrôle de congestion | Oui | Non intégré |
| Ports | Oui | Oui |
| État de connexion au transport | Oui | Pas d'état de connexion UDP équivalent intégré |
| Usage typique | Web sur TCP, SSH, transfert de fichiers | DNS courant sur UDP, NTP, médias temps réel |
| Adaptation par application | Possible | Possible, souvent déterminante |

## 10.1 Quelle solution choisir ?

Le choix du transport ne doit pas être fait en fonction d'une simple idée de vitesse.

TCP convient lorsque l'application a besoin d'un flux fiable et ordonné, fourni directement par le transport.

UDP convient lorsque le protocole applicatif est conçu autour de datagrammes et souhaite définir ses propres mécanismes ou contraintes.

QUIC illustre un troisième cas important : il fonctionne au-dessus d'UDP mais fournit des mécanismes de transport fiables, ordonnés par flux et sécurisés.

La vraie distinction est donc entre les fonctions intégrées au transport et celles qui sont prises en charge par un protocole supérieur.


# 11. Client, serveur, socket et connexion

## 11.1 Le serveur

Un serveur démarre un programme qui attend des communications sur une adresse et un port déterminés, selon sa configuration.

Pour TCP, on parle couramment d'un socket en écoute, ou *listening socket*.

Pour UDP, l'application peut lier un socket à un port afin que le système lui remette les datagrammes correspondants.

Le fait que l'application démarre correctement ne garantit pas que le port est joignable à distance. Le pare-feu, le routage et les paramètres d'écoute peuvent empêcher une connexion externe.

## 11.2 Le client

Le client initie généralement l'échange en contactant le serveur.

Le système peut sélectionner automatiquement un port source éphémère pour distinguer la communication.

Plusieurs connexions peuvent être présentes simultanément sur un même ordinateur, y compris vers le même serveur, car les tuples source/destination et les états de connexion permettent de les différencier.

## 11.3 Qu'est-ce qu'un socket ?

Le terme socket peut désigner une interface de programmation ou un point d'extrémité de communication, selon le contexte.

Un socket TCP inclut des informations nécessaires à la communication et à son état.

Un socket UDP sert notamment à envoyer ou recevoir des datagrammes. Il n'implique pas que le transport fournit les mécanismes de fiabilité de TCP.

Dans un cours de réseau, gardez cette distinction : **un port est un numéro du protocole de transport, tandis qu'un socket est un concept plus large lié au point d'extrémité et à l'interface de communication.**


# 12. Pare-feu, NAT et filtrage des ports

Un pare-feu peut autoriser ou bloquer le trafic en fonction de règles définies.

Selon l'équipement, les règles peuvent prendre en compte :

- les adresses IP ;
- le protocole de transport ;
- les ports source ou destination ;
- l'état d'une connexion ;
- l'interface d'entrée ou de sortie ;
- des informations applicatives supplémentaires.

Une règle qui autorise TCP/443 n'autorise pas automatiquement UDP/443. Le protocole doit être considéré explicitement.

## 12.1 Pare-feu à état

Un pare-feu à état suit les connexions reconnues selon ses mécanismes.

Il peut autoriser le trafic retour associé à une connexion initiée dans le sens autorisé, sous réserve des règles de sécurité.

Le comportement dépend de la configuration et des capacités du produit.

## 12.2 NAT

Le NAT traduit certaines informations d'adressage.

Un NAT avec surcharge peut utiliser une adresse publique et différentes valeurs de ports traduits afin de permettre à plusieurs flux internes de partager une adresse externe.

Le NAT ne remplace pas nécessairement le filtrage de sécurité. Les politiques d'accès et les traductions sont deux éléments qu'il faut analyser séparément.

## 12.3 Pourquoi un port ouvert localement peut rester inaccessible

Un service peut écouter sur un port sans être accessible depuis un réseau distant.

Causes possibles :

- le service écoute seulement sur l'interface locale ;
- l'adresse IP de destination n'est pas celle attendue ;
- une route manque ;
- un pare-feu bloque le trafic ;
- une règle NAT est absente ;
- le service n'écoute pas sur le protocole de transport attendu ;
- une politique de sécurité de l'hôte bloque l'accès.

Le test local et le test distant ne répondent donc pas à la même question.


# 13. Schéma SVG animé — Ports et distribution vers les applications

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 410" role="img" aria-labelledby="port-beg-1-title port-beg-1-desc">
<title id="port-beg-1-title">Distribution des données vers les ports applicatifs</title>
<desc id="port-beg-1-desc">Le système reçoit des segments de transport et les distribue vers différents points d'extrémité selon le protocole et le port. Chaque route s'illumine indépendamment.</desc>
<rect width="940" height="410" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-weight="700" fill="#0f172a" font-family="Arial,sans-serif">Un hôte peut fournir plusieurs services</text>
<g font-family="Arial,sans-serif">
  <rect x="35" y="132" width="205" height="135" rx="12" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="137" y="165" text-anchor="middle" font-size="18" font-weight="700" fill="#1e3a8a">Pile de transport</text>
  <text x="137" y="192" text-anchor="middle" font-size="14" fill="#1e3a8a">TCP / UDP</text>
  <text x="137" y="216" text-anchor="middle" font-size="13" fill="#1e3a8a">Lecture du port</text>
  <text x="137" y="239" text-anchor="middle" font-size="13" fill="#1e3a8a">de destination</text>
  <rect x="645" y="65" width="250" height="67" rx="10" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="770" y="92" text-anchor="middle" font-size="16" font-weight="700" fill="#166534">Service HTTPS</text>
  <text x="770" y="114" text-anchor="middle" font-size="14" fill="#166534">TCP/443 ou transport adapté</text>
  <rect x="645" y="170" width="250" height="67" rx="10" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <text x="770" y="197" text-anchor="middle" font-size="16" font-weight="700" fill="#5b21b6">Service DNS</text>
  <text x="770" y="219" text-anchor="middle" font-size="14" fill="#5b21b6">UDP/53 ou TCP/53</text>
  <rect x="645" y="275" width="250" height="67" rx="10" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="770" y="302" text-anchor="middle" font-size="16" font-weight="700" fill="#92400e">Service SSH</text>
  <text x="770" y="324" text-anchor="middle" font-size="14" fill="#92400e">TCP/22, par convention</text>
  <path d="M240 199 H420 V98 H630" fill="none" stroke="#16a34a" stroke-width="4" stroke-dasharray="10 8">
    <animate attributeName="stroke-dashoffset" values="0;-36" dur="1.5s" repeatCount="indefinite"/>
  </path>
  <path d="M240 199 H420 V203 H630" fill="none" stroke="#7c3aed" stroke-width="4" stroke-dasharray="10 8">
    <animate attributeName="stroke-dashoffset" values="0;-36" dur="2s" repeatCount="indefinite"/>
  </path>
  <path d="M240 199 H420 V308 H630" fill="none" stroke="#d97706" stroke-width="4" stroke-dasharray="10 8">
    <animate attributeName="stroke-dashoffset" values="0;-36" dur="1.2s" repeatCount="indefinite"/>
  </path>
  <text x="35" y="315" font-size="14" fill="#334155">Les numéros de port ne garantissent pas</text>
  <text x="35" y="336" font-size="14" fill="#334155">qu'un service est actif ou joignable.</text>
  <text x="35" y="367" font-size="13" fill="#64748b">Le protocole et le port doivent être interprétés ensemble.</text>
</g>
</svg>


# 14. Premiers tests en ligne de commande

Effectuez les tests uniquement sur des systèmes que vous êtes autorisé à administrer ou à examiner.

## 14.1 Sous Windows

Afficher les connexions et ports :

```powershell
netstat -ano
```

Lister des connexions TCP :

```powershell
Get-NetTCPConnection
```

Tester une connexion TCP vers un port :

```powershell
Test-NetConnection exemple.com -Port 443
```

Cette dernière commande teste une connexion TCP vers le port indiqué. Elle ne valide pas à elle seule la résolution complète de l'application, TLS et HTTP.

## 14.2 Sous Linux

Lister les sockets TCP en écoute :

```bash
ss -lnt
```

Lister les sockets UDP :

```bash
ss -lnu
```

Afficher les connexions TCP :

```bash
ss -tan
```

Afficher les processus quand les permissions et les outils le permettent :

```bash
sudo ss -lntup
```

Les options disponibles dépendent de la version des outils et des privilèges de l'utilisateur.

## 14.3 Test de connexion TCP

Un outil comme Netcat peut effectuer un test TCP dans un environnement autorisé :

```bash
nc -vz exemple.com 443
```

Selon l'implémentation de Netcat, la syntaxe et le résultat exacts peuvent différer.

Un succès indique généralement que la connexion TCP a pu être établie vers la destination indiquée dans ces conditions. Il ne prouve pas que le protocole applicatif fonctionne correctement.

## 14.4 Tester UDP

UDP ne comporte pas d'établissement de connexion intégré équivalent à TCP.

Un outil peut donc envoyer un datagramme sans recevoir de réponse, et l'absence de réponse ne prouve pas nécessairement que le port UDP est fermé.

Pour diagnostiquer UDP, il faut connaître le protocole applicatif et savoir quelle réponse est normalement attendue.


# 15. Exercices

## Exercice 1 — Rôle des ports

Expliquez pourquoi une adresse IP ne suffit pas pour distribuer des données à plusieurs applications qui fonctionnent simultanément.

## Exercice 2 — TCP

Décrivez les trois étapes de l'établissement classique d'une connexion TCP.

## Exercice 3 — UDP

UDP garantit-il la livraison et l'ordre des datagrammes ?

## Exercice 4 — Port source

Lorsqu'un client contacte un service TCP/443, quel rôle joue généralement son port source ?

## Exercice 5 — Ports et protocoles

Expliquez la différence entre TCP/53 et UDP/53.

## Exercice 6 — Diagnostic

Un serveur écoute localement sur TCP/443, mais un client distant n'arrive pas à se connecter. Citez au moins quatre pistes.

## Exercice 7 — Ping et ports

Un ping réussit, mais la connexion TCP au port 443 échoue. Qu'est-ce que ce résultat permet de conclure ? Que ne permet-il pas de conclure ?

## Exercice 8 — Fiabilité

Pourquoi TCP peut-il continuer à échouer malgré ses mécanismes de retransmission ?

## Exercice 9 — UDP applicatif

Une application basée sur UDP a besoin d'une livraison fiable des messages. Comment peut-elle répondre à ce besoin ?

## Exercice 10 — Interprétation

Pourquoi ne faut-il pas conclure qu'un service HTTPS fonctionne uniquement parce qu'un test TCP vers le port 443 réussit ?


# 16. Corrigés commentés

**Exercice 1**

L'adresse IP indique la destination au niveau IP. Les ports permettent au protocole de transport de remettre les données au point d'extrémité approprié sur cette destination.

**Exercice 2**

Le client envoie SYN, le serveur renvoie SYN-ACK, puis le client envoie ACK. Cette séquence constitue le handshake TCP classique.

**Exercice 3**

Non. UDP ne garantit pas, à lui seul, la livraison ni l'ordre des datagrammes. Les applications peuvent ajouter leurs propres mécanismes de fiabilité.

**Exercice 4**

Le port source permet généralement d'identifier le point d'extrémité du client pour cette communication. Il est souvent choisi temporairement par le système.

**Exercice 5**

TCP/53 est l'utilisation de TCP sur le port 53. UDP/53 est l'utilisation d'UDP sur ce numéro. Les règles de filtrage sont distinctes pour chaque protocole.

**Exercice 6**

Pistes possibles : filtrage local, pare-feu intermédiaire, route incorrecte, service lié uniquement à l'adresse de boucle locale, mauvaise adresse de destination, règle NAT absente, protocole incorrect ou réseau distant inaccessible.

**Exercice 7**

Le ping montre qu'un échange ICMP a fonctionné dans les conditions du test. L'échec TCP peut venir du service, du filtrage, du routage ou d'un problème de port. Le ping ne prouve pas que TCP/443 est accessible.

**Exercice 8**

Les pertes peuvent persister, le serveur peut devenir inaccessible, les temporisateurs peuvent expirer ou les mécanismes de transport peuvent finalement abandonner la connexion. La fiabilité de TCP ne peut pas garantir le succès en toutes circonstances.

**Exercice 9**

Le protocole applicatif peut utiliser des identifiants de message, accusés de réception, temporisateurs, retransmissions, numéros de séquence ou mécanismes de déduplication. Ces fonctions doivent être conçues correctement pour répondre au besoin de l'application.

**Exercice 10**

Un test TCP ne valide pas nécessairement TLS, le certificat, le protocole HTTP, l'authentification ou l'état applicatif du serveur. Il ne teste qu'une partie de la chaîne de communication.


# 17. Glossaire

**ACK :** indicateur TCP associé à l'acquittement.

**Datagramme :** unité de données autonome utilisée notamment par UDP.

**Flux d'octets :** abstraction fournie par TCP, sans préservation automatique des frontières entre les messages de l'application.

**Handshake :** séquence de messages servant notamment à initialiser une connexion TCP.

**NAT :** mécanisme de traduction d'informations d'adressage.

**Port :** numéro utilisé par un protocole de transport pour distinguer les points d'extrémité.

**Retransmission :** réémission de données lorsque les mécanismes du transport indiquent qu'elles doivent être envoyées à nouveau.

**SYN :** indicateur TCP couramment utilisé au début de l'établissement d'une connexion.

**Socket :** point d'extrémité ou interface de programmation permettant une communication réseau, selon le contexte.

**TCP :** protocole de transport fournissant un flux fiable et ordonné.

**UDP :** protocole de transport par datagrammes, sans garantie intégrée de livraison.

**QUIC :** protocole de transport moderne s'appuyant sur UDP et fournissant notamment des mécanismes de fiabilité, de sécurité et de contrôle de flux.


# 18. Fiche de révision

- TCP fournit un flux d'octets fiable et ordonné.
- UDP transporte des datagrammes sans garantie de livraison intégrée.
- Les deux protocoles utilisent des ports.
- Une adresse IP et un port répondent à des rôles différents.
- Le port source identifie généralement l'extrémité cliente du flux.
- Le port destination identifie généralement le service visé.
- Un port en écoute ne garantit pas l'accès distant.
- TCP utilise des numéros de séquence, des ACK et des retransmissions.
- TCP inclut des mécanismes de contrôle de flux et de congestion.
- Un test TCP réussi ne prouve pas que le service applicatif fonctionne.
- Un test UDP sans réponse ne prouve pas à lui seul que le port est fermé.
- QUIC est un exemple de protocole moderne utilisant UDP sans se limiter aux garanties natives d'UDP.

## Ressources de référence

- [Spécification TCP — RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html)
- [Spécification UDP — RFC 768](https://www.rfc-editor.org/rfc/rfc768.html)
- [Registre officiel des ports — IANA](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml)
- [Spécification QUIC — RFC 9000](https://www.rfc-editor.org/rfc/rfc9000.html)


## Conclusion

TCP, UDP et les ports sont essentiels à la compréhension des réseaux IP.

TCP fournit une base solide pour les applications qui ont besoin d'un flux fiable et ordonné. UDP permet de transporter des datagrammes avec moins de mécanismes intégrés, mais laisse davantage de responsabilités au protocole applicatif lorsque des garanties supplémentaires sont requises.

Pour progresser, apprenez à distinguer le transport, l'adressage, le port de destination et le service réellement accessible. Les tests et les captures doivent servir à répondre à des questions précises, plutôt qu'à simplement accumuler des commandes.