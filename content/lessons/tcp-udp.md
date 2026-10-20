# TCP, UDP et diagnostic de transport — parcours Admin Réseau Senior

> **Objectif.** Ce cours couvre le fonctionnement réel de TCP et UDP : établissement
> et fermeture des connexions, machine à états, numéros de séquence, contrôle de
> flux, contrôle de congestion, ports, sockets, retransmissions et diagnostic sur
> Linux. À la fin, vous devez pouvoir expliquer pourquoi une connexion reste en
> `TIME_WAIT`, pourquoi un serveur accumule des `CLOSE_WAIT`, pourquoi un débit
> s'effondre malgré une fenêtre annoncée large, et comment le prouver avec `ss`
> et `tcpdump`.
>
> **Public :** administrateur réseau ou système, candidat CCNA, ingénieur
> d'exploitation, développeur backend qui doit diagnostiquer un problème de
> transport.
>
> **Durée :** 60 à 90 minutes de lecture, 120 minutes avec les exercices et les
> manipulations.

## 1. TCP et UDP : deux contrats différents

TCP et UDP partagent la couche transport, mais ne rendent pas le même service.
TCP fournit un flux d'octets fiable, ordonné et avec contrôle de flux/congestion.
UDP fournit des datagrammes indépendants, sans garantie d'ordre, de livraison ni
de déduplication. Cette différence n'est pas une question de « rapidité » : elle
change ce que l'application doit gérer elle-même.

| Critère | TCP | UDP |
| --- | --- | --- |
| Connexion | Établie par un handshake | Aucune connexion |
| Fiabilité | Accusés, retransmissions | Aucune garantie |
| Ordre | Garanti sur le flux | Non garanti |
| Duplication | Détectée et éliminée | Possible |
| Contrôle de flux | Fenêtre de réception | Aucun |
| Contrôle de congestion | Oui (cwnd, perte, ECN) | Non, sauf mécanisme applicatif |
| Taille des données | Flux d'octets, segmentation | Datagramme, taille limitée |
| En-tête minimal | 20 octets | 8 octets |
| Usage typique | HTTP/1.1, SSH, SMTP, bases de données | DNS, DHCP, QUIC, VoIP, jeux |
| Multidiffusion | Non | Oui (multicast) |

Un mythe fréquent : « UDP est toujours plus rapide que TCP ». UDP évite le
handshake et certaines retransmissions, mais une application qui ajoute ses
propres accusés, son ordonnancement et sa gestion de congestion peut être plus
lente qu'un TCP bien réglé. QUIC utilise UDP tout en recréant une fiabilité et
un contrôle de congestion dans l'espace utilisateur, précisément parce que UDP
n'est qu'un transport de datagrammes.

### Le quadruplet et la socket

Une connexion TCP est identifiée par un **quadruplet** :

```text
(adresse source, port source, adresse destination, port destination)
```

Le système d'exploitation associe ce quadruplet à une **socket** et à un état.
Deux connexions peuvent partager la même adresse et le même port source si
leurs destinations diffèrent. Un serveur écoute sur un port avec une socket en
`LISTEN` ; chaque connexion acceptée crée une nouvelle socket avec son propre
quadruplet.

```text
Client 10.0.0.25:51514  <----TCP---->  Serveur 203.0.113.10:443
       (port éphémère)                 (port de service)
```

Les pare-feu stateful suivent ce quadruplet et l'état TCP pour autoriser le
retour. Une asymétrie de routage, un NAT ou un load-balancer peuvent modifier
le quadruplet observé et casser cette logique.

## 2. Le segment TCP

L'en-tête TCP minimal fait 20 octets et peut atteindre 60 octets avec options.

```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-------------------------------+-------------------------------+
|          Source Port          |       Destination Port        |
+-------------------------------+-------------------------------+
|                        Sequence Number                        |
+---------------------------------------------------------------+
|                    Acknowledgment Number                      |
+-------+-------+---------------+-------------------------------+
| Offset|Rsrvd  |CWR|ECE|URG|ACK|PSH|RST|SYN|FIN|  Window       |
+-------+-------+---+---+---+---+---+---+---+---+---------------+
|          Checksum             |       Urgent Pointer          |
+-------------------------------+-------------------------------+
|                    Options (0 à 40 octets)                    |
+---------------------------------------------------------------+
|                            Données                            |
+---------------------------------------------------------------+
```

| Champ | Rôle |
| --- | --- |
| Source/Destination Port | Multiplexage applicatif |
| Sequence Number | Position du premier octet de données dans le flux |
| Acknowledgment Number | Prochain octet attendu (ACK cumulatif) |
| Data Offset | Longueur de l'en-tête en mots de 32 bits |
| Flags | SYN, ACK, FIN, RST, PSH, URG, ECE, CWR |
| Window | Fenêtre de réception annoncée, en octets |
| Checksum | Contrôle d'intégrité de l'en-tête et des données |
| Urgent Pointer | Données urgentes, rarement utilisées |
| Options | MSS, window scaling, SACK, timestamps, etc. |

### Numéros de séquence et ACK

TCP numérote les **octets**, pas les segments. Si un segment commence au
numéro 1000 et transporte 500 octets, le prochain octet attendu est 1500. Un
ACK de 1500 signifie « j'ai reçu jusqu'à l'octet 1499 inclus ». L'ACK est
cumulatif : un ACK 1500 confirme aussi tout ce qui précède, même si des ACK
intermédiaires ont été perdus.

```text
Client                                    Serveur
  seq=1000, len=500  -------------------->
                     <--------------------  ack=1500
  seq=1500, len=500  -------------------->
                     <--------------------  ack=2000
```

Les numéros initiaux (ISN) ne commencent pas à zéro : ils sont choisis de façon
imprévisible pour rendre plus difficile l'injection de segments. Le handshake
synchronise les deux sens et confirme la réception des ISN.

### Options importantes

| Option | Rôle | Piège |
| --- | --- | --- |
| MSS | Taille maximale de données TCP par segment | Ne pas confondre avec MTU |
| Window Scale | Multiplie la fenêtre annoncée | Absente = fenêtre limitée à 64 Ko |
| SACK Permitted / SACK | Signale des blocs reçus hors ordre | Accélère la récupération |
| Timestamps | RTT et protection contre les anciens segments | Peut compliquer la lecture des captures |
| NOP | Alignement | — |

La MSS est la MTU IP moins les en-têtes IP et TCP. Pour une MTU Ethernet de
1500, IPv4 sans options : `1500 - 20 - 20 = 1460` octets de données TCP. Avec
IPv6 : `1500 - 40 - 20 = 1440`. Un tunnel réduit encore la MSS. Une MSS mal
négociée ou un PMTUD cassé provoque des petits paquets qui passent et des gros
transferts qui échouent.

## 3. Le handshake en trois étapes

### Séquence normale

```text
Client                                              Serveur
  état CLOSED                                         état LISTEN
       |                                                 |
       |  SYN, seq=x, options (MSS, WS, SACK, TS)        |
       |------------------------------------------------>|
       |                                                 | SYN_RECEIVED
       |  SYN+ACK, seq=y, ack=x+1, options               |
       |<------------------------------------------------|
  SYN_SENT                                              |
       |  ACK, seq=x+1, ack=y+1                          |
       |------------------------------------------------>|
  ESTABLISHED                                     ESTABLISHED
```

1. **SYN** : le client choisit un ISN `x` et propose ses options.
2. **SYN+ACK** : le serveur choisit un ISN `y`, accuse `x+1` et renvoie ses
   options.
3. **ACK** : le client accuse `y+1`. La connexion est établie des deux côtés.

Le troisième ACK peut transporter des données (TCP Fast Open ou données
immédiatement après l'ACK). Les options du SYN ne sont pas répétées dans les
segments suivants ; elles sont mémorisées pour la connexion.

### Ce que chaque côté apprend

| Information | Négociée par |
| --- | --- |
| MSS | Chaque côté annonce la taille maximale qu'il accepte |
| Window scale | Chaque côté annonce son facteur |
| SACK | Les deux côtés doivent le permettre |
| Timestamps | Les deux côtés doivent l'envoyer |
| RTT initial | Mesuré après le SYN-ACK |

Le MSS annoncé par le client indique ce que le client peut recevoir, pas ce
qu'il peut envoyer. Chaque côté applique la MSS de son pair pour segmenter ses
propres données. Une erreur de lecture de capture est fréquente : la MSS du SYN
d'un côté ne limite pas les segments émis par ce même côté.

### SYN, ACK, RST et half-open

- Un **SYN** sans réponse peut venir d'un filtrage, d'une route absente, d'un
  serveur saturé ou d'une écoute absente.
- Un **RST** immédiat signifie souvent « port fermé » ou « connexion inconnue ».
- Une connexion **half-open** existe lorsqu'un côté croit la connexion établie
  et l'autre l'a oubliée. Un keepalive ou une retransmission finit par produire
  un RST.
- Un **SYN flood** remplit la file des connexions semi-ouvertes. Les SYN cookies
  permettent au serveur de ne pas mémoriser chaque SYN en attendant l'ACK.

### SYN cookies et files d'attente

Le serveur possède généralement deux files :

| File | Contenu |
| --- | --- |
| SYN queue | Connexions `SYN_RECEIVED` en attente du troisième ACK |
| Accept queue | Connexions établies en attente d'`accept()` par l'application |

Une application qui n'appelle pas `accept()` assez vite peut laisser la accept
queue pleine ; de nouveaux clients voient des timeouts ou des RST alors que le
réseau et le serveur semblent up. Sur Linux, `ss -lnt` montre `Send-Q`/`Recv-Q`
pour les sockets en écoute ; `Recv-Q` peut refléter la accept queue. Vérifiez
aussi `net.core.somaxconn` et le backlog passé à `listen()`.

## 4. Transfert, retransmission et acquittements

### Acquittement cumulatif et SACK

TCP acquitte le flux jusqu'au premier trou. Si les segments 1, 2, 4 arrivent et
que 3 manque, le récepteur acquitte 1 et 2 (ou 1 et 2+4 avec SACK) mais ne peut
pas acquitter 3. L'émetteur retransmet le trou après un délai ou après plusieurs
ACK dupliqués. SACK permet de décrire les blocs reçus et évite de retransmettre
inutilement les segments 4 et suivants.

### RTO, RTT et retransmissions

TCP estime le RTT et calcule un **RTO** (Retransmission Timeout). Un RTO trop
court provoque des retransmissions inutiles ; un RTO trop long allonge la
récupération. Les algorithmes modernes (Jacobson/Karels, timestamps) ajustent
le RTO. `ss -ti` expose souvent `rtt`, `rttvar`, `rto`, `retrans`, `cwnd` et
`bytes_retrans`.

Une retransmission peut être :

- **timeout** : aucun ACK avant le RTO, souvent après une perte sévère ;
- **fast retransmit** : trois ACK dupliqués déclenchent une retransmission
  avant le RTO ;
- **spurious** : retransmission inutile due à un RTO trop agressif ou à un ACK
  retardé.

### ACK différé et Nagle

Le récepteur peut retarder un ACK pour en acquitter plusieurs d'un coup
(*delayed ACK*). L'émetteur peut regrouper de petites écritures avec **Nagle**.
L'interaction Nagle + delayed ACK peut ajouter des latences de dizaines de
millisecondes sur des requêtes applicatives en petits morceaux. Les options
`TCP_NODELAY` et `TCP_QUICKACK` permettent de contrôler ce comportement, mais
il faut mesurer avant de désactiver Nagle partout.

### Keepalive

TCP keepalive envoie des sondes après une période d'inactivité pour détecter
un pair disparu. Ce n'est pas un mécanisme de heartbeat applicatif : les délais
par défaut sont longs (souvent 2 heures) et l'application peut avoir ses propres
timeouts. Sur Linux :

```bash
sysctl net.ipv4.tcp_keepalive_time
sysctl net.ipv4.tcp_keepalive_intvl
sysctl net.ipv4.tcp_keepalive_probes
```

Un keepalive sur une connexion idle peut produire un RST si l'autre extrémité
a redémarré ou perdu l'état (NAT, load-balancer, redémarrage d'application).

## 5. La fermeture en quatre étapes

### Séquence normale

```text
Client                                              Serveur
ESTABLISHED                                     ESTABLISHED
     |                                                   |
     |  FIN, seq=u                                      |
     |-------------------------------------------------->|
 FIN_WAIT_1                                      CLOSE_WAIT
     |  ACK, ack=u+1                                    |
     |<--------------------------------------------------|
 FIN_WAIT_2                                            |
     |                                    (l'application lit puis ferme)
     |  FIN, seq=v                                      |
     |<--------------------------------------------------|
     |  ACK, ack=v+1                                    |
     |-------------------------------------------------->|
 TIME_WAIT                                       LAST_ACK
     |                                                   |
     |  attendre 2*MSL                                   |
     |                                                   v
   CLOSED                                           CLOSED
```

1. Le côté actif envoie **FIN**. Il ne peut plus envoyer de données, mais peut
   encore en recevoir.
2. L'autre côté renvoie **ACK** et passe en `CLOSE_WAIT`. L'application doit
   lire les données restantes puis appeler `close()`.
3. Le côté passif envoie **FIN**.
4. Le côté actif renvoie **ACK** et passe en `TIME_WAIT`.

Une fermeture est donc **half-close** : chaque direction se ferme séparément.
Un serveur qui ne ferme jamais la sienne reste en `CLOSE_WAIT`. C'est un
symptôme applicatif, pas un problème réseau.

### Pourquoi TIME_WAIT existe

`TIME_WAIT` dure généralement **2 × MSL** (Maximum Segment Lifetime), souvent
60 secondes sur Linux (`TCP_TIMEWAIT_LEN`), mais la valeur dépend du noyau.
Deux raisons :

1. Laisser le temps au dernier ACK d'arriver ; si le FIN est retransmis, le
   côté qui est en `TIME_WAIT` peut répondre.
2. Éviter qu'une ancienne connexion (même quadruplet) ne reçoive des segments
   retardés et les mélange avec une nouvelle connexion.

`TIME_WAIT` est donc normal sur le côté qui ferme activement. Il devient un
problème lorsque le volume de connexions éphémères est énorme ou que les ports
source sont épuisés. Réutiliser agressivement les sockets ou réduire le délai
peut casser la protection contre les anciens segments ; mesurez et corrigez
d'abord la cause (keepalive, pooling, HTTP/2, etc.).

### RST et fermeture brutale

Un **RST** ferme immédiatement la connexion, sans handshake de fermeture. Il
peut être envoyé par :

- un port fermé ou une socket sans écoute ;
- une application qui ferme avec des données non lues (`SO_LINGER` zéro) ;
- un pare-feu ou un load-balancer qui rejette un flux inconnu ;
- une pile qui reçoit un segment incohérent.

Un RST n'est pas toujours une erreur : c'est parfois la bonne réponse à un
paquet destiné à un port fermé. Dans une capture, distinguez le RST immédiat
(port fermé) du RST après retransmissions (état perdu, NAT, timeout).

## 6. Machine à états TCP

Les états TCP décrivent ce que chaque extrémité attend. Ils sont visibles dans
`ss` et `netstat`.

```text
CLOSED
  | SYN envoyé                 | SYN reçu
  v                            v
SYN_SENT                     LISTEN
  | SYN+ACK reçu               | SYN reçu, SYN+ACK envoyé
  v                            v
ESTABLISHED                  SYN_RECEIVED
  | FIN reçu                   | ACK reçu
  v                            v
CLOSE_WAIT                   ESTABLISHED
  | close()                    |
  v                            | FIN envoyé
LAST_ACK                       v
  | ACK reçu                 FIN_WAIT_1
  v                            | ACK reçu
CLOSED                         v
                            FIN_WAIT_2
                               | FIN reçu
                               v
                            TIME_WAIT
                               | 2*MSL
                               v
                            CLOSED
```

| État | Signification | Où le voir |
| --- | --- | --- |
| CLOSED | Aucune connexion | État théorique |
| LISTEN | Socket serveur en attente de SYN | `ss -lnt` |
| SYN_SENT | SYN envoyé, ACK attendu | Client qui se connecte |
| SYN_RECEIVED | SYN reçu, SYN+ACK envoyé, ACK attendu | Serveur sous charge ou SYN flood |
| ESTABLISHED | Connexion établie, données possibles | Les deux côtés |
| FIN_WAIT_1 | FIN envoyé, ACK/FIN attendu | Côté qui ferme |
| FIN_WAIT_2 | ACK du FIN reçu, FIN du pair attendu | Côté qui ferme |
| CLOSE_WAIT | FIN reçu, l'application n'a pas encore fermé | Côté passif |
| LAST_ACK | FIN envoyé après CLOSE_WAIT, ACK attendu | Côté passif |
| TIME_WAIT | ACK final envoyé, attente 2*MSL | Côté qui a fermé activement |
| CLOSING | FIN et ACK croisés | Fermeture simultanée |

### Lire les états dans la pratique

- Beaucoup de `SYN_SENT` côté client : destination injoignable, filtrage SYN,
  serveur saturé, route retour absente.
- Beaucoup de `SYN_RECEIVED` côté serveur : SYN flood, backlog insuffisant,
  handshake incomplet, perte du troisième ACK.
- Beaucoup de `CLOSE_WAIT` : l'application ne ferme pas ses sockets ; fuite de
  descripteurs, bug de code, pool mal géré.
- Beaucoup de `TIME_WAIT` : côté qui ferme activement beaucoup de connexions
  courtes ; normal, mais peut épuiser les ports éphémères.
- `FIN_WAIT_2` persistant : le pair n'envoie jamais son FIN ; application ou
  pare-feu qui ne termine pas.
- `LAST_ACK` persistant : le FIN du serveur n'est pas acquitté ; perte ou
  filtrage.

## 7. Contrôle de flux : la fenêtre de réception

Le contrôle de flux protège le **récepteur** : il empêche l'émetteur d'envoyer
plus de données que le buffer et l'application ne peuvent en absorber. Chaque
ACK annonce une **fenêtre** (window) : nombre d'octets que l'émetteur peut
encore envoyer sans dépasser la capacité du récepteur.

```text
Émetteur                                      Récepteur
  |  données seq=1000..1999 (1000 octets)        |
  |--------------------------------------------->|
  |                                             | buffer 4096
  |  ACK 2000, window=3096                       |
  |<---------------------------------------------|
  |  peut envoyer jusqu'à 2000+3096=5096         |
```

La fenêtre annoncée est une autorisation glissante. Quand l'application lit
les données, le buffer se libère et la fenêtre augmente. Si l'application ne
lit pas, la fenêtre descend jusqu'à zéro.

### Window scaling

Le champ Window fait 16 bits, soit 65 535 octets. Pour les liens à haut débit
et long RTT, c'est insuffisant. L'option **Window Scale** négociée dans le SYN
multiplie la fenêtre par `2^scale` (scale de 0 à 14). Une fenêtre annoncée de
65 535 avec un scale de 7 représente 8 388 480 octets.

```text
Fenêtre effective = Window annoncée × 2^scale
```

Le facteur est négocié dans le SYN et ne change pas. Il est propre à chaque
direction. Une capture qui affiche `win 501` peut donc représenter une fenêtre
réelle beaucoup plus grande après application du scale.

### Zero window, persist timer et silly window

- **Zero window** : le récepteur annonce 0 ; l'émetteur arrête d'envoyer.
- **Persist timer** : l'émetteur envoie périodiquement une sonde pour savoir
  quand la fenêtre se rouvre.
- **Window update** : le récepteur envoie un ACK avec une nouvelle fenêtre.
- **Silly Window Syndrome** : éviter d'annoncer ou d'envoyer des micro-fenêtres
  inefficaces ; les algorithmes de Nagle/SWS regroupent les petites données.

Une fenêtre à zéro persistante indique souvent une application qui ne lit pas
son socket (blocage, thread pool saturé, GC, deadlock). Ce n'est pas un problème
de bande passante : regardez le CPU, les locks et le code du récepteur.

### Tuning des buffers

```bash
sysctl net.ipv4.tcp_rmem
sysctl net.ipv4.tcp_wmem
sysctl net.core.rmem_max
sysctl net.core.wmem_max
```

`tcp_rmem` et `tcp_wmem` sont des triplets min/default/max. Augmenter les
buffers peut améliorer le débit sur les liens à grand RTT, mais augmente la
mémoire et peut aggraver le **bufferbloat** si la congestion est mal signalée.
La taille optimale dépend du produit bande passante × RTT (BDP) et du nombre
de connexions.

## 8. Contrôle de congestion : slow start et au-delà

Le contrôle de flux protège le récepteur ; le contrôle de congestion protège
le **réseau**. TCP maintient une fenêtre de congestion `cwnd` et une fenêtre
de réception `rwnd`. La quantité de données en vol est limitée par :

```text
fenêtre effective = min(cwnd, rwnd)
```

### Slow start

Au début, `cwnd` est petite (souvent 10 MSS avec les implémentations modernes,
ou 1 à 4 selon l'époque et le paramètre). À chaque ACK, `cwnd` augmente
d'environ 1 MSS : la fenêtre double à chaque RTT.

```text
RTT 1 : cwnd = 1 MSS   -> 1 segment
RTT 2 : cwnd = 2 MSS   -> 2 segments
RTT 3 : cwnd = 4 MSS   -> 4 segments
RTT 4 : cwnd = 8 MSS   -> 8 segments
...
```

Cette croissance exponentielle dure jusqu'à `ssthresh` (slow start threshold).
Ensuite, TCP passe en **congestion avoidance** : `cwnd` augmente d'environ
1 MSS par RTT (additive increase), ce qui est beaucoup plus lent.

### Pertes, fast retransmit et fast recovery

- **Timeout** : `ssthresh = cwnd/2`, `cwnd` revient à 1 MSS (ou à une valeur
  initiale), puis slow start.
- **3 ACK dupliqués** : fast retransmit, `ssthresh = cwnd/2`, `cwnd` diminue
  puis fast recovery.
- **SACK** : permet de récupérer plusieurs trous sans attendre le timeout.
- **ECN** : le réseau marque les paquets au lieu de les jeter ; TCP réduit
  `cwnd` sans retransmission inutile. ECN doit être supporté de bout en bout.

```text
cwnd
  |        /\
  |      /   \      perte
  |    /      \    /
  |  /         \  /
  | /           \/
  |/______________________________________ temps
   slow start   congestion avoidance
```

### Reno, CUBIC, BBR

| Algorithme | Principe | Contexte |
| --- | --- | --- |
| Tahoe/Reno | Slow start, AIMD, fast recovery | Historique, base pédagogique |
| NewReno | Meilleure récupération multi-pertes | Ancien standard Linux |
| CUBIC | Croissance cubique, indépendante du RTT | Défaut Linux moderne |
| BBR | Modèle de bande passante et RTT | Réseaux à perte ou bufferbloat |
| DCTCP | ECN pour datacenters | Faible latence, incast |

Le choix de l'algorithme se fait côté émetteur. Sur Linux :

```bash
sysctl net.ipv4.tcp_congestion_control
sysctl net.ipv4.tcp_available_congestion_control
```

Un changement d'algorithme ne remplace pas un diagnostic : une perte massive,
un RTT qui explose ou une fenêtre zéro persistent malgré CUBIC/BBR.

### BDP, débit et latence

Le produit **bande passante × RTT** (BDP) donne la quantité de données qu'un
lien peut contenir. Pour 1 Gbit/s et 100 ms de RTT :

```text
BDP = 1 000 000 000 bits/s × 0.1 s = 100 000 000 bits = 12.5 Mo
```

Une fenêtre insuffisante ou un buffer trop petit limite le débit même si le
lien est libre. À l'inverse, des buffers trop grands dans le réseau créent de
la latence (bufferbloat) : les paquets attendent en file au lieu d'être
signalés. La solution combine dimensionnement, AQM (fq_codel, CAKE), ECN et
surveillance du RTT.

### Vérifier la congestion sur Linux

```bash
ss -ti
ss -tin state established
nstat -az TcpRetransSegs TcpExtTCPLostRetransmit TcpExtTCPSackRecv
```

`ss -ti` affiche souvent `cwnd`, `ssthresh`, `rtt`, `rto`, `retrans`,
`bytes_retrans`, `delivery_rate` et les options SACK. Une augmentation de
`retrans` avec un `rtt` stable oriente vers une perte locale ; un `rtt` qui
croît fortement avec peu de retransmissions oriente vers une file saturée.

## 9. Ports, sockets et services

### Plages de ports

| Plage | Nom | Usage |
| --- | --- | --- |
| 0–1023 | Well-known / system | Services standards, privilèges root historiques |
| 1024–49151 | Registered | Services enregistrés auprès de l'IANA |
| 49152–65535 | Dynamic / ephemeral | Ports source des clients, usage temporaire |

La plage éphémère Linux est visible avec :

```bash
sysctl net.ipv4.ip_local_port_range
```

Elle ne correspond pas nécessairement à la plage théorique 49152–65535. Une
plage trop petite, un grand nombre de connexions sortantes ou des `TIME_WAIT`
peuvent épuiser les ports source. Le quadruplet permet de réutiliser un port
source avec une destination différente, mais un serveur unique à fort volume
finit par atteindre la limite.

### Ports TCP/UDP les plus connus

| Port | Protocole | Service | Remarque |
| ---: | --- | --- | --- |
| 20/21 | TCP | FTP data/control | Chiffrement absent, préférer SFTP |
| 22 | TCP | SSH | Administration, tunnels |
| 23 | TCP | Telnet | Non chiffré, à éviter |
| 25 | TCP | SMTP | Relais de mail |
| 53 | TCP/UDP | DNS | UDP pour les requêtes, TCP pour les grandes réponses/zone transfers |
| 67/68 | UDP | DHCP serveur/client | Broadcast local, relais DHCP |
| 69 | UDP | TFTP | Transfert simple, provisioning |
| 80 | TCP | HTTP | Non chiffré |
| 110 | TCP | POP3 | Mail |
| 123 | UDP | NTP | Synchronisation de temps |
| 135 | TCP/UDP | RPC/DCOM | Windows |
| 137–139 | TCP/UDP | NetBIOS | Windows historique |
| 143 | TCP | IMAP | Mail |
| 161/162 | UDP | SNMP | Supervision, traps |
| 179 | TCP | BGP | Routage Internet |
| 389 | TCP/UDP | LDAP | Annuaire |
| 443 | TCP | HTTPS | HTTP/2, HTTP/3 (QUIC sur UDP 443) |
| 445 | TCP | SMB | Partage de fichiers Windows |
| 465/587 | TCP | SMTP sécurisé | Soumission de mail |
| 514 | UDP | Syslog | Journaux |
| 636 | TCP | LDAPS | LDAP chiffré |
| 993 | TCP | IMAPS | IMAP chiffré |
| 995 | TCP | POP3S | POP3 chiffré |
| 1194 | UDP | OpenVPN | VPN |
| 1433 | TCP | Microsoft SQL Server | Base de données |
| 1521 | TCP | Oracle Database | Base de données |
| 1812/1813 | UDP | RADIUS auth/accounting | 802.1X, VPN |
| 2049 | TCP/UDP | NFS | Stockage réseau |
| 3306 | TCP | MySQL/MariaDB | Base de données |
| 3389 | TCP/UDP | RDP | Bureau à distance |
| 4789 | UDP | VXLAN | Overlay datacenter |
| 5060/5061 | TCP/UDP/TLS | SIP | VoIP |
| 5432 | TCP | PostgreSQL | Base de données |
| 5672 | TCP | AMQP | Messagerie |
| 6379 | TCP | Redis | Cache (ne pas exposer) |
| 8080/8443 | TCP | HTTP/HTTPS alternatif | Proxies, applications |
| 9200/9300 | TCP | Elasticsearch | API et cluster |
| 27017 | TCP | MongoDB | Base de données |

**Attention :** un port ne prouve pas le service. Un serveur peut écouter SSH
sur 2222, HTTP sur 8080 ou un tunnel sur 443. Vérifiez la bannière, le
certificat, le processus et la politique de filtrage ; ne vous fiez pas au
numéro seul. De même, HTTP/3 utilise UDP 443, ce qui surprend les pare-feu qui
autorisent uniquement TCP 443.

### Sockets, backlog et descripteurs

Une socket est identifiée par le quadruplet et un descripteur de fichier. Un
serveur qui fuit des sockets finit par atteindre `ulimit -n`. Surveillez :

```bash
ulimit -n
cat /proc/sys/fs/file-nr
lsof -p <pid> | wc -l
ss -s
```

Un `accept()` lent, un thread pool saturé ou une fuite de descripteurs se
manifeste souvent par une accept queue pleine, des timeouts clients et des
`SYN_RECEIVED`/`CLOSE_WAIT` anormaux.

## 10. UDP en détail

L'en-tête UDP fait 8 octets : ports source/destination, longueur et checksum.

```text
+-------------------------------+
| Source Port   | Dest Port     |
+-------------------------------+
| Length        | Checksum      |
+-------------------------------+
| Données                        |
+-------------------------------+
```

UDP ne fournit ni ordre, ni retransmission, ni fenêtre. Le checksum UDP couvre
l'en-tête UDP, les données et un pseudo-en-tête IP (adresses source/destination,
protocole, longueur). Il est optionnel en IPv4 (0 = non calculé) mais obligatoire
en IPv6. Un checksum invalide fait jeter le datagramme silencieusement.

### Usages et contraintes

| Usage | Pourquoi UDP |
| --- | --- |
| DNS | Requête/réponse courte, retransmission applicative |
| DHCP | Broadcast, bootstrap |
| VoIP/RTP | Latence et gigue prioritaires, perte tolérable |
| Jeux | Frames fréquentes, état applicatif |
| QUIC/HTTP3 | Fiabilité et congestion dans l'espace utilisateur |
| Multicast | Pas de connexion par pair |
| SNMP traps | Événements sans session |

UDP est aussi utilisé pour des attaques par amplification : un petit datagramme
avec une source usurpée peut provoquer une grande réponse (DNS, NTP, memcached).
Limitez les services ouverts, filtrez l'usurpation et utilisez des réponses
proportionnées. Ne répondez pas aux broadcasts inutiles.

### Fragmentation et MTU

Un datagramme UDP trop grand est fragmenté par IP (IPv4) ou rejeté avec ICMP
Packet Too Big (IPv6/PMTUD). La fragmentation augmente les risques de perte :
si un fragment manque, tout le datagramme est perdu. Pour les applications
modernes, préférez des datagrammes proches de la MTU du chemin, ou une
segmentation applicative (QUIC). Vérifiez la MTU avec des pings DF et capturez
les messages ICMP.

## 11. Diagnostic avec ss, netstat et tcpdump

### ss : l'outil moderne

`ss` lit les sockets depuis le noyau et remplace `netstat` sur Linux.

```bash
# Toutes les sockets TCP/UDP, sans résolution de noms
ss -tunap

# Sockets en écoute TCP et UDP
ss -lntup

# Connexions établies
ss -tan state established

# Connexions vers un port donné
ss -tan '( dport = :443 or sport = :443 )'

# Résumé par état
ss -s

# Détails congestion, RTT, cwnd
ss -tin
ss -tin state established
```

Les colonnes `Recv-Q` et `Send-Q` ont un sens différent selon l'état :

| État | Recv-Q | Send-Q |
| --- | --- | --- |
| LISTEN | Connexions accept queue en attente | Backlog maximum |
| ESTABLISHED | Octets non lus par l'application | Octets non acquittés/envoyés |
| UDP | Datagrammes en file | Datagrammes en file |

Un `Recv-Q` élevé sur une socket établie signifie que l'application ne lit pas
assez vite. Un `Send-Q` élevé signifie que le réseau ou le pair ne suit pas.
Sur une socket en écoute, un `Recv-Q` proche de `Send-Q` indique une accept
queue pleine.

### netstat : encore présent, à connaître

`netstat` est déprécié mais reste utile sur d'anciens systèmes.

```bash
netstat -tunap
netstat -lntup
netstat -s
netstat -an | grep ':443'
```

Les options sont proches de `ss` : `-t` TCP, `-u` UDP, `-n` numérique, `-l`
écoute, `-p` processus, `-a` toutes. Sur les systèmes récents, préférez `ss`
pour la performance et les informations de congestion.

### tcpdump : prouver ce qui passe

```bash
# Capture TCP sur une interface, sans résolution
sudo tcpdump -ni eth0 'tcp'

# HTTP/HTTPS et ports associés
sudo tcpdump -ni eth0 -nn 'tcp port 80 or tcp port 443'

# SYN, SYN-ACK, RST
sudo tcpdump -ni eth0 'tcp[tcpflags] & (tcp-syn|tcp-ack|tcp-rst) != 0'

# Afficher les numéros de séquence absolus et les timestamps
sudo tcpdump -ni eth0 -S -tttt 'host 203.0.113.10 and tcp port 443'

# Écrire dans un fichier pour analyse
sudo tcpdump -ni eth0 -s 0 -w capture.pcap 'tcp port 443'
```

Filtres utiles :

| Filtre | Effet |
| --- | --- |
| `host 10.0.0.5` | Trafic de/vers l'hôte |
| `net 10.0.0.0/24` | Tout un préfixe |
| `port 53` | TCP et UDP port 53 |
| `tcp and port 443` | TCP uniquement |
| `udp and port 53` | UDP uniquement |
| `src host 10.0.0.5` | Source |
| `dst port 22` | Destination |
| `tcp[tcpflags] & tcp-syn != 0` | Paquets SYN |
| `greater 1000` | Paquets de plus de 1000 octets |

Une capture ne dit pas tout : si le trafic est chiffré, vous voyez les
handshakes, les tailles, les RTT et les retransmissions, pas le contenu. Pour
le contenu HTTP, utilisez les journaux applicatifs, un proxy ou une terminaison
TLS autorisée. Ne capturez jamais de données sensibles sans autorisation,
protégez les fichiers `.pcap` et limitez leur durée de conservation.

### Analyse d'une capture TCP

1. Repérez le SYN, le SYN-ACK et l'ACK. Le handshake est-il complet ?
2. Regardez les options : MSS, window scale, SACK, timestamps.
3. Suivez les numéros de séquence et les ACK. Y a-t-il des trous ?
4. Comptez les retransmissions et les ACK dupliqués.
5. Vérifiez la fenêtre annoncée : zero window ? window full ?
6. Regardez les RTT et le délai entre les paquets.
7. Terminez par FIN/ACK ou RST. Qui ferme ?
8. Comparez avec la capture de l'autre extrémité : le paquet perdu l'est-il
   avant ou après le point d'observation ?

### Outils complémentaires

```bash
nstat -az
nstat -az TcpRetransSegs TcpInErrs TcpExtListenDrops
ip -s link show eth0
ethtool -S eth0
conntrack -S
```

`nstat` expose les compteurs SNMP TCP/UDP. `ip -s link` montre les erreurs et
les drops d'interface. `ethtool -S` donne les compteurs du pilote (utile pour
les drops matériels). `conntrack -S` aide sur un pare-feu Linux stateful.

## 12. Dépannage : symptômes et causes

### Tableau de diagnostic

| Symptôme | Causes fréquentes | Vérifications |
| --- | --- | --- |
| `Connection refused` | Port fermé, service arrêté, RST | `ss -lntp`, logs du service |
| Timeout de connexion | Filtrage, route, SYN perdu, backlog | `ss -s`, capture SYN, pare-feu |
| Connexion lente | DNS, handshake, RTT, perte, TLS | `ss -ti`, capture, `dig` |
| Débit faible | Fenêtre, congestion, MTU, buffer | `ss -ti`, `nstat`, ping DF |
| Connexions bloquées | Application, `CLOSE_WAIT`, zero window | `ss -tan`, CPU, threads |
| `TIME_WAIT` massif | Fermeture active, connexions courtes | `ss -tan state time-wait`, pooling |
| `CLOSE_WAIT` massif | Application ne ferme pas | `ss -tan state close-wait`, code |
| Ports éphémères épuisés | Volume sortant, TIME_WAIT | `ss -s`, `ip_local_port_range` |
| Un seul sens | Routage asymétrique, ACL/NAT | Captures des deux côtés |
| RST après SYN | Port fermé, pare-feu, load-balancer | Capture, `ss`, logs |
| Retransmissions | Perte, RTO, congestion | `ss -ti`, `nstat`, capture |
| Duplication | Ancienne connexion, NAT, LB | Numéros de séquence, timestamps |

### Connection refused vs timeout

- **Refused** : un RST revient. La route fonctionne, mais rien n'écoute ou un
  équipement rejette explicitement. Vérifiez le service, le port, le pare-feu.
- **Timeout** : aucun RST. Le SYN est perdu, filtré ou la route retour manque.
  Vérifiez la capture des deux côtés, le routage et les règles stateful.

Un `ping` réussi ne prouve pas qu'un port TCP est ouvert : ICMP et TCP sont
filtrés séparément. Testez avec `nc -vz host port` ou `curl -v`.

### CLOSE_WAIT : le bug applicatif classique

Un processus qui reçoit un FIN mais ne ferme pas sa socket reste en
`CLOSE_WAIT`. Le pair a terminé ; le serveur doit lire les données restantes et
appeler `close()`. Causes : exception non gérée, thread bloqué, pool qui ne
rend pas la connexion, bibliothèque qui oublie de fermer, fuite de descripteurs.

```bash
ss -tan state close-wait
ss -tanp | grep CLOSE-WAIT
lsof -p <pid> | grep socket
```

Corriger le réseau ne sert à rien : il faut corriger l'application. Un redémarrage
masque temporairement le symptôme.

### TIME_WAIT : normal ou problématique ?

Beaucoup de `TIME_WAIT` sur un serveur qui ferme activement des connexions
courtes est normal. Le problème apparaît si :

- les ports éphémères s'épuisent (`Cannot assign requested address`) ;
- le volume de `TIME_WAIT` consomme trop de mémoire ;
- un load-balancer ou un client réutilise mal les connexions.

Pistes : keepalive HTTP, pooling, HTTP/2, réduire les connexions courtes,
augmenter la plage de ports, utiliser `SO_REUSEADDR` correctement. Réduire
`tcp_tw_reuse` ou `tcp_fin_timeout` sans comprendre les risques peut provoquer
des erreurs subtiles. `tcp_tw_recycle` a été retiré des noyaux récents et ne
doit pas être utilisé.

### MSS, MTU et PMTUD

Un ping de 1400 octets passe, un transfert de 1500 échoue : pensez MTU. Testez
avec DF :

```bash
ping -M do -s 1472 -c 2 203.0.113.10
tracepath 203.0.113.10
```

Sur une capture, cherchez ICMP « fragmentation needed » et les segments
retransmis de taille maximale. Un tunnel VXLAN, IPsec ou PPPoE réduit la MTU.
Ajustez la MSS (`iptables -t mangle --clamp-mss-to-pmtu`) avec précaution.

### Asymétrie et pare-feu stateful

Si l'aller passe par un pare-feu A et le retour par B, B peut voir un paquet
qui ne correspond à aucune session et le rejeter. Vérifiez les tables de
routage, les routes par défaut, les métriques, le NAT et les sessions des
équipements. Une capture des deux côtés montre où le retour diverge.

### UDP et DNS

Un échec DNS peut ressembler à un problème TCP. Testez :

```bash
dig example.com
dig +tcp example.com
tcpdump -ni eth0 'udp port 53'
```

Une réponse tronquée (`TC=1`) force le client à réessayer en TCP. Si TCP 53 est
filtré, la résolution échoue malgré un UDP qui fonctionne. Vérifiez aussi les
options EDNS, la taille des réponses et les pare-feu.

## 13. Sécurité du transport

### SYN flood

Un attaquant envoie des SYN avec des sources usurpées ; le serveur alloue des
états `SYN_RECEIVED` et épuise la file. Parades : SYN cookies, rate limiting,
pare-feu, protection DDoS, backlog dimensionné. Les SYN cookies évitent de
stocker l'état initial, mais peuvent perdre certaines options TCP.

### Injection et détournement

TCP n'authentifie pas les segments par cryptographic. Un attaquant sur le
chemin peut injecter un RST ou, avec des numéros de séquence devinés, injecter
des données. TLS protège l'intégrité applicative, mais pas la disponibilité
face à un RST. La randomisation des ISN, les timestamps et le chiffrement
réduisent les risques. Ne considérez jamais un réseau non chiffré comme sûr.

### Scan de ports et fingerprinting

Un SYN scan envoie des SYN et observe SYN-ACK/RST. Un scan connecté établit
une vraie connexion. Les pare-feu et l'IDS détectent les motifs, mais un scan
lent peut passer. Pour l'administration, limitez l'exposition, utilisez un
bastion, l'authentification forte et la journalisation.

### UDP amplification

Les services UDP sans contrôle de source (DNS ouvert, NTP monlist, memcached)
peuvent amplifier une attaque. Désactivez les fonctions inutiles, limitez les
réponses, filtrez l'usurpation et surveillez les volumes anormaux.

## 14. Cas pratique : serveur web lent et CLOSE_WAIT

### Symptôme

Un serveur web derrière un load-balancer répond lentement. Les utilisateurs
signalent des timeouts. Le réseau n'affiche pas de perte. `ss -s` montre un
grand nombre de `CLOSE_WAIT`, et le nombre de descripteurs du processus
augmente jusqu'à la limite.

### Analyse

1. `ss -tan state close-wait` confirme des milliers de sockets.
2. `lsof -p <pid> | wc -l` approche `ulimit -n`.
3. Les journaux applicatifs montrent des exceptions lors de la lecture d'une
   réponse amont.
4. Le code ouvre une connexion vers un service amont et ne la ferme pas dans
   le chemin d'erreur.
5. La accept queue se remplit, les nouveaux clients attendent, le load-balancer
   marque le backend unhealthy.

### Correction

- Fermer les sockets dans un `finally` ou un gestionnaire de contexte.
- Ajouter un timeout applicatif et un circuit breaker.
- Limiter la taille du pool de connexions.
- Surveiller `CLOSE_WAIT`, les descripteurs et la accept queue.
- Redémarrer pour libérer les sockets après correction, puis vérifier la
  stabilité sur plusieurs cycles.

### Preuves à conserver

```text
ss -s
ss -tan state close-wait | head
lsof -p <pid> | wc -l
ss -lnt
nstat -az TcpExtListenDrops
```

## 15. Exercices avec corrigé

### Exercice 1 — Handshake

Un client envoie `SYN seq=1000`. Le serveur répond `SYN+ACK seq=5000 ack=1001`.
Quel ACK le client envoie-t-il ?

**Corrigé :** `ACK ack=5001` (le prochain octet attendu du serveur). Le numéro
de séquence du client pour ses données sera 1001, sauf s'il utilise une option
qui modifie le compte.

### Exercice 2 — Fermeture

Pourquoi la fermeture TCP nécessite-t-elle quatre segments alors que le
handshake en utilise trois ?

**Corrigé :** chaque direction se ferme indépendamment. Le FIN d'un côté et le
FIN de l'autre sont deux messages distincts, chacun acquitté. Le ACK du premier
FIN et le FIN du côté passif peuvent être combinés dans certains cas, mais le
modèle général est quatre étapes.

### Exercice 3 — État

Un serveur affiche beaucoup de sockets en `CLOSE_WAIT`. Que faut-il regarder
en premier ?

**Corrigé :** l'application. Elle a reçu le FIN mais n'a pas fermé sa socket.
Vérifiez le code de fermeture, les exceptions, les threads bloqués et les
descripteurs. Le réseau n'est probablement pas la cause.

### Exercice 4 — TIME_WAIT

Un client ouvre 50 000 connexions courtes par minute vers le même serveur et
voit `Cannot assign requested address`. Pourquoi ?

**Corrigé :** les ports éphémères sont épuisés, notamment à cause des
`TIME_WAIT` sur le côté qui ferme. Le quadruplet doit être unique. Solutions :
pooling/keepalive, HTTP/2, réduire les connexions, augmenter la plage de
ports, vérifier qui ferme activement. Ne réduisez pas aveuglément les délais.

### Exercice 5 — Fenêtre

Une capture montre `win 64` avec un window scale de 7. Quelle est la fenêtre
effective ?

**Corrigé :** `64 × 2^7 = 8192` octets. Sans le scale, on croirait à 64 octets.

### Exercice 6 — Congestion

Pourquoi `cwnd` double-t-elle au début puis augmente-t-elle beaucoup plus
lentement ?

**Corrigé :** slow start double `cwnd` à chaque RTT jusqu'à `ssthresh`, puis
congestion avoidance augmente d'environ 1 MSS par RTT. C'est l'AIMD.

### Exercice 7 — Ports

Pourquoi HTTP/3 peut-il échouer alors que TCP 443 est autorisé ?

**Corrigé :** HTTP/3 utilise QUIC sur UDP 443. Un pare-feu qui n'autorise que
TCP 443 bloque le trafic. Vérifiez les règles UDP et le fallback HTTP/2.

### Exercice 8 — MTU

Un ping de 1472 octets de données passe, mais une session TLS de plusieurs
mégaoctets se bloque. Quelle est la piste ?

**Corrigé :** PMTUD/MTU. Le ping 1472 + 8 ICMP + 20 IP = 1500. Un tunnel ou
un équipement intermédiaire peut avoir une MTU plus faible et bloquer ICMP.
Capturez les messages ICMP et testez avec des tailles décroissantes.

### Exercice 9 — UDP

Pourquoi une application VoIP utilise-t-elle UDP plutôt que TCP ?

**Corrigé :** la voix tolère mieux une petite perte qu'une retransmission
tardive. TCP imposerait un ordre et des retransmissions qui augmentent la
latence et la gigue. La VoIP utilise RTP/UDP avec des mécanismes applicatifs.

### Exercice 10 — Diagnostic

Un client reçoit `Connection refused`. Le ping vers le serveur fonctionne.
Que concluez-vous ?

**Corrigé :** la route IP fonctionne, mais le port TCP n'écoute pas ou un
équipement renvoie un RST. Vérifiez le service, `ss -lntp`, le pare-feu et le
load-balancer. Le ping ne teste pas le port.

## 16. Aide-mémoire

### Commandes essentielles

| Besoin | Commande |
| --- | --- |
| Toutes les sockets | `ss -tunap` |
| Écoute | `ss -lntup` |
| Connexions établies | `ss -tan state established` |
| Détails congestion | `ss -ti` |
| Résumé | `ss -s` |
| Ancien outil | `netstat -tunap` |
| Capture TCP | `tcpdump -ni eth0 'tcp'` |
| Capture SYN/RST | `tcpdump -ni eth0 'tcp[tcpflags] & (tcp-syn\|tcp-rst) != 0'` |
| Compteurs TCP | `nstat -az` |
| Buffers | `sysctl net.ipv4.tcp_rmem net.ipv4.tcp_wmem` |
| Congestion | `sysctl net.ipv4.tcp_congestion_control` |
| Ports éphémères | `sysctl net.ipv4.ip_local_port_range` |
| Test port | `nc -vz host 443` |
| Test HTTP | `curl -v https://host/` |
| Test DNS | `dig +tcp example.com` |

### Règles à retenir

- TCP est un flux d'octets, pas une suite de messages.
- Le handshake synchronise les ISN et les options ; la fermeture a deux sens.
- `TIME_WAIT` est normal sur le côté qui ferme activement.
- `CLOSE_WAIT` est presque toujours un bug applicatif.
- La fenêtre protège le récepteur ; `cwnd` protège le réseau.
- Slow start double la fenêtre, congestion avoidance augmente lentement.
- Un port ouvert ne prouve pas un service fonctionnel.
- Un ping réussi ne prouve pas qu'un port TCP est ouvert.
- Capturez des deux côtés avant de conclure à une perte réseau.
- Un RST peut être une réponse légitime ou un symptôme de state perdu.
- Ne désactivez pas Nagle, les timestamps ou les SYN cookies sans mesure.
- UDP n'est pas « sans contrôle » : l'application doit gérer perte, ordre et
  congestion si elle en a besoin.

### Glossaire

| Terme | Définition |
| --- | --- |
| MSS | Taille maximale de données TCP dans un segment |
| MTU | Taille maximale d'une unité IP sur un lien |
| ISN | Numéro de séquence initial |
| ACK | Accusé de réception cumulatif |
| SACK | Selective Acknowledgment |
| RTT | Round-Trip Time |
| RTO | Retransmission Timeout |
| cwnd | Fenêtre de congestion |
| rwnd | Fenêtre de réception annoncée |
| BDP | Bande passante × RTT |
| ECN | Explicit Congestion Notification |
| PMTUD | Path MTU Discovery |
| TIME_WAIT | Attente 2*MSL après fermeture active |
| CLOSE_WAIT | FIN reçu, application pas encore fermée |
| SYN flood | Attaque par accumulation de connexions semi-ouvertes |
| QUIC | Transport fiable sur UDP, utilisé par HTTP/3 |

## Conclusion opérationnelle

TCP et UDP ne se résument pas à « fiable » contre « rapide ». Le diagnostic
consiste à relier un symptôme applicatif à un état de socket, un compteur, une
fenêtre ou un paquet. Une connexion lente peut être un RTT élevé, une fenêtre
trop petite, une perte, un bufferbloat ou une application qui ne lit pas. Une
connexion refusée peut être un service arrêté ou un RST de pare-feu. Un
`CLOSE_WAIT` massif est un bug de code, pas une panne de câble. Les commandes
`ss`, `nstat` et `tcpdump` fournissent les preuves ; le modèle de la machine à
états et les mécanismes de fenêtre/congestion fournissent l'explication.
