# TCP, UDP & Ports — Analyse et dépannage intermédiaire

> **Niveau :** Intermédiaire  
> **Prérequis :** comprendre l'adressage IP, les ports, le handshake TCP et les différences de base entre TCP et UDP.  
> **Objectif :** analyser les flux, interpréter les numéros de séquence, comprendre les états TCP, vérifier les ports et diagnostiquer des problèmes de transport à partir de preuves.


## Sommaire

1. Rappel du fonctionnement TCP/UDP
2. Identifier une communication par son tuple
3. Les états d'une connexion TCP
4. Numéros de séquence et acquittements
5. Fenêtre de réception et contrôle de flux
6. Retransmissions et temporisateurs
7. Contrôle de congestion
8. Fin et réinitialisation des connexions
9. Fonctionnement et diagnostic d'UDP
10. Ports connus, enregistrés et éphémères
11. Écoute locale, pare-feu et NAT
12. QUIC et HTTP/3
13. Captures Wireshark
14. Schémas SVG animés
15. Laboratoires
16. Exercices corrigés
17. Glossaire et ressources


# 1. Rappel du fonctionnement TCP/UDP

TCP et UDP se situent au niveau Transport dans le modèle OSI traditionnel.

Ils utilisent les services IP afin de transmettre leurs données entre les hôtes, mais ils ne prennent pas les mêmes décisions.

## 1.1 TCP

TCP fournit un flux d'octets fiable et ordonné. Les mécanismes importants comprennent :

- la création et la gestion d'un état de connexion ;
- les numéros de séquence ;
- les ACK ;
- la retransmission des données non acquittées ;
- le contrôle de flux ;
- le contrôle de congestion ;
- les procédures de fermeture de connexion.

TCP ne garantit cependant pas que l'application effectuera correctement son travail. La réussite du transport et la réussite de l'application sont deux événements différents.

## 1.2 UDP

UDP permet d'envoyer et de recevoir des datagrammes sans implémenter directement les mécanismes de transport fiables de TCP.

Chaque datagramme est traité comme une unité distincte par UDP. Les applications doivent prendre en charge les mécanismes supplémentaires dont elles ont besoin.

Cela ne signifie pas que UDP est réservé aux petites quantités de données, mais les applications doivent tenir compte de la MTU du chemin et des conséquences possibles de la fragmentation, des pertes et du désordre.

## 1.3 Une différence importante : TCP n'est pas un protocole de messages

Une application peut écrire trois messages dans un socket TCP. Le destinataire ne reçoit pas nécessairement trois blocs correspondant exactement aux trois appels d'écriture.

TCP fournit un flux d'octets. Les frontières des messages doivent être définies par le protocole applicatif, par exemple avec une longueur, un délimiteur ou une structure de taille connue.

UDP conserve les frontières des datagrammes au niveau de son service de transport, mais ne garantit ni leur livraison ni leur ordre.


# 2. Identifier une communication par son tuple

Un port ne suffit pas, à lui seul, pour identifier une communication complète.

Pour décrire un flux TCP ou UDP, on examine généralement :

- le protocole de transport ;
- l'adresse IP source ;
- le port source ;
- l'adresse IP destination ;
- le port destination.

L'ensemble de ces informations permet de différencier des flux qui partagent parfois la même adresse IP ou le même port de destination.

## 2.1 Exemple

Imaginons un client qui ouvre deux connexions vers un serveur Web :

```text
Flux A :
TCP 192.0.2.10:51001 → 198.51.100.80:443

Flux B :
TCP 192.0.2.10:51002 → 198.51.100.80:443
```

Ces adresses sont réservées aux exemples documentaires.

Les deux connexions visent le même serveur et le même port, mais possèdent des ports sources différents. Cela permet de les distinguer.

Le système d'exploitation gère aussi l'état des connexions et les contraintes d'association des sockets. Le tuple reste un outil fondamental pour interpréter les captures, les journaux et les tables de connexion.

## 2.2 Inversion des rôles dans le sens retour

Pour un segment envoyé par le serveur dans le flux A, les adresses et ports apparaissent dans le sens opposé :

```text
TCP 198.51.100.80:443 → 192.0.2.10:51001
```

L'adresse IP et le port source du segment de retour correspondent au point d'extrémité serveur observé dans ce contexte. La destination correspond au client.

En présence de NAT ou de proxy, les tuples visibles peuvent différer entre plusieurs points du réseau.

## 2.3 Un port TCP n'est pas un port UDP

Le tuple doit être associé au protocole.

```text
TCP 192.0.2.10:51001 → 198.51.100.80:53
UDP 192.0.2.10:51001 → 198.51.100.80:53
```

Ces deux lignes représentent des transports différents, même si les adresses et les numéros de port sont identiques.

Dans une règle de filtrage, dans un journal ou dans une capture, le protocole de transport est donc indispensable.


# 3. Les états d'une connexion TCP

TCP utilise des états pour décrire la progression d'une connexion.

Les noms d'états les plus courants comprennent :

| État | Signification générale |
|---|---|
| `LISTEN` | Un socket attend de nouvelles connexions |
| `SYN-SENT` | Une ouverture active a été initiée |
| `SYN-RECEIVED` | Un SYN a été reçu et la réponse correspondante est en attente ou a été envoyée |
| `ESTABLISHED` | La connexion est établie |
| `FIN-WAIT-1` | L'extrémité a commencé sa fermeture normale |
| `FIN-WAIT-2` | L'extrémité attend la fermeture de l'autre direction |
| `CLOSE-WAIT` | Un FIN distant a été reçu ; l'application locale doit terminer sa fermeture |
| `LAST-ACK` | L'extrémité attend l'acquittement final d'un FIN |
| `TIME-WAIT` | L'extrémité conserve temporairement l'état requis après certaines fermetures |
| `CLOSED` | Aucun état de connexion active correspondant n'est conservé |

Les états représentent des situations précises de la machine à états TCP. Ils ne sont pas des indicateurs universels de la santé d'une application.

## 3.1 Pourquoi un état `LISTEN` n'est-il pas suffisant ?

Un service peut écouter sur le bon port et rester inaccessible à un client distant.

L'écoute indique que le système a un socket prêt à accepter des connexions sur l'adresse et le port correspondants. Elle ne valide pas :

- le routage entre client et serveur ;
- les règles de filtrage ;
- l'adresse IP réellement visée par le client ;
- l'accès depuis tous les réseaux ;
- le traitement de la requête applicative.

Un service lié à l'adresse de boucle locale uniquement peut être accessible depuis le même hôte, mais pas depuis une autre machine.

## 3.2 `CLOSE-WAIT` et fuite de connexions

Lorsque le système reçoit un FIN du correspondant, il entre normalement dans un état où l'application locale doit achever la fermeture de sa propre direction du flux.

Des sockets qui restent longtemps en `CLOSE-WAIT` peuvent justifier une investigation de l'application : elle peut ne pas fermer les sockets après avoir reçu la fermeture distante.

Il faut néanmoins vérifier le contexte, la durée, le comportement attendu du logiciel et les autres éléments de l'incident avant de conclure à une fuite de connexions.

## 3.3 `TIME-WAIT`

`TIME-WAIT` n'indique pas automatiquement une erreur. Cet état participe au bon fonctionnement de TCP après certaines fermetures, notamment pour gérer les segments retardés et certaines réutilisations du même tuple.

Un nombre élevé de sockets dans cet état doit être interprété en fonction du profil du trafic, du rythme d'ouverture des connexions et de l'architecture.

Ne cherchez pas à supprimer systématiquement `TIME-WAIT` sans comprendre le problème que vous tentez de résoudre.


# 4. Schéma SVG animé — Cycle d'une connexion TCP

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 440" role="img" aria-labelledby="state-int-title state-int-desc">
<title id="state-int-title">Cycle simplifié d'une connexion TCP</title>
<desc id="state-int-desc">La connexion passe de l'ouverture à l'état établi, puis à la fermeture. Les contours des phases s'animent séparément pour montrer les transitions.</desc>
<rect width="960" height="440" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-family="Arial,sans-serif" font-weight="700" fill="#0f172a">Cycle logique d'une connexion TCP</text>
<g font-family="Arial,sans-serif">
  <rect x="45" y="90" width="235" height="85" rx="12" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="162" y="123" text-anchor="middle" font-size="18" font-weight="700" fill="#1e3a8a">Établissement</text>
  <text x="162" y="147" text-anchor="middle" font-size="14" fill="#1e3a8a">SYN / SYN-ACK / ACK</text>
  <rect x="362" y="90" width="235" height="85" rx="12" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="479" y="123" text-anchor="middle" font-size="18" font-weight="700" fill="#166534">ESTABLISHED</text>
  <text x="479" y="147" text-anchor="middle" font-size="14" fill="#166534">Données et ACK</text>
  <rect x="679" y="90" width="235" height="85" rx="12" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="796" y="123" text-anchor="middle" font-size="18" font-weight="700" fill="#92400e">Fermeture</text>
  <text x="796" y="147" text-anchor="middle" font-size="14" fill="#92400e">FIN et ACK</text>
  <rect x="39" y="84" width="247" height="97" rx="16" fill="none" stroke="#2563eb" stroke-width="4">
    <animate attributeName="stroke-opacity" values="0.25;1;0.25" dur="3.2s" repeatCount="indefinite"/>
  </rect>
  <rect x="356" y="84" width="247" height="97" rx="16" fill="none" stroke="#16a34a" stroke-width="4">
    <animate attributeName="stroke-opacity" values="0.25;1;0.25" dur="3.7s" repeatCount="indefinite"/>
  </rect>
  <rect x="673" y="84" width="247" height="97" rx="16" fill="none" stroke="#d97706" stroke-width="4">
    <animate attributeName="stroke-opacity" values="0.25;1;0.25" dur="4.2s" repeatCount="indefinite"/>
  </rect>
  <path d="M280 133 H354 M597 133 H671" stroke="#475569" stroke-width="3"/>
  <path d="M342 123 l12 10 -12 10 M659 123 l12 10 -12 10" fill="none" stroke="#475569" stroke-width="3"/>
  <rect x="45" y="245" width="870" height="125" rx="12" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="70" y="279" font-size="16" font-weight="700" fill="#334155">États à connaître pendant l'analyse</text>
  <text x="70" y="309" font-size="14" fill="#334155">LISTEN · SYN-SENT · SYN-RECEIVED · ESTABLISHED</text>
  <text x="70" y="336" font-size="14" fill="#334155">FIN-WAIT-1 · FIN-WAIT-2 · CLOSE-WAIT · LAST-ACK · TIME-WAIT</text>
  <text x="45" y="402" font-size="13" fill="#64748b">Diagramme pédagogique : les transitions exactes dépendent de l'événement et de l'état local.</text>
</g>
</svg>

Ce dessin n'est pas une machine à états complète. Pour une analyse experte, les transitions détaillées doivent être étudiées dans la spécification TCP et dans le contexte des segments réellement observés.


# 5. Numéros de séquence et acquittements

## 5.1 TCP numérote les octets

TCP utilise des numéros de séquence pour représenter la position des octets dans le flux.

L'exemple suivant est volontairement simplifié :

- Le segment A transporte 100 octets à partir du numéro de séquence 1000.
- Le segment B transporte les 100 octets suivants.
- Si le destinataire a reçu A et B, l'acquittement cumulatif peut indiquer 1200 comme prochain octet attendu.

Les valeurs illustrées ne représentent pas une capture réelle.

Un segment qui transporte des données avance la séquence selon le nombre d'octets transmis. SYN et FIN consomment également un espace de séquence, même lorsqu'ils ne transportent pas de données applicatives.

## 5.2 ACK cumulatif

Un ACK cumulatif indique la prochaine position attendue dans le flux.

Si un récepteur attend l'octet numéro 1200, il n'a pas nécessairement reçu tous les octets qui suivent.

Les données reçues au-delà d'un trou peuvent être mises en mémoire tampon selon le comportement du récepteur, mais l'ACK cumulatif ne permet pas à lui seul de représenter toutes les données reçues hors ordre.

## 5.3 Acquittement sélectif (SACK)

La fonctionnalité Selective Acknowledgment permet au récepteur d'indiquer des blocs de données reçus au-delà de la partie du flux reconnue par l'ACK cumulatif.

L'émetteur peut ainsi mieux identifier les données déjà reçues et celles qui manquent.

SACK ne supprime pas les pertes et ne signifie pas que chaque connexion utilise nécessairement les mêmes options de récupération. Il s'agit d'une information supplémentaire de récupération de perte.

## 5.4 Schéma SVG animé — Trou dans une séquence

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 400" role="img" aria-labelledby="seq-int-title seq-int-desc">
<title id="seq-int-title">Séquence TCP avec un segment manquant</title>
<desc id="seq-int-desc">Des blocs représentent plusieurs plages d'octets TCP. Un bloc manquant est mis en évidence par une animation d'opacité tandis que les blocs reçus restent visibles.</desc>
<rect width="950" height="400" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-family="Arial,sans-serif" font-size="23" font-weight="700" fill="#0f172a">Séquences : ce qui est reçu et ce qui manque</text>
<g font-family="Arial,sans-serif">
  <text x="50" y="83" font-size="15" font-weight="700" fill="#334155">Plages d'octets illustratives</text>
  <rect x="50" y="106" width="180" height="58" rx="8" fill="#bbf7d0" stroke="#15803d" stroke-width="2"/>
  <text x="140" y="130" text-anchor="middle" font-size="14" font-weight="700" fill="#14532d">1000–1099</text>
  <text x="140" y="150" text-anchor="middle" font-size="13" fill="#14532d">Reçu</text>
  <rect x="250" y="106" width="180" height="58" rx="8" fill="#fecaca" stroke="#b91c1c" stroke-width="2">
    <animate attributeName="fill-opacity" values="0.4;1;0.4" dur="2.6s" repeatCount="indefinite"/>
  </rect>
  <text x="340" y="130" text-anchor="middle" font-size="14" font-weight="700" fill="#991b1b">1100–1199</text>
  <text x="340" y="150" text-anchor="middle" font-size="13" fill="#991b1b">Manquant</text>
  <rect x="450" y="106" width="180" height="58" rx="8" fill="#bbf7d0" stroke="#15803d" stroke-width="2"/>
  <text x="540" y="130" text-anchor="middle" font-size="14" font-weight="700" fill="#14532d">1200–1299</text>
  <text x="540" y="150" text-anchor="middle" font-size="13" fill="#14532d">Reçu hors ordre</text>
  <rect x="650" y="106" width="180" height="58" rx="8" fill="#bbf7d0" stroke="#15803d" stroke-width="2"/>
  <text x="740" y="130" text-anchor="middle" font-size="14" font-weight="700" fill="#14532d">1300–1399</text>
  <text x="740" y="150" text-anchor="middle" font-size="13" fill="#14532d">Reçu hors ordre</text>
  <path d="M50 196 H630" stroke="#475569" stroke-width="3"/>
  <path d="M618 186 l12 10 -12 10" fill="none" stroke="#475569" stroke-width="3"/>
  <text x="50" y="222" font-size="14" fill="#334155">Un ACK cumulatif peut toujours annoncer 1100 comme prochain octet attendu.</text>
  <rect x="50" y="255" width="780" height="70" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="75" y="283" font-size="16" font-weight="700" fill="#1e3a8a">Récupération</text>
  <text x="75" y="307" font-size="14" fill="#1e3a8a">Les informations de réception hors ordre peuvent aider à identifier le trou dans le flux.</text>
  <text x="50" y="359" font-size="13" fill="#64748b">Les plages sont des exemples : un SACK réel dépend des numéros de séquence, des options et des données reçues.</text>
</g>
</svg>


# 6. Fenêtre de réception et contrôle de flux

## 6.1 La fenêtre annoncée

Un récepteur TCP annonce une fenêtre qui indique à l'émetteur combien d'octets il est actuellement prêt à recevoir au-delà du point d'acquittement cumulatif, sous réserve des options et du calcul réel du protocole.

Cette fenêtre est souvent appelée *receive window* ou `rwnd`.

Si la mémoire de réception se remplit, la fenêtre peut diminuer.

Dans certaines situations, le récepteur annonce une fenêtre nulle. L'émetteur doit alors adapter son comportement jusqu'à ce que la fenêtre permette à nouveau la transmission, selon les règles TCP applicables.

## 6.2 Fenêtre nulle

Une fenêtre nulle n'indique pas nécessairement que le réseau est défaillant.

Elle peut indiquer que le récepteur ne dispose temporairement pas de capacité suffisante pour accepter davantage de données.

Il faut examiner :

- la fenêtre annoncée ;
- les annonces ultérieures ;
- la consommation des données par l'application ;
- l'état du système ;
- le rythme d'arrivée des données ;
- l'éventuelle présence de sondes de fenêtre.

Une application qui lit trop lentement les données peut contribuer au phénomène.

## 6.3 Échelle de fenêtre

L'option Window Scale permet de représenter des fenêtres de réception plus grandes que celles qu'un champ TCP non étendu peut exprimer directement.

Cette option se négocie pendant l'établissement de la connexion. Elle est importante dans certaines connexions à haut débit ou à forte latence.

Ne confondez pas la fenêtre annoncée par le récepteur avec la fenêtre de congestion de l'émetteur : les deux jouent des rôles différents.


# 7. Retransmissions et temporisateurs

## 7.1 Retransmission après expiration du RTO

TCP utilise un temporisateur de retransmission, désigné par **RTO** (*Retransmission Timeout*).

Lorsque les données restent non acquittées et que le temporisateur expire, l'émetteur peut retransmettre les données nécessaires et adapter le temporisateur suivant les règles TCP.

Le RTO n'est pas un chiffre fixe universel.

Son calcul tient compte des mesures du temps aller-retour et de leur variabilité. Les règles d'estimation et les limites applicables sont précisées par les documents techniques du protocole.

## 7.2 Retransmission rapide

Des ACK dupliqués ou certaines informations SACK peuvent permettre à l'émetteur de détecter une perte avant l'expiration du RTO.

La récupération dépend de l'algorithme employé, du nombre de données en vol et des informations reçues.

Une retransmission rapide ne signifie pas que tous les paquets suivants avaient été perdus. Au contraire, les accusés de réception peuvent montrer que certaines données sont arrivées malgré un trou dans la séquence.

## 7.3 Pourquoi Wireshark indique-t-il une retransmission ?

Wireshark utilise des règles d'analyse pour annoter les retransmissions possibles.

Cette annotation est utile, mais elle ne fournit pas automatiquement la cause de la perte.

La capture peut être incomplète ou prise sur l'hôte avant un traitement matériel. Un segment peut avoir été retransmis pour une cause située ailleurs sur le chemin.

Pour interpréter la cause, vérifiez :

- les numéros de séquence ;
- l'historique des ACK ;
- les intervalles temporels ;
- l'emplacement de la capture ;
- les autres flux et mesures réseau disponibles.


# 8. Contrôle de congestion

Le contrôle de congestion est différent du contrôle de flux.

Le contrôle de flux protège la capacité de réception annoncée par l'extrémité distante. Le contrôle de congestion limite la quantité de données injectée dans le réseau en fonction des mécanismes de contrôle du transport.

## 8.1 Fenêtre de congestion

La fenêtre de congestion, couramment notée `cwnd`, participe à déterminer la quantité de données qu'un émetteur peut garder en vol.

Elle évolue au fil des accusés de réception et selon les règles de l'algorithme de congestion.

Une perte peut entraîner une réduction de la quantité de données en vol autorisée par l'algorithme. Les détails dépendent de la méthode de congestion utilisée.

## 8.2 Pourquoi le contrôle de congestion est-il important ?

Sans contrôle de congestion approprié, un émetteur pourrait continuer à injecter des données à un rythme supérieur à la capacité disponible du réseau.

Cela augmenterait les files d'attente et pourrait aggraver les pertes et les retards.

Le contrôle de congestion vise à utiliser la capacité disponible tout en s'adaptant aux signes de congestion.

## 8.3 Un grand RTT n'est pas automatiquement une panne

Le RTT (*Round-Trip Time*) correspond au temps nécessaire pour qu'un signal de communication aille vers l'autre extrémité et revienne, selon le point de mesure.

Un RTT élevé peut être lié à la distance, à la propagation, aux files d'attente, à la charge ou à une route particulière.

Un RTT élevé n'établit pas automatiquement que le contrôle de congestion est incorrect. Il faut séparer le délai de propagation du délai d'attente et étudier le chemin.


# 9. Fin et réinitialisation d'une connexion TCP

## 9.1 FIN et fermeture normale

TCP permet de fermer indépendamment les deux directions du flux.

Un FIN indique que l'extrémité n'enverra plus de données dans cette direction. L'autre direction peut continuer à transmettre les données restantes jusqu'à sa propre fermeture.

Une fermeture classique utilise souvent plusieurs segments, car les deux directions doivent être fermées et acquittées.

## 9.2 RST

RST est utilisé pour réinitialiser une connexion dans les circonstances définies par TCP.

Un RST peut apparaître lorsqu'un port ne correspond à aucun socket qui accepte cette connexion ou lorsqu'une connexion est interrompue brutalement.

Toutefois, il peut aussi être produit par un équipement intermédiaire. Il faut donc examiner la source du paquet, les captures et la configuration du chemin.

## 9.3 Différencier FIN et RST

| Indicateur | Interprétation générale |
|---|---|
| FIN | Fermeture ordonnée d'une direction du flux |
| RST | Réinitialisation ou rejet de la connexion dans le contexte observé |

Un FIN n'indique pas nécessairement une erreur. Un RST n'indique pas nécessairement un problème matériel.

Pour déterminer ce qui s'est passé, corrélez les flags TCP, les états et le contexte applicatif.


# 10. Fonctionnement et diagnostic d'UDP

## 10.1 UDP conserve les frontières des datagrammes

UDP transporte des datagrammes. Chaque réception correspond à une unité distincte de transport, contrairement au flux d'octets fourni par TCP.

Cela facilite certains protocoles fondés sur des requêtes, des événements ou des messages autonomes.

Cependant, UDP ne fournit pas la fiabilité de TCP. L'application doit considérer les conséquences de la perte et du désordre.

## 10.2 Les applications basées sur UDP peuvent ajouter de la fiabilité

Une application peut définir :

- des identifiants de message ;
- des numéros de séquence ;
- des accusés de réception ;
- des temporisateurs ;
- des retransmissions ;
- une déduplication ;
- une gestion des délais d'expiration.

Un protocole supérieur peut ainsi obtenir des garanties adaptées à ses besoins.

QUIC est un exemple important : il utilise UDP mais fournit ses propres mécanismes de transport, de contrôle de flux et de récupération de pertes.

## 10.3 Taille des datagrammes et MTU

UDP ne garantit pas que des datagrammes volumineux traverseront tout le chemin sans fragmentation ou perte.

La taille maximale utile dépend de la famille IP, de la MTU du chemin et de l'encapsulation.

Les applications sensibles aux pertes de datagrammes doivent éviter de supposer qu'un envoi local garantit la livraison de l'intégralité des données distantes.

## 10.4 Pourquoi un test UDP est difficile à interpréter

UDP ne possède pas de handshake intégré qui prouve que le service distant accepte les datagrammes.

Une absence de réponse peut signifier :

- que le service n'écoute pas ;
- que la requête n'est pas comprise ;
- que le pare-feu supprime le datagramme ;
- que la réponse est perdue ;
- que le service n'est pas conçu pour répondre à cette requête ;
- que la réponse emprunte un chemin différent.

Le diagnostic doit s'appuyer sur le protocole applicatif et la réponse attendue.


# 11. Ports connus, enregistrés et éphémères

Les ports fournissent des identifiants de transport, mais ils ne définissent pas à eux seuls le protocole applicatif.

Le registre IANA centralise les affectations officielles de noms de service et de numéros de port.

## 11.1 Tableau pratique des services

| Service | Port courant | Transport usuel | Remarques |
|---|---:|---|---|
| HTTP | 80 | TCP | Port traditionnel pour HTTP |
| HTTPS | 443 | TCP, ou UDP pour QUIC/HTTP/3 | Le transport dépend du protocole utilisé |
| DNS | 53 | UDP et TCP | Les deux existent |
| SSH | 22 | TCP | Port par défaut habituel |
| SMTP | 25 | TCP | Transfert entre serveurs selon la configuration |
| Soumission de courrier | 587 | TCP | Port courant de soumission |
| DNS sécurisé via certains protocoles | Variable selon le protocole | Variable | Vérifier le service concerné |
| DHCPv4 serveur/client | 67/68 | UDP | Affectation et configuration IPv4 |
| NTP | 123 | UDP | Synchronisation horaire courante |
| RDP | 3389 | TCP et UDP selon l'usage | Peut employer plusieurs transports |

Ce tableau présente des valeurs courantes, non des règles absolues. Les services peuvent être configurés sur d'autres ports. Vérifiez toujours le registre IANA et la documentation de l'application.

## 11.2 Les ports éphémères

Un client utilise souvent un port source éphémère pour distinguer la communication.

Le port est sélectionné selon les mécanismes du système d'exploitation. La plage, la stratégie de sélection et les contraintes de réutilisation varient selon l'environnement.

Le port éphémère n'est pas un serveur temporaire automatiquement ouvert à tout le réseau. C'est d'abord un élément d'identification de l'extrémité de transport.

## 11.3 Vérifier l'écoute

Sous Windows :

```powershell
Get-NetTCPConnection -State Listen
```

Sous Linux :

```bash
ss -lntup
```

Les commandes et les informations affichées dépendent des privilèges et du système d'exploitation.

Pour UDP, l'état « écoute » ne représente pas le même handshake que TCP. Il indique principalement qu'un socket a été lié à une adresse et à un port.


# 12. Pare-feu et NAT

## 12.1 Filtrage avec état

Un pare-feu à état suit les informations relatives aux flux qu'il reconnaît.

Lorsqu'une règle autorise une connexion TCP dans un sens, l'équipement peut autoriser les paquets de retour associés à cette connexion en fonction de son état et de ses règles.

La politique n'est pas identique sur tous les produits. Certains équipements effectuent des inspections supplémentaires et peuvent imposer des conditions applicatives.

## 12.2 NAT et tuples modifiés

Un NAT peut modifier l'adresse IP source ou destination et, dans certaines formes de traduction, les ports également.

Les tuples observés sur le réseau intérieur et extérieur peuvent donc être différents.

Lors d'une investigation, il faut corréler les flux à partir des informations disponibles, et pas uniquement comparer l'adresse source.

## 12.3 Symptômes de filtrage

Un filtrage peut :

- rejeter explicitement une connexion ;
- envoyer un RST ou un message d'erreur ;
- supprimer silencieusement les paquets ;
- autoriser l'établissement, puis filtrer certains échanges ;
- autoriser TCP tout en bloquant un protocole UDP utilisé parallèlement.

Le symptôme doit être confronté aux journaux et aux captures du réseau concerné.


# 13. QUIC et HTTP/3

QUIC est un protocole de transport qui fonctionne au-dessus d'UDP.

Il fournit notamment :

- des flux ;
- des mécanismes de fiabilité pour les données concernées ;
- du contrôle de flux ;
- des mécanismes de perte et de congestion ;
- l'intégration avec TLS pour la sécurité ;
- des possibilités de migration du chemin selon les mécanismes du protocole.

HTTP/3 utilise QUIC.

## 13.1 Pourquoi cela est-il important ?

Une analyse limitée à TCP ne permet pas d'expliquer tout le trafic Web actuel.

Lorsqu'un navigateur établit HTTP/3, l'échange peut apparaître sous forme de trafic UDP/443 associé à QUIC.

Un test de port TCP/443 ne vérifie donc pas automatiquement le chemin UDP/443 utilisé par QUIC.

De même, bloquer UDP/443 peut empêcher l'établissement d'une connexion QUIC, même si TCP/443 reste autorisé. Le comportement de repli dépend du client, du serveur et de leur configuration.

## 13.2 QUIC n'est pas « UDP sans fiabilité »

QUIC réutilise UDP comme transport inférieur pour les datagrammes IP, mais il implémente ses propres mécanismes de transport.

Il est donc incorrect de conclure qu'une application HTTP/3 perd forcément sa fiabilité parce que QUIC utilise UDP.

Il faut distinguer la fiabilité native du protocole UDP des fonctions ajoutées par QUIC au-dessus de celui-ci.


# 14. Schéma SVG animé — TCP, UDP et QUIC

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 430" role="img" aria-labelledby="quic-int-title quic-int-desc">
<title id="quic-int-title">Comparaison des piles TCP, UDP et QUIC</title>
<desc id="quic-int-desc">Trois colonnes représentent un transport TCP, un transport UDP simple et un transport QUIC au-dessus d'UDP. Chaque pile possède une surbrillance indépendante.</desc>
<rect width="960" height="430" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-family="Arial,sans-serif" font-weight="700" fill="#0f172a">Trois piles de transport à distinguer</text>
<g font-family="Arial,sans-serif">
  <rect x="40" y="115" width="250" height="210" rx="12" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
  <text x="165" y="85" text-anchor="middle" font-size="18" font-weight="700" fill="#334155">TCP classique</text>
  <rect x="65" y="135" width="200" height="55" rx="8" fill="#bfdbfe" stroke="#2563eb"/><text x="165" y="168" text-anchor="middle" font-size="16" font-weight="700" fill="#1e3a8a">Application</text>
  <rect x="65" y="200" width="200" height="55" rx="8" fill="#bbf7d0" stroke="#15803d"/><text x="165" y="233" text-anchor="middle" font-size="16" font-weight="700" fill="#14532d">TCP</text>
  <rect x="65" y="265" width="200" height="40" rx="8" fill="#fde68a" stroke="#b45309"/><text x="165" y="290" text-anchor="middle" font-size="15" font-weight="700" fill="#78350f">IP</text>
  <rect x="355" y="115" width="250" height="210" rx="12" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
  <text x="480" y="85" text-anchor="middle" font-size="18" font-weight="700" fill="#334155">UDP direct</text>
  <rect x="380" y="135" width="200" height="55" rx="8" fill="#bfdbfe" stroke="#2563eb"/><text x="480" y="168" text-anchor="middle" font-size="16" font-weight="700" fill="#1e3a8a">Application</text>
  <rect x="380" y="200" width="200" height="55" rx="8" fill="#ddd6fe" stroke="#7c3aed"/><text x="480" y="233" text-anchor="middle" font-size="16" font-weight="700" fill="#5b21b6">UDP</text>
  <rect x="380" y="265" width="200" height="40" rx="8" fill="#fde68a" stroke="#b45309"/><text x="480" y="290" text-anchor="middle" font-size="15" font-weight="700" fill="#78350f">IP</text>
  <rect x="670" y="115" width="250" height="210" rx="12" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
  <text x="795" y="85" text-anchor="middle" font-size="18" font-weight="700" fill="#334155">QUIC</text>
  <rect x="695" y="135" width="200" height="45" rx="8" fill="#bfdbfe" stroke="#2563eb"/><text x="795" y="163" text-anchor="middle" font-size="15" font-weight="700" fill="#1e3a8a">HTTP/3</text>
  <rect x="695" y="189" width="200" height="45" rx="8" fill="#bbf7d0" stroke="#15803d"/><text x="795" y="217" text-anchor="middle" font-size="15" font-weight="700" fill="#14532d">QUIC + TLS</text>
  <rect x="695" y="243" width="200" height="40" rx="8" fill="#ddd6fe" stroke="#7c3aed"/><text x="795" y="268" text-anchor="middle" font-size="15" font-weight="700" fill="#5b21b6">UDP</text>
  <rect x="695" y="290" width="200" height="25" rx="7" fill="#fde68a" stroke="#b45309"/><text x="795" y="307" text-anchor="middle" font-size="13" font-weight="700" fill="#78350f">IP</text>
  <rect x="60" y="196" width="210" height="62" rx="11" fill="none" stroke="#0f766e" stroke-width="4"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="3s" repeatCount="indefinite"/></rect>
  <rect x="375" y="196" width="210" height="62" rx="11" fill="none" stroke="#7c3aed" stroke-width="4"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="3.8s" repeatCount="indefinite"/></rect>
  <rect x="690" y="184" width="210" height="106" rx="11" fill="none" stroke="#0f766e" stroke-width="4"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="4.3s" repeatCount="indefinite"/></rect>
  <text x="40" y="361" font-size="14" fill="#334155">TCP fournit un flux fiable.</text>
  <text x="355" y="361" font-size="14" fill="#334155">UDP fournit des datagrammes.</text>
  <text x="670" y="361" font-size="14" fill="#334155">QUIC ajoute un transport avancé.</text>
  <text x="40" y="391" font-size="13" fill="#64748b">La pile réelle dépend de l'application et des protocoles employés.</text>
</g>
</svg>


# 15. Captures Wireshark

Wireshark permet d'observer le comportement réel des flux lorsque la capture est prise au bon endroit.

Les filtres suivants sont des filtres d'affichage :

| Filtre | Utilité |
|---|---|
| `tcp` | Afficher les paquets TCP |
| `udp` | Afficher les paquets UDP |
| `tcp.port == 443` | Filtrer TCP associé au port 443 |
| `udp.port == 53` | Filtrer UDP associé au port 53 |
| `tcp.flags.syn == 1` | Afficher les segments ayant le bit SYN positionné |
| `tcp.flags.reset == 1` | Afficher les segments ayant le bit RST positionné |
| `tcp.analysis.retransmission` | Afficher les retransmissions signalées par l'analyse |
| `tcp.analysis.duplicate_ack` | Afficher les ACK dupliqués selon la détection de Wireshark |
| `udp.length > 1200` | Afficher les datagrammes UDP dont la longueur indiquée dépasse cette valeur |
| `ip.addr == 192.0.2.10` | Afficher les paquets associés à cette adresse IPv4 |

Les annotations de Wireshark sont des indices, pas des diagnostics définitifs.

Un filtre d'affichage masque les paquets dans l'interface. Un filtre de capture, lui, peut empêcher leur enregistrement initial.

## 15.1 Analyser une connexion TCP

1. Identifiez le début du flux.
2. Relevez les ports et les adresses aux deux extrémités.
3. Repérez SYN, SYN-ACK et ACK lorsque le handshake classique est utilisé.
4. Examinez les premières données.
5. Observez les ACK, les numéros de séquence et les fenêtres.
6. Recherchez les retransmissions, RST ou FIN.
7. Corrélez les observations avec la durée de l'échange et les journaux applicatifs.

## 15.2 Analyser UDP

1. Identifiez le protocole applicatif.
2. Vérifiez les ports source et destination.
3. Comparez la requête aux réponses attendues.
4. Recherchez les duplications ou les différences de contenu lorsque cela est pertinent.
5. Vérifiez si une absence de réponse est normale pour ce protocole.
6. Examinez les points de capture et les éventuelles pertes.

Le fait de voir un datagramme UDP sortir de l'interface ne prouve pas qu'il est arrivé au destinataire.


# 16. Laboratoires

## TP 1 — Observer les ports locaux

Sous Windows :

```powershell
netstat -ano
Get-NetTCPConnection
```

Sous Linux :

```bash
ss -lntup
ss -tan
```

Objectifs :

- repérer un service en écoute ;
- distinguer un socket en écoute d'une connexion TCP établie ;
- identifier les adresses et ports locaux ;
- associer, lorsque les droits le permettent, une connexion à son processus.

## TP 2 — Tester un port TCP

```powershell
Test-NetConnection exemple.com -Port 443
```

Ou :

```bash
nc -vz exemple.com 443
```

Notez le résultat, la date, le nom testé et le port.

Ensuite, testez le même service avec un outil applicatif comme `curl` afin de distinguer l'accès TCP de l'accès HTTPS.

```bash
curl -Iv https://exemple.com
```

## TP 3 — Observer le handshake

1. Démarrez une capture autorisée.
2. Lancez une connexion TCP vers un service accessible.
3. Utilisez le filtre `tcp.flags.syn == 1`.
4. Observez les segments de l'ouverture.
5. Relevez les ports et numéros de séquence.
6. Examinez la fermeture si elle est présente dans la capture.

Le comportement d'une connexion réutilisée, d'un proxy ou d'un transport différent peut changer ce que vous observez.

## TP 4 — Comparer TCP et UDP

Pour chaque protocole, définissez une question de test précise.

- Pour TCP, recherchez si l'établissement se produit et si le service accepte ensuite la requête.
- Pour UDP, définissez le datagramme attendu et déterminez si le protocole doit répondre.

N'utilisez pas un test UDP arbitraire pour déclarer ouvert ou fermé un port dont vous ne connaissez pas le protocole applicatif.


# 17. Exercices

## Exercice 1 — Tuple de connexion

Deux connexions TCP utilisent la même adresse source, la même adresse destination et le même port destination. Comment peuvent-elles être distinguées ?

## Exercice 2 — État TCP

Un poste présente plusieurs sockets en `CLOSE-WAIT`. Pourquoi cette observation peut-elle justifier une investigation de l'application ?

## Exercice 3 — TIME-WAIT

Pourquoi ne faut-il pas considérer systématiquement `TIME-WAIT` comme une panne ?

## Exercice 4 — SACK

Quelle information supplémentaire SACK peut-il fournir par rapport à un ACK cumulatif ?

## Exercice 5 — Fenêtres TCP

Expliquez la différence entre la fenêtre de réception et la fenêtre de congestion.

## Exercice 6 — UDP sans réponse

Une requête UDP ne reçoit aucune réponse. Donnez cinq causes possibles qui ne supposent pas automatiquement que le port est fermé.

## Exercice 7 — QUIC

Pourquoi bloquer UDP/443 peut-il affecter une connexion HTTP/3 même si TCP/443 reste autorisé ?

## Exercice 8 — Retransmission

Wireshark signale une retransmission TCP. Quelles informations faut-il examiner avant d'en attribuer la cause à un équipement intermédiaire ?

## Exercice 9 — Port en écoute

Pourquoi un serveur qui écoute sur un port TCP localement peut-il rester inaccessible depuis un poste distant ?

## Exercice 10 — FIN et RST

Distinguez la fermeture normale par FIN de la réinitialisation associée à RST.


# 18. Corrigés commentés

**Exercice 1**

Les connexions sont généralement distinguées par leur port source différent, ou plus généralement par leur tuple et leur état de connexion.

**Exercice 2**

`CLOSE-WAIT` indique généralement que la fermeture a été initiée par l'autre extrémité et que l'application locale doit terminer sa partie de fermeture. Un grand nombre de sockets qui persistent peut justifier la vérification du traitement applicatif.

**Exercice 3**

`TIME-WAIT` participe au fonctionnement normal de TCP après certaines fermetures, notamment pour gérer des segments retardés et certaines réutilisations de tuple. Sa présence n'est donc pas une panne en soi.

**Exercice 4**

SACK indique des blocs de données reçus au-delà du prochain octet attendu par l'ACK cumulatif. Cela permet à l'émetteur de mieux identifier les données manquantes.

**Exercice 5**

La fenêtre de réception limite les données en vol en fonction de la capacité annoncée par le récepteur. La fenêtre de congestion limite le volume autorisé par l'algorithme de congestion de l'émetteur.

**Exercice 6**

Le service ne répond pas à cette requête, le datagramme a été perdu, la réponse a été perdue, un filtrage silencieux existe, le protocole applicatif attend d'autres paramètres ou la capture n'est pas faite au bon endroit.

**Exercice 7**

HTTP/3 utilise QUIC au-dessus d'UDP. L'autorisation de TCP/443 ne garantit donc pas que le trafic UDP/443 nécessaire à une connexion QUIC soit autorisé.

**Exercice 8**

Il faut examiner les séquences, les ACK, le délai, les captures complémentaires, les pertes de capture et les éventuels offloads. La retransmission est un indice, pas une preuve de la cause.

**Exercice 9**

Le service peut être lié à la mauvaise adresse, un pare-feu peut filtrer le trafic, une route peut manquer, une règle NAT peut être absente ou l'adresse distante peut être incorrecte.

**Exercice 10**

FIN est associé à une fermeture ordonnée d'une direction du flux. RST est associé à une réinitialisation ou à un rejet de connexion selon le contexte.


# 19. Glossaire intermédiaire

**ACK cumulatif :** acquittement qui indique le prochain octet attendu dans le flux TCP.

**CLOSE-WAIT :** état TCP dans lequel l'extrémité locale a reçu la fermeture de l'autre côté et attend généralement que l'application termine son propre côté.

**Cwnd :** fenêtre de congestion TCP.

**FIN :** indicateur TCP associé à la fermeture ordonnée.

**MSS :** quantité maximale de données TCP dans un segment, hors en-têtes TCP et IP.

**NAT :** traduction d'adresses et parfois de ports.

**RTO :** temporisateur de retransmission.

**RST :** indicateur TCP associé à une réinitialisation ou à un rejet.

**RTT :** temps aller-retour mesuré pour un échange.

**SACK :** mécanisme TCP d'acquittement sélectif.

**Socket :** point d'extrémité ou interface de communication selon le contexte.

**TIME-WAIT :** état TCP normal après certaines fermetures.

**Tuple :** ensemble des adresses, ports et protocole utilisé pour caractériser un flux.

**Window Scale :** option TCP permettant de représenter des fenêtres plus grandes.


# 20. Ressources de référence

- [TCP — RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html)
- [Gestion du temporisateur de retransmission — RFC 6298](https://www.rfc-editor.org/rfc/rfc6298.html)
- [Acquittement sélectif TCP — RFC 2018](https://www.rfc-editor.org/rfc/rfc2018.html)
- [QUIC — RFC 9000](https://www.rfc-editor.org/rfc/rfc9000.html)
- [Registre officiel des ports — IANA](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml)


## Conclusion

Le niveau intermédiaire doit vous permettre de passer des définitions à l'observation réelle.

Vous devez pouvoir distinguer un port en écoute d'une connexion établie, expliquer les numéros de séquence et les ACK, interpréter les retransmissions sans tirer de conclusion excessive et vérifier les différences entre TCP, UDP et QUIC.

Au niveau expert, ces notions seront utilisées pour analyser les mécanismes de performance, les interactions avec les middleboxes, les limites des captures et les comportements complexes de transport.